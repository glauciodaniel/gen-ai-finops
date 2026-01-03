# GenAIFinOps - Complete Quickstart Guide

Get the full-stack GenAIFinOps platform running in under 5 minutes!

## Prerequisites

- Python 3.10+ (for backend)
- Node.js 18+ (for frontend)
- pip (Python package manager)
- npm (Node package manager)

## Step 1: Setup Backend API

### Install Python Dependencies

```bash
cd gen_ai_finops
pip install -r requirements.txt
```

### Configure Environment (Optional)

For full LLM functionality, create a `.env` file:

```bash
# OpenAI (recommended)
OPENAI_API_KEY=your_key_here

# OR Anthropic
ANTHROPIC_API_KEY=your_key_here
```

**Note:** The system works in fallback mode without API keys, using hardcoded seed data.

### Populate Knowledge Base

```bash
python main.py scrape
```

This will populate the ChromaDB with pricing data.

### Start Backend Server

```bash
python main.py server
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Keep this terminal running!**

## Step 2: Setup Frontend

### Install Dependencies

Open a **new terminal** in the project root:

```bash
npm install
```

### Configure API URL (Optional)

Create `.env` file in project root:

```bash
VITE_API_URL=http://localhost:8000
```

**Note:** This is already the default, so you can skip this step.

### Start Frontend

```bash
npm run dev
```

The app will be available at:
- **URL:** http://localhost:5173

## Step 3: Use the Platform

### Dashboard (Home)

Visit http://localhost:5173

You'll see:
- System health metrics
- Total models and providers
- Quick start guide

### Oracle (Pricing Chat)

Navigate to **Oracle** in the sidebar.

Try asking:
- "What is the cheapest GPT model?"
- "Which models support function calling?"
- "Compare GPT-4 and GPT-3.5 pricing"

### Architect (Cost Optimizer)

Navigate to **Architect** in the sidebar.

Example use case:

```
Use Case: Customer support chatbot with function calling
Monthly Input Tokens: 10000000
Current Model: gpt-4
```

Click **Optimize Stack** to see:
- Recommended model
- Annual savings (up to $4,767+!)
- Cost comparison chart
- Alternative options

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  Frontend (React + TypeScript)                   │
│  Port: 5173                                      │
│                                                  │
│  • Dashboard                                     │
│  • Oracle (Chat)                                 │
│  • Architect (Optimizer)                         │
│                                                  │
└────────────────┬─────────────────────────────────┘
                 │
                 │ REST API calls
                 │
┌────────────────▼─────────────────────────────────┐
│                                                  │
│  Backend API (FastAPI)                           │
│  Port: 8000                                      │
│                                                  │
│  • Oracle Agent (RAG + LLM)                      │
│  • Architect Agent (FinOps)                      │
│  • Scraper Agent (Data Ingestion)                │
│                                                  │
└────────────────┬─────────────────────────────────┘
                 │
                 │
┌────────────────▼─────────────────────────────────┐
│                                                  │
│  ChromaDB (Vector Database)                      │
│  Location: gen_ai_finops/data/chroma_db/         │
│                                                  │
│  • Pricing data                                  │
│  • Model metadata                                │
│  • Embeddings                                    │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Typical Workflow

### 1. Initial Setup
```bash
# Terminal 1: Backend
cd gen_ai_finops
python main.py scrape    # Populate data (once)
python main.py server    # Start API

# Terminal 2: Frontend
npm run dev              # Start UI
```

### 2. Daily Usage
```bash
# Terminal 1: Backend
cd gen_ai_finops
python main.py server

# Terminal 2: Frontend
npm run dev
```

### 3. Update Pricing Data
```bash
# In backend terminal (or via API)
python main.py scrape
```

Or use the "Refresh Data" button in the Dashboard.

## API Endpoints

All available at http://localhost:8000/docs

**Key Endpoints:**

```bash
# Health check
GET /health

# Statistics
GET /api/stats

# Ask Oracle
POST /api/oracle/ask
{
  "question": "What is the cheapest model?",
  "n_results": 5
}

# Optimize costs
POST /api/architect/optimize
{
  "use_case_description": "Chatbot with function calling",
  "monthly_input_tokens": 10000000,
  "current_model": "gpt-4"
}

# Run scraper
POST /api/scraper/run
```

## Common Issues

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd gen_ai_finops
pip install -r requirements.txt
```

### Frontend can't connect to API

**Error:** Network errors in browser console

**Solutions:**
1. Ensure backend is running on port 8000
2. Check `.env` file has `VITE_API_URL=http://localhost:8000`
3. Verify CORS is enabled in backend (it should be by default)

### Empty knowledge base

**Symptom:** Dashboard shows 0 models

**Solution:**
```bash
cd gen_ai_finops
python main.py scrape
```

Then refresh the frontend.

### Port already in use

**Backend (8000):**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Frontend (5173):**
```bash
# Find process using port 5173
lsof -ti:5173 | xargs kill -9
```

## Testing the System

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/api/stats

# Ask Oracle
curl -X POST http://localhost:8000/api/oracle/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the cheapest model?"}'
```

### 2. Test Frontend

1. Visit http://localhost:5173
2. Click through Dashboard → Oracle → Architect
3. Try asking a question in Oracle
4. Try optimizing a use case in Architect

## Production Deployment

### Backend

1. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your_key
export PORT=8000
```

### Frontend

1. Build for production:
```bash
npm run build
```

2. Serve with a static server:
```bash
npm install -g serve
serve -s dist -p 3000
```

Or deploy to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Any static hosting

### Environment Variables

**Backend:**
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Frontend:**
- `VITE_API_URL` (e.g., `https://api.yourdomain.com`)

## Development Tips

### Backend

```bash
# Interactive mode
python main.py

# CLI commands
python main.py ask "your question"
python main.py scrape
python main.py help
```

### Frontend

```bash
# Development server (hot reload)
npm run dev

# Type checking
npm run typecheck

# Linting
npm run lint

# Production build
npm run build

# Preview build
npm run preview
```

## Project Statistics

**Backend:**
- 2,597 lines of Python
- 14 Python files
- 11 API endpoints
- 3 AI agents

**Frontend:**
- ~2,500 lines of TypeScript/React
- 15+ components
- 3 main pages
- Fully typed with TypeScript

**Total:**
- Full-stack platform in ~5,000 lines
- Complete with API, UI, database, and AI agents

## Next Steps

1. **Explore the Oracle:** Ask different pricing questions
2. **Test the Architect:** Try various use cases
3. **Check the API docs:** Visit http://localhost:8000/docs
4. **Read the documentation:**
   - `gen_ai_finops/README.md` - Backend overview
   - `gen_ai_finops/API.md` - API documentation
   - `FRONTEND_README.md` - Frontend details

## Support

Issues or questions?
1. Check API docs: http://localhost:8000/docs
2. Review implementation notes in `PHASE*.md` files
3. Check backend logs in Terminal 1
4. Check browser console for frontend errors

---

**Status**: ✅ Complete Full-Stack Platform

**Backend**: http://localhost:8000
**Frontend**: http://localhost:5173
**API Docs**: http://localhost:8000/docs

**Ready to save up to 99% on AI costs!**
