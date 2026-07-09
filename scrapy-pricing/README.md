# scrapy-pricing

Daily pricing pipeline that feeds the GenAIFinOps backend with normalized AI model prices for OpenAI, Anthropic, and Google.

## Design

- **Primary source**: [`litellm/model_prices_and_context_window.json`](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json) — a well-maintained public JSON with per-token prices, context windows, and capability flags. Each provider spider filters this by its provider slug or key prefix.
- **Cross-check**: The same litellm JSON is loaded again by `LiteLLMCrossCheckPipeline`. If a spider ever adds provider-page HTML scraping in `parse()`, any divergence > 20% (configurable) is logged and attached to the spider as `divergence_warnings`.
- **Ingestion**: `IngestPipeline` accumulates items per provider and POSTs one batch per provider to `POST /pricing/ingest` on the backend. Ingestion is skipped for providers under `MIN_MODELS_PER_PROVIDER` (default 3) — silent partial data never reaches the DB.
- **Auditability**: The backend writes one `ScrapeRun` row per provider batch with `status`, `items_found`, `items_changed`, and `error_log`.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set `INGEST_TOKEN` in `.env` to match `PRICING_INGEST_TOKEN` in `backend/.env`.

## Run one spider

```powershell
scrapy crawl openai
scrapy crawl anthropic
scrapy crawl google
```

## Run all three

```powershell
python run_all.py
```

## Tests

```powershell
pytest tests/
```

## Docker (daily cron)

```powershell
docker build -f Dockerfile.scrapy -t genai-finops-scrapy .
docker run --env-file .env genai-finops-scrapy
```

The container runs cron with `0 6 * * *` (06:00 UTC daily).

## Adding real HTML scraping later

Each spider inherits from `BaseLiteLLMSpider`. To add real scraping of a provider's pricing page, override `start_requests()` and `parse()`, emit the same `ModelPricingItem` shape, and set `source` to the URL. The `LiteLLMCrossCheckPipeline` will flag any divergence and the backend will mark the run as `partial` — never a silent fallback.
