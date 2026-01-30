#!/usr/bin/env python3
"""Manage API keys for LLM Council API."""

import sys
import os
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.api_keys import (
    create_api_key, list_api_keys, revoke_api_key, get_api_stats
)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")


def create_command():
    """Create a new API key."""
    print_header("Create New API Key")

    name = input("Key name (e.g., 'Claude Integration'): ").strip()
    if not name:
        print("Error: Name is required")
        return

    description = input("Description (optional): ").strip()

    rate_limit = input("Rate limit (requests per hour, default 100): ").strip()
    rate_limit = int(rate_limit) if rate_limit else 100

    print("\nCreating API key...")
    api_key = create_api_key(name, description, rate_limit=rate_limit)

    print_header("API Key Created Successfully!")
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Rate Limit: {rate_limit} requests/hour")
    print()
    print("⚠️  IMPORTANT: Save this key securely - it won't be shown again!")
    print()
    print(f"API Key: {api_key}")
    print()
    print("Use this key in API requests with the X-API-Key header:")
    print(f'  curl -H "X-API-Key: {api_key}" http://localhost:8001/api/v1/council/ask')
    print()


def list_command():
    """List all API keys."""
    print_header("API Keys")

    keys = list_api_keys()

    if not keys:
        print("No API keys found.")
        print("\nCreate one with: python manage_api_keys.py create")
        return

    for i, key in enumerate(keys, 1):
        status = "✓ ENABLED" if key["enabled"] else "✗ DISABLED"
        print(f"{i}. {key['name']} [{status}]")
        if key.get("description"):
            print(f"   Description: {key['description']}")
        print(f"   Created: {key['created_at']}")
        print(f"   Rate Limit: {key['rate_limit']} requests/hour")
        print(f"   Total Requests: {key['request_count']}")
        if key.get("last_used"):
            print(f"   Last Used: {key['last_used']}")
        print()


def revoke_command():
    """Revoke an API key."""
    print_header("Revoke API Key")

    keys = list_api_keys()

    if not keys:
        print("No API keys found.")
        return

    print("Available keys:")
    for i, key in enumerate(keys, 1):
        status = "ENABLED" if key["enabled"] else "DISABLED"
        print(f"{i}. {key['name']} [{status}]")

    print()
    name = input("Enter the name of the key to revoke: ").strip()

    if not name:
        print("Cancelled.")
        return

    confirm = input(f"Are you sure you want to revoke '{name}'? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Cancelled.")
        return

    if revoke_api_key(name):
        print(f"\n✓ API key '{name}' has been revoked.")
    else:
        print(f"\n✗ API key '{name}' not found.")


def stats_command():
    """Show API statistics."""
    print_header("API Statistics")

    stats = get_api_stats()

    print(f"Total API Keys: {stats['total_keys']}")
    print(f"  Enabled: {stats['enabled_keys']}")
    print(f"  Disabled: {stats['disabled_keys']}")
    print()
    print(f"Total API Requests: {stats['total_requests']}")


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("LLM Council API Key Manager")
        print()
        print("Usage:")
        print("  python manage_api_keys.py create    # Create a new API key")
        print("  python manage_api_keys.py list      # List all API keys")
        print("  python manage_api_keys.py revoke    # Revoke an API key")
        print("  python manage_api_keys.py stats     # Show usage statistics")
        print()
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        create_command()
    elif command == "list":
        list_command()
    elif command == "revoke":
        revoke_command()
    elif command == "stats":
        stats_command()
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: create, list, revoke, stats")
        sys.exit(1)


if __name__ == "__main__":
    main()
