# GenAIFinOps REST API Documentation

## Overview

The GenAIFinOps REST API provides programmatic access to the cost optimization platform. Use these endpoints to query pricing data, get model recommendations, and optimize your AI costs.

**Base URL (local)**: `http://localhost:8000`

**API Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Starting the Server

```bash
python main.py server
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently, the API does not require authentication. This will be added in future versions for production deployments.

## Endpoints

### General

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "name": "GenAIFinOps API",
  "version": "0.2.0",
  "description": "The 'Kubernetes' of AI Costs",
  "docs": "/docs",
  "endpoints": {
    "oracle": "/api/oracle/ask",
    "architect": "/api/architect/optimize",
    "scraper": "/api/scraper/status",
    "query": "/api/query"
  }
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.2.0",
  "knowledge_base_status": "operational",
  "llm_available": true
}
```

---

### Oracle (RAG-Powered Pricing Queries)

#### `POST /api/oracle/ask`
Ask the Oracle a pricing question using RAG + LLM.

**Request Body:**
```json
{
  "question": "What is the cheapest model for embeddings?",
  "n_results": 5
}
```

**Response:**
```json
{
  "status": "success",
  "question": "What is the cheapest model for embeddings?",
  "answer": "Based on the pricing data, the cheapest model for embeddings is Text Embedding 3 Small at $0.02 per 1M tokens...",
  "context_used": 5
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/oracle/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the cheapest GPT model?"}'
```

---

### Architect (Cost Optimization)

#### `POST /api/architect/optimize`
Analyze a use case and get model recommendations with cost calculations.

**Request Body:**
```json
{
  "use_case_description": "Chatbot for customer support with function calling",
  "monthly_input_tokens": 10000000,
  "monthly_output_tokens": 2000000,
  "current_model": "gpt-4"
}
```

**Response:**
```json
{
  "status": "success",
  "use_case": "Chatbot for customer support with function calling",
  "requirements": {
    "needs_function_calling": true,
    "needs_vision": false,
    "needs_large_context": false,
    "max_latency_tolerance": "low",
    "quality_requirement": "medium",
    "budget_priority": "medium"
  },
  "recommendation": {
    "model": "OpenAI gpt-4o-mini",
    "monthly_cost": "$2.70",
    "monthly_cost_raw": 2.7,
    "reasoning": "Supports function calling | Very affordable",
    "action": "Switch to gpt-4o-mini to save $397.30/month"
  },
  "alternatives": [
    {
      "provider": "OpenAI",
      "model_name": "gpt-4o-mini",
      "monthly_cost": "$2.70",
      "monthly_cost_raw": 2.7,
      "input_cost_per_1m": "$0.15",
      "output_cost_per_1m": "$0.60",
      "match_score": 150,
      "reasons": ["Supports function calling", "Very affordable"],
      "context_window": 128000,
      "supports_function_calling": true,
      "supports_vision": true
    }
  ],
  "volume": {
    "monthly_input_tokens": 10000000,
    "monthly_output_tokens": 2000000
  },
  "current_model": {
    "name": "gpt-4",
    "monthly_cost": "$400.00",
    "monthly_cost_raw": 400.0
  },
  "savings": {
    "monthly": "$397.30",
    "monthly_raw": 397.3,
    "annual": "$4767.60",
    "annual_raw": 4767.6,
    "percentage": "99.3%"
  }
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/architect/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "use_case_description": "Simple text classification",
    "monthly_input_tokens": 5000000,
    "current_model": "gpt-4"
  }'
```

---

### Scraper

#### `GET /api/scraper/status`
Get the current status of the pricing knowledge base.

**Response:**
```json
{
  "status": "operational",
  "total_models": 8,
  "providers": ["OpenAI"],
  "last_updated": "2026-01-03T12:34:56.789Z"
}
```

#### `POST /api/scraper/run`
Manually trigger the scraper to update pricing data.

**Response:**
```json
{
  "status": "success",
  "message": "Scraper completed successfully",
  "entries_added": 8
}
```

---

### Search & Data

#### `POST /api/query`
Perform semantic search on pricing data (without LLM processing).

**Query Parameters:**
- `query` (string, required): Search query
- `n_results` (int, optional): Number of results (default: 5)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/query?query=cheap%20models&n_results=3"
```

**Response:**
```json
{
  "status": "success",
  "query": "cheap models",
  "results": [
    {
      "provider": "OpenAI",
      "model_name": "text-embedding-3-small",
      "input_cost": 0.02,
      "output_cost": 0.0,
      "context_window": 8191,
      "supports_function_calling": false
    }
  ],
  "total_results": 3
}
```

#### `GET /api/providers`
List all available providers.

**Response:**
```json
{
  "status": "success",
  "providers": ["OpenAI"],
  "total": 1
}
```

#### `GET /api/models`
List all models in the knowledge base.

**Response:**
```json
{
  "status": "success",
  "models": [
    {
      "provider": "OpenAI",
      "model_name": "gpt-4o",
      "input_cost": 2.5,
      "output_cost": 10.0,
      "context_window": 128000
    }
  ],
  "total": 8
}
```

#### `GET /api/stats`
Get knowledge base statistics.

**Response:**
```json
{
  "status": "success",
  "total_models": 8,
  "providers": ["OpenAI"],
  "provider_counts": {
    "OpenAI": 8
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "status": "error",
  "message": "Error description",
  "detail": "Additional details (optional)"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently, there is no rate limiting. This will be added in production versions.

---

## CORS

CORS is enabled for all origins (`*`). This is suitable for development but should be restricted in production.

---

## Examples

### Python

```python
import requests

# Ask the Oracle
response = requests.post(
    "http://localhost:8000/api/oracle/ask",
    json={"question": "What is the cheapest model?"}
)
print(response.json()["answer"])

# Get cost optimization
response = requests.post(
    "http://localhost:8000/api/architect/optimize",
    json={
        "use_case_description": "Document analysis with vision",
        "monthly_input_tokens": 5000000,
        "current_model": "gpt-4-turbo"
    }
)
print(response.json()["recommendation"])
```

### JavaScript (fetch)

```javascript
// Ask the Oracle
const response = await fetch('http://localhost:8000/api/oracle/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Compare GPT-4 and GPT-3.5 pricing'
  })
});
const data = await response.json();
console.log(data.answer);

// Get optimization
const optResponse = await fetch('http://localhost:8000/api/architect/optimize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    use_case_description: 'Chatbot with function calling',
    monthly_input_tokens: 10000000,
    current_model: 'gpt-4'
  })
});
const optData = await optResponse.json();
console.log(optData.savings);
```

---

## Future Enhancements

- Authentication & API Keys
- Rate limiting
- Webhooks for price changes
- Batch operations
- Historical pricing data
- Cost alerts and notifications

---

**Version**: 0.2.0
**Last Updated**: 2026-01-03
