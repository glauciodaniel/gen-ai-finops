#!/usr/bin/env python3
"""
GenAIFinOps - Main Entry Point
CLI interface for the AI Cost Optimization Platform

Usage:
    python main.py              # Interactive mode
    python main.py scrape       # Run scraper to populate knowledge base
    python main.py ask "question"  # Ask a pricing question
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from utils.pricing_knowledge_base import PricingKnowledgeBase
from utils.data_normalizer import normalize_pricing_data
from agents.scraper import OpenAIPricingScraper, MultiProviderScraper
from agents.oracle import PricingOracle

load_dotenv()


def display_banner():
    """Display the GenAIFinOps banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              💸 GenAIFinOps v0.1.0                       ║
    ║    The "Kubernetes" of AI Costs                          ║
    ║    Automated Token Optimization & Multi-Cloud Pricing    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def display_help():
    """Display help information."""
    help_text = """
    Available Commands:

    1. scrape   - Run scraper to populate knowledge base with OpenAI pricing
    2. ask      - Ask a pricing question (uses RAG + LLM)
    3. query    - Query pricing information using semantic search
    4. add      - Add pricing data to the knowledge base
    5. stats    - Display knowledge base statistics
    6. list     - List all providers or models
    7. test     - Run with sample data for testing
    8. clear    - Clear all data from the knowledge base
    9. server   - Start REST API server (CLI only: python main.py server)
    10. help    - Display this help message
    11. exit    - Exit the application

    Examples:
        > scrape
        > ask What is the cheapest model for embeddings?
        > query How much does GPT-4 cost?
        > list providers
        > stats
    """
    print(help_text)


def command_add(kb: PricingKnowledgeBase):
    """Handle the 'add' command to add pricing data."""
    print("\nAdd Pricing Data")
    print("Enter pricing data as JSON (or 'cancel' to abort):")
    print("Example: {\"provider\": \"OpenAI\", \"model_name\": \"gpt-4\", \"input_cost_per_1m_tokens\": 30.0, \"output_cost_per_1m_tokens\": 60.0}")

    try:
        user_input = input("\nJSON data: ").strip()
        if user_input.lower() == 'cancel':
            print("Cancelled.")
            return

        data = json.loads(user_input)
        count = kb.add_prices(data)
        print(f"\n✓ Successfully added {count} pricing entry(ies).")

    except json.JSONDecodeError:
        print("✗ Error: Invalid JSON format.")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def command_query(kb: PricingKnowledgeBase):
    """Handle the 'query' command for semantic search."""
    print("\nSemantic Pricing Query")
    print("Ask a question about pricing (or 'cancel' to abort):")

    query = input("\nYour question: ").strip()
    if query.lower() == 'cancel':
        print("Cancelled.")
        return

    print("\nSearching...")
    results = kb.query_prices(query, n_results=5)

    if not results:
        print("No results found. Try adding more data first.")
        return

    print(f"\nFound {len(results)} relevant result(s):\n")
    for idx, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"{idx}. {meta['provider']} - {meta['model_name']}")
        print(f"   Input:  ${meta['input_cost']}/1M tokens")
        print(f"   Output: ${meta['output_cost']}/1M tokens")
        print(f"   Updated: {meta['last_updated'][:10]}")
        print()


def command_stats(kb: PricingKnowledgeBase):
    """Display knowledge base statistics."""
    print("\nKnowledge Base Statistics:")
    stats = kb.get_stats()
    print(json.dumps(stats, indent=2))


def command_list(kb: PricingKnowledgeBase):
    """List providers or models."""
    print("\nList Options:")
    print("1. providers - List all providers")
    print("2. models    - List all models")

    choice = input("\nYour choice: ").strip().lower()

    if choice == 'providers' or choice == '1':
        providers = kb.get_all_providers()
        print(f"\nProviders ({len(providers)}):")
        for provider in providers:
            print(f"  - {provider}")

    elif choice == 'models' or choice == '2':
        models = kb.get_all_models()
        print(f"\nModels ({len(models)}):")
        for model in models:
            print(f"  - {model['provider']}: {model['model_name']} (${model['input_cost']}/1M in)")

    else:
        print("Invalid choice.")


def command_test(kb: PricingKnowledgeBase):
    """Add sample test data."""
    print("\nAdding sample test data...")

    sample_data = [
        {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0,
            "context_window": 8192,
            "supports_function_calling": True
        },
        {
            "provider": "OpenAI",
            "model_name": "gpt-3.5-turbo",
            "input_cost_per_1m_tokens": 0.5,
            "output_cost_per_1m_tokens": 1.5,
            "context_window": 16385,
            "supports_function_calling": True
        },
        {
            "provider": "Anthropic",
            "model_name": "claude-3-opus",
            "input_cost_per_1m_tokens": 15.0,
            "output_cost_per_1m_tokens": 75.0,
            "context_window": 200000
        },
        {
            "provider": "Google",
            "model_name": "gemini-pro",
            "input_cost_per_1m_tokens": 0.5,
            "output_cost_per_1m_tokens": 1.5,
            "context_window": 32768
        }
    ]

    count = kb.add_prices(sample_data)
    print(f"\n✓ Successfully added {count} sample entries.")
    print("Try querying: 'What is the cheapest model?' or 'Compare GPT-4 and Claude'")


