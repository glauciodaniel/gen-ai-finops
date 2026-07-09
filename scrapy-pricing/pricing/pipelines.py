import logging
from typing import Any

import requests
from scrapy.exceptions import DropItem


class ValidationPipeline:
    REQUIRED = ("provider", "slug", "displayName", "inputPer1M", "outputPer1M")

    def process_item(self, item: dict[str, Any], spider) -> dict[str, Any]:
        for field in self.REQUIRED:
            if field not in item or item[field] in (None, ""):
                raise DropItem(f"Missing required field {field}: {item}")

        for field in ("inputPer1M", "outputPer1M"):
            try:
                value = float(item[field])
            except (TypeError, ValueError) as e:
                raise DropItem(f"Invalid {field}={item[field]}: {e}")
            if value < 0:
                raise DropItem(f"Negative price {field}={value} for {item['slug']}")

        return item


class LiteLLMCrossCheckPipeline:
    def __init__(self, litellm_url: str, threshold: float):
        self.litellm_url = litellm_url
        self.threshold = threshold
        self.reference: dict[str, dict[str, Any]] = {}
        self.divergences: list[str] = []
        self.log = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            litellm_url=crawler.settings.get("LITELLM_URL"),
            threshold=crawler.settings.getfloat("PRICE_DIVERGENCE_THRESHOLD", 0.2),
        )

    def open_spider(self, spider):
        try:
            resp = requests.get(self.litellm_url, timeout=30)
            resp.raise_for_status()
            self.reference = resp.json()
            self.log.info(
                "Loaded %d models from litellm reference",
                len(self.reference),
            )
        except Exception as e:
            self.log.warning("Could not load litellm reference: %s", e)
            self.reference = {}

    def process_item(self, item: dict[str, Any], spider) -> dict[str, Any]:
        if not self.reference:
            return item
        ref = self._match(item["slug"])
        if not ref:
            return item

        for field, ref_key in (
            ("inputPer1M", "input_cost_per_token"),
            ("outputPer1M", "output_cost_per_token"),
        ):
            ref_val = ref.get(ref_key)
            if ref_val is None:
                continue
            ref_per_1m = float(ref_val) * 1_000_000
            scraped = float(item[field])
            if ref_per_1m == 0:
                continue
            divergence = abs(scraped - ref_per_1m) / ref_per_1m
            if divergence > self.threshold:
                msg = (
                    f"{item['slug']}.{field}: scraped={scraped:.4f} "
                    f"litellm={ref_per_1m:.4f} divergence={divergence:.2%}"
                )
                self.divergences.append(msg)
                self.log.warning("Price divergence: %s", msg)
        return item

    def close_spider(self, spider):
        if self.divergences:
            spider.divergence_warnings = list(self.divergences)

    def _match(self, slug: str) -> dict[str, Any] | None:
        if slug in self.reference:
            return self.reference[slug]
        for key, value in self.reference.items():
            if key.endswith(f"/{slug}") or key == slug:
                return value
        return None


class IngestPipeline:
    def __init__(self, ingest_url: str, token: str, min_models: int):
        self.ingest_url = ingest_url
        self.token = token
        self.min_models = min_models
        self.batches: dict[str, list[dict[str, Any]]] = {}
        self.source_by_provider: dict[str, str] = {}
        self.log = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            ingest_url=crawler.settings.get("INGEST_URL"),
            token=crawler.settings.get("INGEST_TOKEN"),
            min_models=crawler.settings.getint("MIN_MODELS_PER_PROVIDER", 3),
        )

    def process_item(self, item: dict[str, Any], spider) -> dict[str, Any]:
        provider = item["provider"]
        self.batches.setdefault(provider, []).append(self._to_payload(item))
        source = item.get("source")
        if source:
            self.source_by_provider[provider] = source
        return item

    def close_spider(self, spider):
        if not self.token:
            self.log.error("INGEST_TOKEN not set; skipping submission")
            return
        for provider, models in self.batches.items():
            if len(models) < self.min_models:
                self.log.error(
                    "Not enough models for %s (%d < %d); skipping submission",
                    provider,
                    len(models),
                    self.min_models,
                )
                continue
            payload = {
                "provider": provider,
                "source": self.source_by_provider.get(provider, "scrapy"),
                "models": models,
            }
            try:
                resp = requests.post(
                    self.ingest_url,
                    headers={"Authorization": f"Bearer {self.token}"},
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                self.log.info(
                    "Ingested %d models for %s: %s",
                    len(models),
                    provider,
                    resp.json(),
                )
            except requests.HTTPError as e:
                self.log.error(
                    "Ingest failed for %s: %s %s",
                    provider,
                    e,
                    getattr(e.response, "text", ""),
                )
            except requests.RequestException as e:
                self.log.error("Ingest request failed for %s: %s", provider, e)

    @staticmethod
    def _to_payload(item: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "slug": item["slug"],
            "displayName": item["displayName"],
            "inputPer1M": float(item["inputPer1M"]),
            "outputPer1M": float(item["outputPer1M"]),
        }
        for optional in (
            "modality",
            "contextWindow",
            "maxOutput",
            "supportsTools",
            "supportsVision",
            "supportsJson",
            "deprecated",
            "cachedInputPer1M",
            "currency",
        ):
            if optional in item and item[optional] is not None:
                value = item[optional]
                if optional == "cachedInputPer1M":
                    value = float(value)
                payload[optional] = value
        return payload
