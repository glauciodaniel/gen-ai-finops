# 💸 GenAIFinOps - The "Kubernetes" of AI Costs

> **Automated Token Optimization & Multi-Cloud Pricing Intelligence**

## 📦 Status: Phase 1 + 2 + 3 COMPLETE ✅

Full-stack FinOps platform with REST API ready for production!

### What's Implemented:

**Phase 1 - Foundation:**
- ✅ Project structure and dependency management
- ✅ ChromaDB vector database integration
- ✅ Pricing data schema and validation
- ✅ `PricingKnowledgeBase` class (the "brain")
- ✅ CLI interface for testing

**Phase 2 - Intelligence:**
- ✅ OpenAI pricing scraper with seed data
- ✅ Oracle agent (RAG + LLM)
- ✅ Natural language pricing queries
- ✅ Multi-provider LLM support via litellm
- ✅ Fallback mode for offline operation

**Phase 3 - FinOps + API:**
- ✅ Cost Architect agent with optimization logic
- ✅ Intelligent requirement extraction from use cases
- ✅ Monthly/annual cost calculations
- ✅ FastAPI REST API with 11 endpoints
- ✅ Automatic OpenAPI documentation (Swagger + ReDoc)
- ✅ CORS support for frontend integration
- ✅ Async request processing

## 🚀 Quick Start

### 1. Installation

```bash
cd gen_ai_finops

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database

```bash
# Install PostgreSQL (if not already installed)
# On Ubuntu/Debian: sudo apt-get install postgresql
# On macOS: brew install postgresql
# On Windows: Download from postgresql.org

# Create database
createdb gen_ai_finops
# Or using psql:
# psql -U postgres
# CREATE DATABASE gen_ai_finops;

# Run migrations
cd gen_ai_finops
alembic upgrade head

# Create admin user (optional)
python scripts/create_admin_user.py
```

### 3. Configure Environment Variables

```bash
cp env.example .env
# Edit .env and configure:
# - DATABASE_URL (PostgreSQL connection string)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY (optional)
# - JWT_SECRET_KEY (change in production!)
```

**Note:** System works without API keys in fallback mode!

### 4. Populate the Knowledge Base

```bash
# Option 1: Use real OpenAI pricing (scrapes or uses seed data)
python main.py scrape

# Option 2: Use sample test data
python main.py
GenAIFinOps> test
```

### 5. Ask Pricing Questions

```bash
# Command-line mode
python main.py ask "What is the cheapest GPT model?"

# Interactive mode
python main.py
GenAIFinOps> ask What models support function calling?
GenAIFinOps> ask Compare GPT-4o and GPT-3.5 pricing
GenAIFinOps> stats
```

### 6. Start the API Server

```bash
python main.py server
```

Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

See [API.md](API.md) for complete API documentation.

## 🏗 Architecture

```
gen_ai_finops/
├── agents/                    # AI agents (scraper, oracle, architect)
│   └── __init__.py
├── data/
│   ├── chroma_db/            # ChromaDB persistence (local vector DB)
│   ├── scraped_pricing/      # Raw scraped data
│   └── pricing_schema.json   # Standard pricing schema
├── utils/
│   ├── pricing_knowledge_base.py  # ChromaDB wrapper (the "brain")
│   ├── data_normalizer.py         # Data validation & normalization
│   └── __init__.py
├── config/
│   └── __init__.py
├── .env.example              # Environment variables template
├── .gitignore
├── main.py                   # CLI entry point
├── pyproject.toml           # Source of truth for dependencies
├── requirements.txt         # Generated from pyproject.toml
└── README.md
```

## 🧠 The Knowledge Base

The `PricingKnowledgeBase` class wraps ChromaDB and provides:

### Key Methods:

```python
from utils.pricing_knowledge_base import PricingKnowledgeBase

# Initialize
kb = PricingKnowledgeBase()

# Add pricing data
kb.add_prices([{
    "provider": "OpenAI",
    "model_name": "gpt-4",
    "input_cost_per_1m_tokens": 30.0,
    "output_cost_per_1m_tokens": 60.0
}])

# Semantic search
results = kb.query_prices("What is the cheapest model?", n_results=5)

# Get stats
stats = kb.get_stats()
```

## 📊 Data Schema

All pricing data follows this standardized schema:

```json
{
  "provider": "OpenAI",
  "model_name": "gpt-4",
  "model_display_name": "GPT-4",
  "input_cost_per_1m_tokens": 30.0,
  "output_cost_per_1m_tokens": 60.0,
  "context_window": 8192,
  "supports_function_calling": true,
  "supports_vision": false,
  "supports_json_mode": true,
  "last_updated": "2026-01-03T00:00:00Z"
}
```

See `data/pricing_schema.json` for the complete schema.

## 🔧 CLI Commands

### Command-Line Mode:

```bash
python main.py scrape              # Run scraper to populate KB
python main.py ask "your question" # Ask Oracle a question
python main.py help                # Show help
```

### Interactive Mode:

| Command | Description |
|---------|-------------|
| `scrape` | Run scraper to populate knowledge base with OpenAI pricing |
| `ask <question>` | Ask Oracle a pricing question (RAG + LLM) |
| `query <question>` | Semantic search only (no LLM) |
| `test` | Add sample pricing data |
| `add` | Add new pricing data (JSON format) |
| `list providers` | Show all providers |
| `list models` | Show all models |
| `stats` | Display knowledge base statistics |
| `clear` | Clear all data (use with caution!) |
| `help` | Show all commands |
| `exit` | Exit the application |

## 🎯 Example Queries

```
> query What is the cheapest model for function calling?
> query Compare GPT-4 and Claude 3 Opus pricing
> query Quanto custa o Gemini Pro?
> query Which models support vision?
```

## 🔍 How RAG Works Here

1. **Data Ingestion**: Pricing data is converted to meaningful text via `pricing_to_text()`
2. **Vectorization**: Text is embedded using ChromaDB's default embedding function
3. **Storage**: Vectors + metadata are persisted to `./data/chroma_db`
4. **Query**: User question is vectorized and compared via cosine similarity
5. **Retrieval**: Most relevant pricing entries are returned

This is **pure semantic search** - no SQL, no exact matching required!

## 📝 Notes

- ChromaDB data persists locally in `./data/chroma_db`
- The database is portable - commit it to Git if needed
- Default embedding function is used (can be swapped for custom models)
- All pricing data is validated against the schema before insertion

## 🚧 Coming Next (Phase 4 - Frontend)

- [ ] React dashboard with Tailwind CSS
- [ ] Real-time cost calculator interface
- [ ] Model comparison charts and visualizations
- [ ] Token usage tracking dashboard
- [ ] Cost alerts and notifications
- [ ] Saved optimization scenarios
- [ ] Export reports (PDF/CSV)
- [ ] Live web scraping (real-time pricing updates)
- [ ] Multi-provider scrapers (Anthropic, Google, AWS Bedrock, Azure)
- [ ] Slack/Discord bot integration

## 📄 License

MIT License - See LICENSE for details.

---

**Status**: ✅ Phase 1 + 2 + 3 Complete - Full Backend + API Operational

See implementation notes:
- `PHASE1_COMPLETE.md` - ChromaDB & Knowledge Base
- `PHASE2_COMPLETE.md` - Scraper & Oracle (RAG)
- `PHASE3_COMPLETE.md` - Architect & REST API
- `API.md` - Complete API documentation