def command_clear(kb: PricingKnowledgeBase):
    """Clear all data from the knowledge base."""
    print("\n⚠️  WARNING: This will delete ALL data from the knowledge base!")
    confirm = input("Type 'yes' to confirm: ").strip().lower()

    if confirm == 'yes':
        kb.clear_all()
        print("✓ Knowledge base cleared.")
    else:
        print("Cancelled.")


def command_scrape(kb: PricingKnowledgeBase):
    """Run the scraper to populate the knowledge base."""
    print("\n🤖 Running OpenAI Pricing Scraper...\n")

    scraper = OpenAIPricingScraper(kb)
    count = scraper.run()

    if count > 0:
        print(f"\n✓ Scraping complete! {count} entries added.")
        print("\nTry asking: 'What is the cheapest GPT model?'")
    else:
        print("\n✗ Scraping failed or no data was added.")


def command_ask(kb: PricingKnowledgeBase, question: str = None):
    """Ask the Oracle a pricing question using RAG + LLM."""
    if not question:
        print("\n💬 Ask the Pricing Oracle")
        print("Enter your question (or 'cancel' to abort):")
        question = input("\nQuestion: ").strip()

        if question.lower() == 'cancel' or not question:
            print("Cancelled.")
            return

    print()
    oracle = PricingOracle(kb)
    answer = oracle.ask(question)

    print("="*60)
    print("Oracle Response:")
    print("="*60)
    print(answer)
    print("="*60)


def main():
    """Main CLI loop."""
    display_banner()

    print("Initializing ChromaDB Knowledge Base...\n")
    kb = PricingKnowledgeBase()

    print("\nType 'help' for available commands, 'scrape' to populate data, or 'test' for sample data.\n")

    while True:
        try:
            user_input = input("GenAIFinOps> ").strip()

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                break

            elif command == 'help' or command == 'h':
                display_help()

            elif command == 'scrape':
                command_scrape(kb)

            elif command == 'ask':
                command_ask(kb, args if args else None)

            elif command == 'add':
                command_add(kb)

            elif command == 'query':
                if args:
                    print("\nSearching...")
                    results = kb.query_prices(args, n_results=5)
                    if results:
                        print(f"\nFound {len(results)} result(s):\n")
                        for idx, result in enumerate(results, 1):
                            meta = result['metadata']
                            print(f"{idx}. {meta['provider']} - {meta['model_name']}")
                            print(f"   Input: ${meta['input_cost']}/1M | Output: ${meta['output_cost']}/1M")
                            print()
                    else:
                        print("No results found.")
                else:
                    command_query(kb)

            elif command == 'stats':
                command_stats(kb)

            elif command == 'list':
                command_list(kb)

            elif command == 'test':
                command_test(kb)

            elif command == 'clear':
                command_clear(kb)

            elif command == 'server':
                print("\n⚠️  Server mode must be run from command line:")
                print("   python main.py server")
                print()

            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break

        except Exception as e:
            print(f"Error: {str(e)}")


def cli_mode():
    """Handle command-line arguments for non-interactive mode."""
    if len(sys.argv) < 2:
        main()
        return

    command = sys.argv[1].lower()

    kb = PricingKnowledgeBase()

    if command == 'scrape':
        print("🤖 Running scraper...\n")
        scraper = OpenAIPricingScraper(kb)
        count = scraper.run()
        print(f"\n✓ Complete! {count} entries added to knowledge base.")

    elif command == 'ask':
        if len(sys.argv) < 3:
            print("Error: Please provide a question.")
            print('Usage: python main.py ask "your question here"')
            sys.exit(1)

        question = " ".join(sys.argv[2:])
        oracle = PricingOracle(kb)
        answer = oracle.ask(question)

        print("\n" + "="*60)
        print("Oracle Response:")
        print("="*60)
        print(answer)
        print("="*60 + "\n")

    elif command == 'server':
        print("🚀 Starting GenAIFinOps API Server...\n")
        print("API Documentation will be available at:")
        print("  • Swagger UI: http://localhost:8000/docs")
        print("  • ReDoc: http://localhost:8000/redoc")
        print("\nPress Ctrl+C to stop the server\n")

        try:
            import uvicorn
            from api.main import app

            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        except ImportError:
            print("✗ Error: FastAPI and Uvicorn are required to run the server.")
            print("   Install with: pip install fastapi uvicorn[standard]")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Server error: {str(e)}")
            sys.exit(1)

    elif command == 'help' or command == '--help' or command == '-h':
        print("""
GenAIFinOps CLI

Usage:
    python main.py              # Interactive mode
    python main.py scrape       # Run scraper
    python main.py ask "question"  # Ask a question
    python main.py server       # Start REST API server

Interactive Commands:
    scrape  - Populate knowledge base from OpenAI
    ask     - Ask pricing question (RAG + LLM)
    query   - Semantic search only
    test    - Add sample data
    stats   - Show statistics
    list    - List providers/models
    help    - Show help
    exit    - Exit
        """)

    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py help' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    cli_mode()
