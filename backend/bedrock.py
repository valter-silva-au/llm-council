"""Amazon Bedrock API client for making LLM requests."""

import asyncio
import logging
import boto3
from typing import List, Dict, Any, Optional
from .config import AWS_REGION

logger = logging.getLogger("llm_council.bedrock")


def _get_bedrock_client():
    """Create a Bedrock Runtime client."""
    return boto3.client(
        'bedrock-runtime',
        region_name=AWS_REGION
    )


def _convert_messages_to_bedrock_format(messages: List[Dict[str, str]]) -> List[Dict]:
    """
    Convert OpenAI-style messages to Bedrock Converse format.

    OpenAI format: [{"role": "user", "content": "Hello"}]
    Bedrock format: [{"role": "user", "content": [{"text": "Hello"}]}]
    """
    bedrock_messages = []
    for msg in messages:
        bedrock_messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })
    return bedrock_messages


def _sync_query_model(
    client,
    model: str,
    messages: List[Dict[str, str]]
) -> Optional[Dict[str, Any]]:
    """
    Synchronous model query (runs in thread pool).
    """
    try:
        bedrock_messages = _convert_messages_to_bedrock_format(messages)

        response = client.converse(
            modelId=model,
            messages=bedrock_messages
        )

        # Extract content from Bedrock response
        output_message = response.get('output', {}).get('message', {})
        content_list = output_message.get('content', [])

        # Bedrock returns content as a list of blocks
        content_text = ''
        for block in content_list:
            if 'text' in block:
                content_text += block['text']

        return {
            'content': content_text,
            'reasoning_details': None  # Bedrock doesn't have this field
        }

    except Exception as e:
        logger.error(f"Error querying Bedrock model {model}: {e}", exc_info=True)
        return None


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via Amazon Bedrock Converse API.

    Args:
        model: Bedrock model identifier (e.g., "us.amazon.nova-pro-v1:0")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds (not used directly, Bedrock has its own)

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    client = _get_bedrock_client()
    logger.debug(f"Querying Bedrock model: {model} with {len(messages)} messages")

    # Run synchronous boto3 call in thread pool
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_sync_query_model, client, model, messages),
            timeout=timeout
        )
        if result:
            logger.debug(f"Bedrock model {model} responded ({len(result.get('content', ''))} chars)")
        else:
            logger.warning(f"Bedrock model {model} returned None")
        return result
    except asyncio.TimeoutError:
        logger.error(f"Timeout querying Bedrock model {model} after {timeout}s")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of Bedrock model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
