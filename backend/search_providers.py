"""Multi-provider web search with automatic fallback."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger("llm_council.search")


class SearchProvider(Enum):
    """Available search providers."""
    TAVILY = "tavily"
    SERPER = "serper"
    BRAVE = "brave"
    SERPAPI = "serpapi"


class SearchProviderConfig:
    """Configuration for a search provider."""
    def __init__(self, provider: SearchProvider, api_key: Optional[str], enabled: bool = True):
        self.provider = provider
        self.api_key = api_key
        self.enabled = enabled and api_key is not None

    def __repr__(self):
        return f"SearchProviderConfig({self.provider.value}, enabled={self.enabled})"


async def search_tavily(
    api_key: str,
    query: str,
    max_results: int = 5,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """Search using Tavily API."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                "answer": data.get("answer"),
                "results": data.get("results", []),
                "query": query,
                "provider": "tavily"
            }
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return None


async def search_serper(
    api_key: str,
    query: str,
    max_results: int = 5,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """Search using Serper API (Google Search)."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": max_results
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Convert Serper format to common format
            results = []
            for item in data.get("organic", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "content": item.get("snippet", "")
                })

            # Try to extract answer from knowledge graph or answer box
            answer = None
            if "answerBox" in data:
                answer = data["answerBox"].get("answer") or data["answerBox"].get("snippet")
            elif "knowledgeGraph" in data:
                answer = data["knowledgeGraph"].get("description")

            return {
                "answer": answer,
                "results": results,
                "query": query,
                "provider": "serper"
            }
    except Exception as e:
        logger.error(f"Serper search failed: {e}")
        return None


async def search_brave(
    api_key: str,
    query: str,
    max_results: int = 5,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """Search using Brave Search API."""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": max_results
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert Brave format to common format
            results = []
            for item in data.get("web", {}).get("results", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("description", "")
                })

            return {
                "answer": None,  # Brave doesn't provide AI answers
                "results": results,
                "query": query,
                "provider": "brave"
            }
    except Exception as e:
        logger.error(f"Brave search failed: {e}")
        return None


async def search_serpapi(
    api_key: str,
    query: str,
    max_results: int = 5,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """Search using SerpAPI (Google Search)."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "num": max_results,
        "engine": "google"
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert SerpAPI format to common format
            results = []
            for item in data.get("organic_results", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "content": item.get("snippet", "")
                })

            # Try to extract answer
            answer = None
            if "answer_box" in data:
                answer = data["answer_box"].get("answer") or data["answer_box"].get("snippet")
            elif "knowledge_graph" in data:
                answer = data["knowledge_graph"].get("description")

            return {
                "answer": answer,
                "results": results,
                "query": query,
                "provider": "serpapi"
            }
    except Exception as e:
        logger.error(f"SerpAPI search failed: {e}")
        return None


async def search_with_fallback(
    providers: List[SearchProviderConfig],
    query: str,
    max_results: int = 5,
    timeout: float = 30.0
) -> Optional[Dict[str, Any]]:
    """
    Try multiple search providers until one succeeds.

    Args:
        providers: List of provider configurations to try
        query: The search query
        max_results: Maximum number of results to return
        timeout: Request timeout in seconds

    Returns:
        Dict with search results, or None if all providers failed
    """
    if not providers:
        logger.warning("No search providers configured")
        return None

    enabled_providers = [p for p in providers if p.enabled]
    if not enabled_providers:
        logger.warning("No enabled search providers found")
        return None

    logger.info(f"Attempting search with {len(enabled_providers)} providers: {[p.provider.value for p in enabled_providers]}")

    for provider_config in enabled_providers:
        provider = provider_config.provider
        api_key = provider_config.api_key

        logger.info(f"Trying {provider.value}...")

        try:
            if provider == SearchProvider.TAVILY:
                result = await search_tavily(api_key, query, max_results, timeout)
            elif provider == SearchProvider.SERPER:
                result = await search_serper(api_key, query, max_results, timeout)
            elif provider == SearchProvider.BRAVE:
                result = await search_brave(api_key, query, max_results, timeout)
            elif provider == SearchProvider.SERPAPI:
                result = await search_serpapi(api_key, query, max_results, timeout)
            else:
                logger.warning(f"Unknown provider: {provider}")
                continue

            if result and result.get("results"):
                logger.info(f"✓ {provider.value} returned {len(result['results'])} results")
                return result
            else:
                logger.warning(f"✗ {provider.value} returned no results")

        except Exception as e:
            logger.error(f"✗ {provider.value} failed: {e}")
            continue

    logger.error("All search providers failed")
    return None


def format_search_results(search_data: Dict[str, Any]) -> str:
    """
    Format search results into a context string for LLMs.

    Args:
        search_data: The search response from any provider

    Returns:
        Formatted string with search results
    """
    if not search_data:
        return ""

    parts = ["## Web Search Results\n"]

    provider = search_data.get("provider", "unknown")
    parts.append(f"*Source: {provider}*\n")

    # Include AI-generated answer if available
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
