"""OpenRouter API client for making LLM requests."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL

logger = logging.getLogger("llm_council.openrouter")

# Enable web search for real-time information
ENABLE_WEB_SEARCH = True

# Models that support extended thinking/reasoning
REASONING_MODELS = [
    "anthropic/claude",  # Claude models support thinking
    "openai/o1",         # O1 models have built-in reasoning
    "openai/o3",         # O3 models have built-in reasoning
    "deepseek/deepseek-r1",  # DeepSeek R1 has CoT
    "google/gemini-2.5-pro",  # Gemini 2.5 has thinking
]


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenRouter API.

    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    # Enable web search for real-time information
    if ENABLE_WEB_SEARCH:
        payload["plugins"] = {
            "web_search": {
                "enabled": True
            }
        }
        logger.debug(f"Web search enabled for {model}")

    # Check if model supports extended reasoning
    model_lower = model.lower()
    supports_reasoning = any(rm in model_lower for rm in REASONING_MODELS)
    if supports_reasoning:
        logger.debug(f"Model {model} supports extended reasoning")

    logger.debug(f"Querying OpenRouter model: {model} with {len(messages)} messages")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            content = message.get('content', '')
            logger.debug(f"OpenRouter model {model} responded ({len(content)} chars)")

            return {
                'content': content,
                'reasoning_details': message.get('reasoning_details')
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error querying model {model}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Error querying model {model}: {e}", exc_info=True)
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
