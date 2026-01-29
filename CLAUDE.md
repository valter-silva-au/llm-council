# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
uv sync                          # Backend (from project root)
cd frontend && npm install       # Frontend

# Run application
./start.sh                       # Both servers (Linux/Mac)

# Or manually:
uv run python -m backend.main    # Backend on :8001 (MUST run from project root)
cd frontend && npm run dev       # Frontend on :5173

# Lint
cd frontend && npm run lint

# Test API connectivity
uv run python test_openrouter.py
```

## Project Overview

LLM Council is a 3-stage deliberation system where multiple LLMs answer user questions collaboratively:
1. **Stage 1**: Parallel queries to all council models
2. **Stage 2**: Anonymized peer review (models rank each other's responses as "Response A, B, C...")
3. **Stage 3**: Chairman model synthesizes final answer

## Architecture

**Backend (FastAPI):** `backend/`
- `config.py` - `COUNCIL_MODELS` list, `CHAIRMAN_MODEL`, reads `OPENROUTER_API_KEY` from `.env`
- `council.py` - Core 3-stage logic, ranking parsing, aggregate calculation
- `openrouter.py` - Async model queries via OpenRouter API
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
