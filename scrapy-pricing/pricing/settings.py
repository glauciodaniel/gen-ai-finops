import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "pricing"

SPIDER_MODULES = ["pricing.spiders"]
NEWSPIDER_MODULE = "pricing.spiders"

USER_AGENT = "gen-ai-finops-scraper/0.1 (+https://github.com/glauciodaniel/gen-ai-finops)"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1.0

RETRY_ENABLED = True
RETRY_TIMES = 3

ITEM_PIPELINES = {
    "pricing.pipelines.ValidationPipeline": 100,
    "pricing.pipelines.LiteLLMCrossCheckPipeline": 200,
    "pricing.pipelines.IngestPipeline": 900,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

LOG_LEVEL = os.getenv("SCRAPY_LOG_LEVEL", "INFO")

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:3000/pricing/ingest")
INGEST_TOKEN = os.getenv("INGEST_TOKEN", "")
LITELLM_URL = os.getenv(
    "LITELLM_URL",
    "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
)
PRICE_DIVERGENCE_THRESHOLD = float(os.getenv("PRICE_DIVERGENCE_THRESHOLD", "0.2"))
MIN_MODELS_PER_PROVIDER = int(os.getenv("MIN_MODELS_PER_PROVIDER", "3"))
