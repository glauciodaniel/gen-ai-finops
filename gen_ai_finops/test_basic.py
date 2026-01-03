#!/usr/bin/env python3
"""
Basic test script to verify GenAIFinOps setup
Run this to test if everything is working correctly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("GenAIFinOps - Basic System Test")
print("="*60)

print("\n1. Testing data_normalizer module...")
try:
    from utils.data_normalizer import (
        validate_pricing_data,
        normalize_pricing_data,
        pricing_to_text
    )
    print("   ✓ data_normalizer imported successfully")

    test_data = {
        "provider": "OpenAI",
        "model_name": "gpt-4-test",
        "input_cost_per_1m_tokens": 30.0,
        "output_cost_per_1m_tokens": 60.0,
        "context_window": 8192
    }

    normalized = normalize_pricing_data(test_data)
    print(f"   ✓ Data normalization works")

    text = pricing_to_text(normalized)
    print(f"   ✓ Text conversion works")
    print(f"   Example text: {text[:80]}...")

except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    sys.exit(1)

print("\n2. Testing PricingKnowledgeBase module...")
try:
    from utils.pricing_knowledge_base import PricingKnowledgeBase

    print("   ✓ PricingKnowledgeBase imported successfully")
    print("   Note: ChromaDB initialization will happen when instantiated")

except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    sys.exit(1)

print("\n3. Checking file structure...")
required_files = [
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "main.py",
    "data/pricing_schema.json",
    "utils/pricing_knowledge_base.py",
    "utils/data_normalizer.py"
]

for file in required_files:
    file_path = Path(__file__).parent / file
    if file_path.exists():
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ Missing: {file}")

print("\n" + "="*60)
print("Basic tests completed!")
print("="*60)
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the CLI: python main.py")
print("3. Try: test, query, stats commands")
print("\nFor full ChromaDB testing, run: python main.py")
