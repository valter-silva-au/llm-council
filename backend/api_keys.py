"""API key management for LLM Council API."""

import secrets
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("llm_council.api_keys")

# API keys storage
API_KEYS_FILE = Path(__file__).parent.parent / "data" / "api_keys.json"


def generate_api_key() -> str:
    """
    Generate a secure API key.

    Returns:
        A new API key in format: llmc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    # Generate 32 random bytes, encode as hex
    key_bytes = secrets.token_bytes(32)
    key_hex = key_bytes.hex()
    return f"llmc_{key_hex}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.

    Args:
        api_key: The API key to hash

    Returns:
        SHA256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def load_api_keys() -> Dict[str, Any]:
    """
    Load API keys from storage.

    Returns:
        Dict mapping key hash to key metadata
    """
    if not API_KEYS_FILE.exists():
        return {}

    try:
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return {}


def save_api_keys(keys: Dict[str, Any]):
    """
    Save API keys to storage.

    Args:
        keys: Dict mapping key hash to key metadata
    """
    API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)


def create_api_key(
    name: str,
    description: str = "",
    rate_limit: int = 100,
    rate_window: int = 3600
) -> str:
    """
    Create a new API key.

    Args:
        name: Name/identifier for this key (e.g., "Claude Integration")
        description: Optional description
        rate_limit: Number of requests allowed per rate_window
        rate_window: Time window in seconds (default: 1 hour)

    Returns:
        The new API key (only returned once!)
    """
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    keys = load_api_keys()

    keys[key_hash] = {
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "rate_limit": rate_limit,
        "rate_window": rate_window,
        "request_count": 0,
        "last_used": None,
        "enabled": True
    }

    save_api_keys(keys)

    logger.info(f"Created API key: {name}")
    return api_key


def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Validate an API key and return its metadata.

    Args:
        api_key: The API key to validate

    Returns:
        Key metadata if valid, None if invalid
    """
    if not api_key or not api_key.startswith("llmc_"):
        return None

    key_hash = hash_api_key(api_key)
    keys = load_api_keys()

    key_data = keys.get(key_hash)

    if not key_data:
        logger.warning("Invalid API key attempt")
        return None

    if not key_data.get("enabled", True):
        logger.warning(f"Disabled API key used: {key_data.get('name')}")
        return None

    return key_data


def record_api_usage(api_key: str) -> bool:
    """
    Record usage of an API key and check rate limits.

    Args:
        api_key: The API key

    Returns:
        True if within rate limit, False if limit exceeded
    """
    key_hash = hash_api_key(api_key)
    keys = load_api_keys()

    key_data = keys.get(key_hash)
    if not key_data:
        return False

    # Update usage
    key_data["last_used"] = datetime.now().isoformat()
    key_data["request_count"] = key_data.get("request_count", 0) + 1

    # Simple rate limiting (would use Redis in production)
    # For now, just track total count
    # TODO: Implement proper time-window based rate limiting

    keys[key_hash] = key_data
    save_api_keys(keys)

    return True


def list_api_keys() -> List[Dict[str, Any]]:
    """
    List all API keys (without revealing actual keys).

    Returns:
        List of key metadata
    """
    keys = load_api_keys()

    return [
        {
            "name": data["name"],
            "description": data.get("description", ""),
            "created_at": data["created_at"],
            "rate_limit": data.get("rate_limit", 100),
            "request_count": data.get("request_count", 0),
            "last_used": data.get("last_used"),
            "enabled": data.get("enabled", True)
        }
        for data in keys.values()
    ]


def revoke_api_key(name: str) -> bool:
    """
    Revoke (disable) an API key by name.

    Args:
        name: Name of the key to revoke

    Returns:
        True if key was found and revoked
    """
    keys = load_api_keys()

    for key_hash, data in keys.items():
        if data["name"] == name:
            data["enabled"] = False
            keys[key_hash] = data
            save_api_keys(keys)
            logger.info(f"Revoked API key: {name}")
            return True

    return False


def get_api_stats() -> Dict[str, Any]:
    """
    Get statistics about API usage.

    Returns:
        Dict with usage stats
    """
    keys = load_api_keys()

    total_keys = len(keys)
    enabled_keys = sum(1 for k in keys.values() if k.get("enabled", True))
    total_requests = sum(k.get("request_count", 0) for k in keys.values())

    return {
        "total_keys": total_keys,
        "enabled_keys": enabled_keys,
        "disabled_keys": total_keys - enabled_keys,
        "total_requests": total_requests
    }
