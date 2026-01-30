"""External API for LLM Council.

Provides RESTful API and MCP endpoints for external integrations.
"""

import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from .council import run_full_council
from .api_keys import validate_api_key, record_api_usage, get_api_stats
from .deliberations import list_deliberations, get_deliberation, search_deliberations

logger = logging.getLogger("llm_council.api")

# Create API app (mounted at /api/v1 by main.py)
api_app = FastAPI(
    title="LLM Council API",
    description="External API for consulting the LLM Council",
    version="1.0.0"
)

# Enable CORS
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class CouncilRequest(BaseModel):
    """Request to consult the council."""
    question: str
    include_web_search: bool = True
    include_stage1: bool = False  # Return individual responses
    include_stage2: bool = False  # Return rankings


class CouncilResponse(BaseModel):
    """Response from the council."""
    answer: str
    chairman: str
    models_participated: int
    web_search_used: bool
    deliberation_path: Optional[str] = None
    stage1: Optional[List[Dict[str, str]]] = None
    stage2: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class DeliberationSearch(BaseModel):
    """Search for past deliberations."""
    query: str
    limit: int = 10


# Dependency: Validate API Key
async def validate_api_key_header(x_api_key: Optional[str] = Header(None)):
    """
    Validate API key from header.

    Args:
        x_api_key: API key from X-API-Key header

    Raises:
        HTTPException: If key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Include X-API-Key header.")

    key_data = validate_api_key(x_api_key)

    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Record usage
    if not record_api_usage(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return key_data


# Endpoints
@api_app.get("/")
async def root():
    """API root endpoint."""
    return {
        "service": "LLM Council API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@api_app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@api_app.post("/council/ask", response_model=CouncilResponse)
async def ask_council(
    request: CouncilRequest,
    api_key_data: dict = Depends(validate_api_key_header)
):
    """
    Consult the LLM Council with a question.

    This endpoint runs the full 3-stage council deliberation:
    - Stage 1: Individual model responses
    - Stage 2: Peer rankings
    - Stage 3: Chairman synthesis

    Args:
        request: The council request
        api_key_data: Validated API key data (injected)

    Returns:
        The council's answer and metadata

    Example:
        ```bash
        curl -X POST https://api.llmcouncil.com/v1/council/ask \\
          -H "X-API-Key: llmc_xxxxx" \\
          -H "Content-Type: application/json" \\
          -d '{
            "question": "What are the pros and cons of microservices?",
            "include_stage1": true
          }'
        ```
    """
    logger.info(f"API request from: {api_key_data.get('name')}")
    logger.info(f"Question: {request.question[:100]}...")

    try:
        # Run the council deliberation
        stage1, stage2, stage3, metadata = await run_full_council(request.question)

        # Build response
        response = CouncilResponse(
            answer=stage3.get("response", ""),
            chairman=stage3.get("model", "unknown"),
            models_participated=len(stage1),
            web_search_used=metadata.get("deliberation_path") is not None,
            deliberation_path=metadata.get("deliberation_path"),
            metadata={
                "aggregate_rankings": metadata.get("aggregate_rankings", [])
            }
        )

        # Include optional data
        if request.include_stage1:
            response.stage1 = stage1

        if request.include_stage2:
            response.stage2 = stage2

        logger.info(f"Council responded: {len(response.answer)} chars")
        return response

    except Exception as e:
        logger.error(f"Error in council deliberation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Council deliberation failed: {str(e)}")


@api_app.get("/deliberations")
async def get_deliberations(
    limit: int = 10,
    api_key_data: dict = Depends(validate_api_key_header)
):
    """
    List recent council deliberations.

    Args:
        limit: Maximum number of results
        api_key_data: Validated API key data

    Returns:
        List of deliberation metadata
    """
    logger.info(f"Listing deliberations: {api_key_data.get('name')}")

    deliberations = list_deliberations(limit=limit)

    return {
        "deliberations": deliberations,
        "count": len(deliberations)
    }


@api_app.get("/deliberations/{name}")
async def get_deliberation_detail(
    name: str,
    api_key_data: dict = Depends(validate_api_key_header)
):
    """
    Get a specific deliberation by name.

    Args:
        name: Deliberation directory name
        api_key_data: Validated API key data

    Returns:
        Complete deliberation data
    """
    logger.info(f"Getting deliberation {name}: {api_key_data.get('name')}")

    delib = get_deliberation(name)

    if not delib:
        raise HTTPException(status_code=404, detail="Deliberation not found")

    return delib


@api_app.post("/deliberations/search")
async def search_deliberations_endpoint(
    search: DeliberationSearch,
    api_key_data: dict = Depends(validate_api_key_header)
):
    """
    Search past deliberations by keyword.

    Args:
        search: Search parameters
        api_key_data: Validated API key data

    Returns:
        Matching deliberations
    """
    logger.info(f"Searching deliberations for '{search.query}': {api_key_data.get('name')}")

    results = search_deliberations(search.query, limit=search.limit)

    return {
        "results": results,
        "count": len(results),
        "query": search.query
    }


@api_app.get("/stats")
async def get_stats(api_key_data: dict = Depends(validate_api_key_header)):
    """
    Get API usage statistics.

    Args:
        api_key_data: Validated API key data

    Returns:
        Usage statistics
    """
    stats = get_api_stats()
    deliberations = list_deliberations(limit=1000)

    return {
        "api": stats,
        "deliberations": {
            "total": len(deliberations)
        }
    }


# MCP Tool Definitions
@api_app.get("/mcp/tools")
async def mcp_tools():
    """
    Get MCP tool definitions for this API.

    This endpoint returns tool definitions in the Model Context Protocol format,
    allowing AI assistants like Claude to discover and use the council as a tool.

    Returns:
        MCP tool definitions
    """
    return {
        "tools": [
            {
                "name": "consult_llm_council",
                "description": "Consult a council of multiple AI models (Claude Opus, DeepSeek R1, Mistral Large, Nova Premier) for diverse perspectives on complex questions. The council deliberates through 3 stages: individual responses, peer evaluation, and synthesis. Use this when you want multiple expert opinions or need to validate your thinking.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask the council"
                        },
                        "include_individual_responses": {
                            "type": "boolean",
                            "description": "Whether to include individual model responses (default: false)",
                            "default": False
                        }
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "search_council_deliberations",
                "description": "Search past council deliberations for historical context and previous wisdom on similar topics. Useful when the council has likely discussed a topic before.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keywords to find in past deliberations)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }
