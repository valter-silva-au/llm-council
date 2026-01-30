"""Amazon Bedrock API client for making LLM requests."""

import asyncio
import logging
import boto3
from typing import List, Dict, Any, Optional
from .config import AWS_REGION

logger = logging.getLogger("llm_council.bedrock")

# Models that support extended thinking
THINKING_MODELS = [
    "anthropic.claude-opus-4-5",
    "anthropic.claude-sonnet-4",
    "anthropic.claude-sonnet-4-5",
    "anthropic.claude-haiku-4-5",
    "anthropic.claude-3-7-sonnet",
    "us.anthropic.claude-opus-4-5",
    "us.anthropic.claude-sonnet-4",
    "us.anthropic.claude-sonnet-4-5",
    "us.anthropic.claude-haiku-4-5",
]

# Default thinking budget (tokens)
THINKING_BUDGET_TOKENS = 4000


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


def _supports_thinking(model: str) -> bool:
    """Check if model supports extended thinking."""
    model_lower = model.lower()
    for thinking_model in THINKING_MODELS:
        if thinking_model.lower() in model_lower:
            return True
    return False


def _sync_query_model(
    client,
    model: str,
    messages: List[Dict[str, str]],
    enable_thinking: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Synchronous model query (runs in thread pool).
    Enables extended thinking for supported Claude models.
    """
    try:
        # Log prompt size for debugging
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        estimated_tokens = total_chars // 4  # Rough estimate: 1 token ≈ 4 chars
        logger.debug(f"Model {model}: Prompt size ~{total_chars} chars (~{estimated_tokens} tokens)")

        bedrock_messages = _convert_messages_to_bedrock_format(messages)

        # Build request parameters
        request_params = {
            "modelId": model,
            "messages": bedrock_messages,
        }

        # Enable thinking for supported models
        if enable_thinking and _supports_thinking(model):
            logger.info(f"Enabling extended thinking for {model} (budget: {THINKING_BUDGET_TOKENS} tokens)")
            request_params["additionalModelRequestFields"] = {
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": THINKING_BUDGET_TOKENS
                }
            }
            # Extended thinking requires higher max_tokens
            request_params["inferenceConfig"] = {
                "maxTokens": 16000
            }
        else:
            # For non-thinking models (like Nova), ensure adequate max tokens
            request_params["inferenceConfig"] = {
                "maxTokens": 8000
            }

        response = client.converse(**request_params)

        # Extract content from Bedrock response
        output_message = response.get('output', {}).get('message', {})
        content_list = output_message.get('content', [])

        # Bedrock returns content as a list of blocks
        content_text = ''
        thinking_text = ''
        for block in content_list:
            if 'text' in block:
                content_text += block['text']
            # Capture thinking blocks if present
            if 'thinking' in block:
                thinking_text += block.get('thinking', '')

        if thinking_text:
            logger.debug(f"Model {model} used extended thinking ({len(thinking_text)} chars)")

        return {
            'content': content_text,
            'reasoning_details': thinking_text if thinking_text else None
        }

    except Exception as e:
        error_str = str(e)
        # If thinking fails, retry without it
        if enable_thinking and ('thinking' in error_str.lower() or 'validation' in error_str.lower()):
            logger.warning(f"Extended thinking not supported for {model}, retrying without it")
            return _sync_query_model(client, model, messages, enable_thinking=False)

        # Log detailed error information
        logger.error(f"Error querying Bedrock model {model}: {e}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"Response metadata: {e.response.get('ResponseMetadata', {})}")
            logger.error(f"Error code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            logger.error(f"Error message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
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
