# 🚀 GenAIFinOps - Setup Instructions

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Steps

### 1. Navigate to the project directory

```bash
cd gen_ai_finops
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

This will install:
- beautifulsoup4 (web scraping)
- requests (HTTP client)
- chromadb (vector database)
- langchain (LLM framework)
- litellm (multi-provider LLM interface)
- pydantic (data validation)
- tiktoken (token counting)
- and more...

### 5. Configure environment (optional)

```bash
cp .env.example .env
```

Edit `.env` and add your API keys if needed (for future agents).

### 6. Run the application

```bash
python main.py
```

## Quick Test

Once inside the CLI:

```
GenAIFinOps> test
```

This adds sample pricing data to ChromaDB.

```
GenAIFinOps> query What is the cheapest model?
```

This performs semantic search.

```
GenAIFinOps> stats
```

Shows knowledge base statistics.

## Troubleshooting

### "No module named 'chromadb'"

Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "Permission denied" when running Python

Make sure the script is executable:
```bash
chmod +x main.py
```

### ChromaDB initialization errors

The `data/chroma_db/` directory will be created automatically on first run.
Make sure you have write permissions in the project directory.

## Next Steps

After successful setup:

1. Explore the CLI commands with `help`
2. Add your own pricing data with `add`
3. Test semantic queries with `query`
4. Check the code in `utils/pricing_knowledge_base.py` to understand the RAG implementation

## Project Structure

```
gen_ai_finops/
├── agents/                    # Future: scraper, oracle, architect agents
├── data/
│   ├── chroma_db/            # ChromaDB vector database (created on first run)
│   ├── scraped_pricing/      # Future: raw scraped data
│   └── pricing_schema.json   # Standard pricing data schema
├── utils/
│   ├── pricing_knowledge_base.py  # ChromaDB wrapper (THE BRAIN)
│   ├── data_normalizer.py         # Data validation & normalization
│   └── __init__.py
├── config/
├── main.py                   # CLI entry point - START HERE
├── pyproject.toml           # Dependency source of truth
├── requirements.txt         # Generated from pyproject.toml
└── README.md                # Project overview
```

## Development

To run tests (basic syntax check):
```bash
python test_basic.py
```

To check code quality (after installing dev dependencies):
```bash
pip install -e ".[dev]"
black .
ruff check .
```

---

**Need help?** Check README.md or open an issue on GitHub.
