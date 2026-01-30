# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
uv sync                          # Backend (from project root)
cd frontend && npm install       # Frontend

# Run application - WINDOWS (PowerShell)
.\scripts\start-backend.ps1      # Backend on :8001
.\scripts\start-frontend.ps1     # Frontend on :5173
.\scripts\restart-all.ps1        # Restart both (after code changes)
.\scripts\status.ps1             # Check if running
.\scripts\logs.ps1               # View logs in real-time

# Run application - Linux/Mac
./start.sh                       # Both servers
# Or manually:
uv run python -m backend.main    # Backend on :8001 (MUST run from project root)
cd frontend && npm run dev       # Frontend on :5173

# Lint
cd frontend && npm run lint

# Test API connectivity
uv run python test_openrouter.py
uv run python test_search.py     # Test web search providers
uv run python test_chairman.py   # Test Chairman model
uv run python test_stage3.py     # Test Stage 3 synthesis
```

**Environment Configuration:**
- System prefers `.env.dev` over `.env` (see `config.py:9-13`)
- All scripts automatically use `.env.dev` if it exists
- Useful for maintaining separate dev/prod configs

**IMPORTANT - After Code Changes:**
Backend code changes require restart to take effect:
```powershell
# Windows
.\scripts\restart-backend.ps1

# Linux/Mac
# Stop backend (Ctrl+C), then restart:
uv run python -m backend.main
```

## Project Overview

LLM Council is a 3-stage deliberation system where multiple LLMs answer user questions collaboratively:
1. **Stage 1**: Parallel queries to all council models
2. **Stage 2**: Anonymized peer review (models rank each other's responses as "Response A, B, C...")
3. **Stage 3**: Chairman model synthesizes final answer

## Architecture

**Backend (FastAPI):** `backend/`
- `config.py` - `COUNCIL_MODELS` list, `CHAIRMAN_MODEL`, API keys from `.env`
- `council.py` - Core 3-stage logic, ranking parsing, aggregate calculation, web search integration
- `openrouter.py` - Async model queries via OpenRouter API
- `bedrock.py` - Async model queries via AWS Bedrock
- `search_providers.py` - Multi-provider web search with automatic fallback
- `storage.py` - JSON storage in `data/conversations/`
- `main.py` - FastAPI app with CORS for localhost:5173 and :3000

**Frontend (React + Vite):** `frontend/src/`
- Tab views for inspecting individual model responses (Stage 1) and evaluations (Stage 2)
- Client-side de-anonymization for display (models see anonymous labels)
- Metadata (label_to_model, aggregate_rankings) stored in UI state only, not persisted

## Key Implementation Details

- **Relative imports required**: Backend uses `from .config import ...` - run as module from project root
- **Port 8001**: Backend runs on 8001 (not 8000). Update `main.py` and `frontend/src/api.js` if changing
- **Markdown wrapper**: All ReactMarkdown must be wrapped in `<div className="markdown-content">`
- **Graceful degradation**: Single model failures don't fail the entire request

## Web Search with Fallback

Optional real-time web search provides councils with current information. The system supports multiple search providers with automatic fallback:

**Supported Providers (tried in order):**
1. **Tavily** - Specialized AI search with answer generation
2. **Serper** - Google Search API with answer boxes
3. **Brave Search** - Privacy-focused search
4. **SerpAPI** - Google Search with rich snippets

**Configuration:**
- Add API key(s) to `.env` (see `.env.example`)
- System tries providers in order until one succeeds
- Only ONE provider key needed for search to work
- If all providers fail, council proceeds without search context

**Search flow:**
1. User query triggers web search before Stage 1
2. Search results formatted into context for all council models
3. Models cite sources in their responses
4. If search fails, degraded gracefully to knowledge-only responses

## Stage 2 Prompt Format

Models must output rankings in this format for reliable parsing:
```
1. Evaluate each response individually
2. Output "FINAL RANKING:" header
3. Numbered list: "1. Response C", "2. Response A", etc.
```

Fallback regex extracts "Response X" patterns if format isn't followed exactly.

## Data Flow

```
User Query → Stage 1 (parallel) → Stage 2 (anonymize + parallel rank)
→ Aggregate Rankings → Stage 3 (chairman synthesis) → Return to frontend
```
