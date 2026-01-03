"""
OpenAI Pricing Scraper Agent
Scrapes pricing data from OpenAI website and stores in ChromaDB.
"""
import sys
from pathlib import Path
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pricing_knowledge_base import PricingKnowledgeBase
from utils.data_normalizer import normalize_pricing_data


class OpenAIPricingScraper:
    """
    Scrapes OpenAI pricing information and stores in the knowledge base.
    Includes hardcoded seed data as fallback.
    """

    def __init__(self, kb: Optional[PricingKnowledgeBase] = None):
        """
        Initialize the scraper.

        Args:
            kb: Optional PricingKnowledgeBase instance (will create one if not provided)
        """
        self.kb = kb or PricingKnowledgeBase()
        self.base_url = "https://openai.com/api/pricing"
        self.user_agent = "Mozilla/5.0 (compatible; GenAIFinOps/0.1)"
        self.delay = 2

    def get_seed_data(self) -> List[Dict[str, Any]]:
        """
        Returns hardcoded seed data for immediate use.
        This data is current as of January 2026 and serves as fallback.

        Returns:
            List[Dict]: List of pricing data dictionaries
        """
        seed_data = [
            {
                "provider": "OpenAI",
                "model_name": "gpt-4o",
                "model_display_name": "GPT-4o",
                "input_cost_per_1m_tokens": 2.50,
                "output_cost_per_1m_tokens": 10.0,
                "context_window": 128000,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "max_output_tokens": 16384,
                "training_data_cutoff": "2023-10",
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Most capable GPT-4 model, multimodal input support"
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-4o-mini",
                "model_display_name": "GPT-4o mini",
                "input_cost_per_1m_tokens": 0.15,
                "output_cost_per_1m_tokens": 0.60,
                "context_window": 128000,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "max_output_tokens": 16384,
                "training_data_cutoff": "2023-10",
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Affordable and intelligent small model for fast, lightweight tasks"
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-4-turbo",
                "model_display_name": "GPT-4 Turbo",
                "input_cost_per_1m_tokens": 10.0,
                "output_cost_per_1m_tokens": 30.0,
                "context_window": 128000,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "max_output_tokens": 4096,
                "training_data_cutoff": "2023-12",
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Previous generation high-intelligence model"
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-4",
                "model_display_name": "GPT-4",
                "input_cost_per_1m_tokens": 30.0,
                "output_cost_per_1m_tokens": 60.0,
                "context_window": 8192,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "max_output_tokens": 8192,
                "training_data_cutoff": "2023-09",
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Original GPT-4 model"
            },
            {
                "provider": "OpenAI",
                "model_name": "gpt-3.5-turbo",
                "model_display_name": "GPT-3.5 Turbo",
                "input_cost_per_1m_tokens": 0.50,
                "output_cost_per_1m_tokens": 1.50,
                "context_window": 16385,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "max_output_tokens": 4096,
                "training_data_cutoff": "2021-09",
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Fast and affordable model for simple tasks"
            },
            {
                "provider": "OpenAI",
                "model_name": "text-embedding-3-small",
                "model_display_name": "Text Embedding 3 Small",
                "input_cost_per_1m_tokens": 0.02,
                "output_cost_per_1m_tokens": 0.0,
                "context_window": 8191,
                "supports_function_calling": False,
                "supports_json_mode": False,
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Most efficient embedding model"
            },
            {
                "provider": "OpenAI",
                "model_name": "text-embedding-3-large",
                "model_display_name": "Text Embedding 3 Large",
                "input_cost_per_1m_tokens": 0.13,
                "output_cost_per_1m_tokens": 0.0,
                "context_window": 8191,
                "supports_function_calling": False,
                "supports_json_mode": False,
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "High-performance embedding model"
            },
            {
                "provider": "OpenAI",
                "model_name": "dall-e-3",
                "model_display_name": "DALL-E 3",
                "input_cost_per_1m_tokens": 0.0,
                "output_cost_per_1m_tokens": 0.0,
                "supports_function_calling": False,
                "supports_json_mode": False,
                "supports_vision": False,
                "pricing_url": "https://openai.com/api/pricing",
                "notes": "Image generation model. Pricing: $0.040-$0.120 per image depending on quality/size"
            }
        ]

        for item in seed_data:
            item["last_updated"] = datetime.utcnow().isoformat()

        return seed_data

    def scrape_openai_pricing(self) -> List[Dict[str, Any]]:
        """
        Attempts to scrape live pricing data from OpenAI website.
        Falls back to seed data if scraping fails.

        Returns:
            List[Dict]: Scraped or seed pricing data
        """
        print(f"Attempting to scrape OpenAI pricing from: {self.base_url}")

        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            response = requests.get(self.base_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            print(f"✓ Successfully fetched OpenAI pricing page (Status: {response.status_code})")
            print("⚠️  Note: HTML parsing for live data not yet implemented.")
            print("   Using seed data instead. Live scraping will be added in future versions.")

            time.sleep(self.delay)

            return self.get_seed_data()

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to scrape OpenAI pricing: {str(e)}")
            print("   Falling back to hardcoded seed data...")
            return self.get_seed_data()

        except Exception as e:
            print(f"⚠️  Unexpected error during scraping: {str(e)}")
            print("   Falling back to hardcoded seed data...")
            return self.get_seed_data()

    def ingest_to_kb(self, data: List[Dict[str, Any]]) -> int:
        """
        Ingests pricing data into the knowledge base.

        Args:
            data: List of pricing data dictionaries

        Returns:
            int: Number of entries successfully added
        """
        print(f"\nIngesting {len(data)} pricing entries into ChromaDB...")

        try:
            count = self.kb.add_prices(data)
            print(f"✓ Successfully ingested {count} entries")
            return count

        except Exception as e:
            print(f"✗ Error ingesting data: {str(e)}")
            return 0

    def run(self) -> int:
        """
        Main execution method: scrape and ingest.

        Returns:
            int: Number of entries successfully added
        """
        print("="*60)
        print("OpenAI Pricing Scraper Agent")
        print("="*60)
        print()

        data = self.scrape_openai_pricing()

        if not data:
            print("✗ No data to ingest.")
            return 0

        count = self.ingest_to_kb(data)

        print()
        print("="*60)
        print(f"Scraping complete! {count} entries added to knowledge base.")
        print("="*60)

        return count

    def save_to_file(self, data: List[Dict[str, Any]], filename: str = "openai_pricing.json"):
        """
        Save scraped data to a JSON file for inspection.

        Args:
            data: Pricing data to save
            filename: Output filename
        """
        output_dir = Path(__file__).parent.parent / "data" / "scraped_pricing"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Saved scraped data to: {output_path}")


class MultiProviderScraper:
    """
    Future: Orchestrates scraping across multiple providers.
    Currently supports OpenAI only.
    """

    def __init__(self, kb: Optional[PricingKnowledgeBase] = None):
        self.kb = kb or PricingKnowledgeBase()
        self.scrapers = {
            "openai": OpenAIPricingScraper(self.kb)
        }

    def scrape_all(self) -> Dict[str, int]:
        """
        Scrapes all configured providers.

        Returns:
            Dict: Provider name -> count of entries added
        """
        results = {}

        for provider_name, scraper in self.scrapers.items():
            print(f"\n{'='*60}")
            print(f"Scraping {provider_name.upper()}...")
            print(f"{'='*60}\n")

            try:
                count = scraper.run()
                results[provider_name] = count
            except Exception as e:
                print(f"✗ Error scraping {provider_name}: {str(e)}")
                results[provider_name] = 0

        return results

    def add_scraper(self, name: str, scraper):
        """Add a new scraper for another provider."""
        self.scrapers[name] = scraper


if __name__ == "__main__":
    print("\n🤖 Running OpenAI Pricing Scraper...\n")

    kb = PricingKnowledgeBase()

    scraper = OpenAIPricingScraper(kb)

    count = scraper.run()

    print("\n📊 Knowledge Base Stats:")
    stats = kb.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n✅ Scraper test complete!")
