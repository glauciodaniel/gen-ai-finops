import json
import logging
from typing import Any, Iterable

import scrapy

from pricing.items import ModelPricingItem


class BaseLiteLLMSpider(scrapy.Spider):
    """Base spider that reads pricing from the litellm JSON reference and
    filters by provider. Subclasses declare provider_slug and match_keys
    (litellm keys that identify their models).

    HTML scraping of provider pricing pages can be layered on top in
    subclasses by overriding parse() — the litellm data acts as the
    baseline so the pipeline never silently ingests stale data.
    """

    provider_slug: str = ""
    match_prefixes: tuple[str, ...] = ()
    default_modality = "text"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_ = logging.getLogger(self.__class__.__name__)

    def start_requests(self) -> Iterable[scrapy.Request]:
        url = self.settings.get("LITELLM_URL")
        yield scrapy.Request(url, callback=self.parse_litellm, dont_filter=True)

    def parse_litellm(self, response):
        try:
            data: dict[str, Any] = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.log_.error("Could not parse litellm JSON: %s", e)
            return

        yielded = 0
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            if not self._matches(key, entry):
                continue
            item = self._to_item(key, entry)
            if item is None:
                continue
            yielded += 1
            yield item

        self.log_.info(
            "Emitted %d %s models from litellm", yielded, self.provider_slug
        )

    def _matches(self, key: str, entry: dict[str, Any]) -> bool:
        provider_field = str(entry.get("litellm_provider", "")).lower()
        if provider_field == self.provider_slug:
            return True
        for prefix in self.match_prefixes:
            if key.startswith(prefix):
                return True
        return False

    def _to_item(self, key: str, entry: dict[str, Any]) -> ModelPricingItem | None:
        input_cost = entry.get("input_cost_per_token")
        output_cost = entry.get("output_cost_per_token")
        if input_cost is None or output_cost is None:
            return None

        slug = self._normalize_slug(key)
        mode = str(entry.get("mode", self.default_modality)).lower()
        modality = self._map_modality(mode)

        item = ModelPricingItem()
        item["provider"] = self.provider_slug
        item["slug"] = slug
        item["displayName"] = self._display_name(slug)
        item["modality"] = modality
        item["contextWindow"] = entry.get("max_input_tokens") or entry.get(
            "max_tokens"
        )
        item["maxOutput"] = entry.get("max_output_tokens")
        item["supportsTools"] = bool(entry.get("supports_function_calling"))
        item["supportsVision"] = bool(entry.get("supports_vision"))
        item["supportsJson"] = bool(entry.get("supports_response_schema"))
        item["deprecated"] = bool(entry.get("deprecation_date"))
        item["inputPer1M"] = round(float(input_cost) * 1_000_000, 6)
        item["outputPer1M"] = round(float(output_cost) * 1_000_000, 6)
        cached = entry.get("cache_read_input_token_cost")
        if cached is not None:
            item["cachedInputPer1M"] = round(float(cached) * 1_000_000, 6)
        item["currency"] = "USD"
        item["source"] = "litellm"
        return item

    def _normalize_slug(self, key: str) -> str:
        if "/" in key:
            return key.split("/", 1)[1]
        return key

    def _display_name(self, slug: str) -> str:
        return slug.replace("-", " ").replace("_", " ").title()

    @staticmethod
    def _map_modality(mode: str) -> str:
        if mode in ("chat", "completion", "responses"):
            return "text"
        if mode == "embedding":
            return "embedding"
        if mode in ("image_generation", "image"):
            return "image"
        if mode in ("audio_transcription", "audio_speech", "audio"):
            return "audio"
        return "text"
