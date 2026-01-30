# LLM Council API Documentation

The LLM Council now provides a RESTful API and Model Context Protocol (MCP) integration, allowing external applications and AI assistants to consult the council programmatically.

## Quick Start

### 1. Create an API Key

```bash
python manage_api_keys.py create
```

Save the generated API key - it's only shown once!

### 2. Make Your First Request

```bash
curl -X POST http://localhost:8001/api/v1/council/ask \
  -H "X-API-Key: llmc_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the trade-offs between microservices and monolithic architecture?"
  }'
```

## Authentication

All API requests require an API key in the `X-API-Key` header:

```
X-API-Key: llmc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Endpoints

### POST /api/v1/council/ask

Consult the council with a question.

**Request Body:**
```json
{
  "question": "Your question here",
  "include_web_search": true,
  "include_stage1": false,
  "include_stage2": false
}
```

**Response:**
```json
{
  "answer": "The council's synthesized answer...",
  "chairman": "us.amazon.nova-premier-v1:0",
  "models_participated": 4,
  "web_search_used": true,
  "deliberation_path": "deliberations/2026-01-30-...",
  "metadata": {
    "aggregate_rankings": [...]
  }
}
```

### GET /api/v1/deliberations

List recent deliberations.

**Query Parameters:**
- `limit` (int): Maximum number of results (default: 10)

**Response:**
```json
{
  "deliberations": [...],
  "count": 10
}
```

### GET /api/v1/deliberations/{name}

Get a specific deliberation by name.

**Response:**
Complete deliberation data including all stages.

### POST /api/v1/deliberations/search

Search past deliberations.

**Request Body:**
```json
{
  "query": "microservices",
  "limit": 5
}
```

### GET /api/v1/stats

Get API usage statistics.

### GET /api/v1/mcp/tools

Get MCP tool definitions for AI assistants.

## Rate Limiting

Each API key has a configurable rate limit (default: 100 requests/hour).

When you exceed the limit, you'll receive a `429 Too Many Requests` response.

## Model Context Protocol (MCP) Integration

The council can be used as a tool by AI assistants like Claude via MCP.

### MCP Tools

**1. consult_llm_council**
- Consults the council of multiple AI models
- Returns synthesized answer from 3-stage deliberation
- Optional: Include individual model responses

**2. search_council_deliberations**
- Search past council deliberations
- Find historical context and previous wisdom

### Example: Using with Claude

When configuring Claude's tool use, add the council as a tool:

```json
{
  "name": "consult_llm_council",
  "description": "Consult a council of multiple AI models for diverse perspectives",
  "input_schema": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "The question to ask the council"
      }
    }
  }
}
```

Then Claude can call it like:
```json
{
  "tool": "consult_llm_council",
  "input": {
    "question": "What are the ethical implications of AGI?"
  }
}
```

## API Management

### Create API Key
```bash
python manage_api_keys.py create
```

### List API Keys
```bash
python manage_api_keys.py list
```

### Revoke API Key
```bash
python manage_api_keys.py revoke
```

### View Statistics
```bash
python manage_api_keys.py stats
```

## Examples

### Python

```python
import requests

API_KEY = "llmc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_URL = "http://localhost:8001/api/v1"

# Ask the council
response = requests.post(
    f"{API_URL}/council/ask",
    headers={"X-API-Key": API_KEY},
    json={
        "question": "What are the pros and cons of serverless architecture?",
        "include_stage1": True  # Include individual model responses
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Models: {result['models_participated']}")

# Search past deliberations
response = requests.post(
    f"{API_URL}/deliberations/search",
    headers={"X-API-Key": API_KEY},
    json={
        "query": "architecture",
        "limit": 5
    }
)

results = response.json()
print(f"Found {results['count']} deliberations")
```

### JavaScript

```javascript
const API_KEY = "llmc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
const API_URL = "http://localhost:8001/api/v1";

// Ask the council
const response = await fetch(`${API_URL}/council/ask`, {
  method: "POST",
  headers: {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    question: "What are the key differences between REST and GraphQL?",
    include_web_search: true
  })
});

const result = await response.json();
console.log("Answer:", result.answer);
```

### curl

```bash
# Ask a question
curl -X POST http://localhost:8001/api/v1/council/ask \
  -H "X-API-Key: llmc_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the security considerations for OAuth 2.0?"
  }'

# List deliberations
curl -X GET "http://localhost:8001/api/v1/deliberations?limit=5" \
  -H "X-API-Key: llmc_xxxxx"

# Search deliberations
curl -X POST http://localhost:8001/api/v1/deliberations/search \
  -H "X-API-Key: llmc_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "security",
    "limit": 10
  }'
```

## Error Responses

**401 Unauthorized**
```json
{
  "detail": "Invalid API key"
}
```

**429 Too Many Requests**
```json
{
  "detail": "Rate limit exceeded"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Council deliberation failed: ..."
}
```

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8001/api/v1/docs
- **ReDoc**: http://localhost:8001/api/v1/redoc

## Production Deployment

For production use:

1. **Use HTTPS** - Encrypt all API traffic
2. **Restrict CORS** - Update allowed origins in `api.py`
3. **Add Redis** - Implement proper time-window rate limiting
4. **Add PostgreSQL** - Store API keys and usage in database
5. **Monitor** - Set up logging and metrics (Prometheus/Grafana)
6. **Scale** - Use load balancers and multiple instances

## Support

For issues or questions:
- GitHub Issues: https://github.com/valter-silva-au/llm-council/issues
- Documentation: See README.md and deliberations/README.md
