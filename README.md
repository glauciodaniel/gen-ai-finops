# GenAIFinOps

AI model pricing intelligence and cost optimization built on the [HedHog](https://hedhog.com) framework (NestJS + Prisma + Vite/React).

## What works today

- **Real pricing data**: daily-refreshed prices for OpenAI, Anthropic, and Google models — 250+ entries pulled from the [litellm](https://github.com/BerriAI/litellm) public JSON. See `scrapy-pricing/README.md` for how spiders can be extended to also scrape provider pricing pages directly.
- **Versioned price history**: every price change is a new row in `model_price` with `effective_from`. This enables the "did gpt-4o get cheaper this month?" query that most tools can't answer.
- **Auditable ingestion**: every batch received from the pipeline produces one `scrape_run` row with status (`success` / `partial` / `failed`), items found, items changed, and any error log — visible in the admin UI at `/pricing/scrape-runs`.
- **Cost optimizer**: `POST /optimizer/analyze` takes a free-text use case + expected volume and returns ranked model recommendations with monthly cost. Optional `currentModelSlug` yields a savings projection. LLM-based requirements extraction (structured JSON output) with a deterministic keyword-heuristic fallback.
- **Admin UI**: pricing overview, paginated model catalog, price history charts, scrape run audit log, and optimizer form.

## What is NOT done yet (roadmap)

- **Oracle** — natural-language pricing chat backed by Prisma tool use + MCP server exposure (Phase 4, planned).
- **Authentication on read endpoints** — pricing information is public data (all provider prices are public knowledge), so the read endpoints are intentionally unauthenticated in this build. The write endpoint (`POST /pricing/ingest`) is guarded by a service token (`PRICING_INGEST_TOKEN`). If you deploy this in a context where you want to gate reads, plug in HedHog's Auth module and add a JWT guard to `PricingController`.
- **Provider-page HTML scraping** — the pipeline currently uses litellm as the source of truth. Real HTML scraping is a valid enhancement path (each spider inherits from `BaseLiteLLMSpider` and can override `parse()` — see `scrapy-pricing/README.md`), but it was not the priority for MVP given how frequently these pages change layout.
- **Alerting on price changes** — the data model supports it (any change lands as a new `model_price` row); wiring up email/notification is a follow-up.

## Running it locally

Requires Docker Desktop, Node 20+, and Python 3.12+.

```powershell
# 1. Postgres
docker compose up -d postgres

# 2. Backend
cd backend
npm install
npm run migrate:up   # runs TypeORM migration, then prisma db pull + generate
npm run start:dev    # NestJS on port 3000

# 3. Populate with real pricing data (in another shell)
cd scrapy-pricing
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # then set INGEST_TOKEN to match backend/.env
python -m scrapy crawl openai
python -m scrapy crawl anthropic
python -m scrapy crawl google

# 4. Admin (in another shell)
cd admin
npm install --legacy-peer-deps
npm run dev          # Vite on port 5173
```

Now visit `http://localhost:5173/pricing` for the pricing catalog or `http://localhost:5173/optimizer` for the cost analyzer.

## Testing

- **Backend**: `cd backend && npm test` (Jest, 25 unit tests covering cost math, ranking, and requirements extraction).
- **Scrapy**: `cd scrapy-pricing && pytest tests/` (14 tests for the base spider and validation/cross-check pipelines).
- **Admin**: `cd admin && npx tsc --noEmit` (strict typecheck).
- **CI**: `.github/workflows/ci.yml` runs all of the above on every push and PR, plus a live-Postgres integration smoke that runs the actual TypeORM migration and Prisma introspection.

## Repository layout

```
backend/          NestJS API (pricing + optimizer)
  src/pricing/    /pricing/{providers,models,history,scrape-runs,compare,stats,ingest}
  src/optimizer/  /optimizer/analyze — cost calc + ranker + requirements extractor
  src/typeorm/    migration files (TypeORM manages DDL, Prisma introspects for the client)
admin/            Vite + React admin panel (HedHog scaffold + pricing/optimizer pages)
scrapy-pricing/   Python Scrapy project — daily pipeline into POST /pricing/ingest
```

## History

This repository was rewritten in July 2026 from an earlier Python/FastAPI + Bolt-generated React prototype. The original code — which had a broken rate limiter causing all rate-limited endpoints to return HTTP 500, hardcoded prices from 2024, and a scraper that discarded its HTTP response and returned seed data — is preserved on the `legacy` branch.
