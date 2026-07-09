"""Run all provider spiders sequentially and report status per provider.

Exit code is non-zero if any spider produced zero items, so cron / CI can
distinguish silent failures from successful runs.
"""
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from pricing.spiders.openai_spider import OpenAISpider
from pricing.spiders.anthropic_spider import AnthropicSpider
from pricing.spiders.google_spider import GoogleSpider


def main() -> int:
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(OpenAISpider)
    process.crawl(AnthropicSpider)
    process.crawl(GoogleSpider)
    process.start()

    stats = process.bootstrap_failed
    if stats:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
