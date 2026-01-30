"""Tavily API client for web search."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from .config import TAVILY_API_KEY

logger = logging.getLogger("llm_council.tavily")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def search_web(
    query: str,
    max_results: int = 5,
    search_depth: str = "advanced",
    include_answer: bool = True,
    include_raw_content: bool = False,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """
    Search the web using Tavily API.

    Args:
        query: The search query
        max_results: Maximum number of results to return
        search_depth: "basic" or "advanced" (more thorough)
        include_answer: Whether to include AI-generated answer
        include_raw_content: Whether to include raw page content
        timeout: Request timeout in seconds

    Returns:
        Dict with 'answer' and 'results' list, or None if failed
    """
    if not TAVILY_API_KEY:
        logger.warning("Tavily API key not configured, skipping web search")
        return None

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
    }

    logger.info(f"Searching web for: {query[:100]}...")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(TAVILY_SEARCH_URL, json=payload)
            response.raise_for_status()

            data = response.json()

            results_count = len(data.get("results", []))
            logger.info(f"Tavily returned {results_count} results")

            return {
                "answer": data.get("answer"),
                "results": data.get("results", []),
                "query": query
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily HTTP error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Tavily search error: {e}", exc_info=True)
        return None


def format_search_results(search_data: Dict[str, Any]) -> str:
    """
    Format Tavily search results into a context string for LLMs.

    Args:
        search_data: The search response from Tavily

    Returns:
        Formatted string with search results
    """
    if not search_data:
        return ""

    parts = ["## Web Search Results\n"]

    # Include Tavily's AI-generated answer if available
    if search_data.get("answer"):
        parts.append(f"**Summary:** {search_data['answer']}\n")

    parts.append("\n**Sources:**\n")

    # Format individual results
    for i, result in enumerate(search_data.get("results", []), 1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")

        # Truncate content if too long
        if len(content) > 500:
            content = content[:500] + "..."

        parts.append(f"\n{i}. **{title}**")
        parts.append(f"   URL: {url}")
        parts.append(f"   {content}\n")

    return "\n".join(parts)
