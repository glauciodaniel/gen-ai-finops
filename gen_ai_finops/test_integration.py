#!/usr/bin/env python3
"""
Integration Test for GenAIFinOps
Tests the complete RAG pipeline: Scraper -> ChromaDB -> Oracle
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("GenAIFinOps - Integration Test")
print("="*60)
print()

print("Step 1: Testing imports...")
try:
    from utils.pricing_knowledge_base import PricingKnowledgeBase
    from agents.scraper import OpenAIPricingScraper
    from agents.oracle import PricingOracle
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {str(e)}")
    sys.exit(1)

print("\nStep 2: Initializing PricingKnowledgeBase...")
try:
    kb = PricingKnowledgeBase()
    print(f"✓ ChromaDB initialized")
    print(f"  Current entries: {kb.collection.count()}")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    sys.exit(1)

print("\nStep 3: Running scraper with seed data...")
try:
    scraper = OpenAIPricingScraper(kb)

    seed_data = scraper.get_seed_data()
    print(f"  Seed data contains {len(seed_data)} entries")

    count = scraper.ingest_to_kb(seed_data)
    print(f"✓ Scraped and ingested {count} entries")
except Exception as e:
    print(f"✗ Scraper error: {str(e)}")
    sys.exit(1)

print("\nStep 4: Testing ChromaDB queries...")
try:
    results = kb.query_prices("cheapest model", n_results=3)
    print(f"✓ Query returned {len(results)} results")

    if results:
        print(f"  Top result: {results[0]['metadata']['model_name']}")
except Exception as e:
    print(f"✗ Query error: {str(e)}")
    sys.exit(1)

print("\nStep 5: Testing Oracle (RAG + LLM)...")
try:
    oracle = PricingOracle(kb)
    status = oracle.get_status()

    print(f"  LLM available: {status['llm_available']}")
    print(f"  API key configured: {status['api_key_configured']}")
    print(f"  Model: {status['model']}")
    print(f"  KB entries: {status['knowledge_base']['total_models']}")

    test_question = "What is the cheapest GPT model?"
    print(f"\n  Testing question: '{test_question}'")

    answer = oracle.ask(test_question)
    print(f"\n  Oracle response preview:")
    print(f"  {answer[:200]}...")

    print("\n✓ Oracle integration working")

except Exception as e:
    print(f"✗ Oracle error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 6: Getting knowledge base stats...")
try:
    stats = kb.get_stats()
    print(f"✓ Stats retrieved:")
    print(f"  Total models: {stats['total_models']}")
    print(f"  Providers: {', '.join(stats['providers'])}")
except Exception as e:
    print(f"✗ Stats error: {str(e)}")

print("\n" + "="*60)
print("✅ Integration Test PASSED")
print("="*60)
print("\nSystem is ready! Try:")
print("  python main.py scrape")
print("  python main.py ask 'What is the cheapest model?'")
print("  python main.py  (interactive mode)")
