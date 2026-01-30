#!/usr/bin/env python3
"""Test script for web search providers."""

import asyncio
import sys
from backend.config import TAVILY_API_KEY, SERPER_API_KEY, BRAVE_API_KEY, SERPAPI_API_KEY

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from backend.search_providers import (
    search_with_fallback,
    format_search_results,
    SearchProvider,
    SearchProviderConfig
)


async def test_search():
    """Test web search with all configured providers."""
    from pathlib import Path

    print("🔍 Testing Web Search Providers")
    print("=" * 60)

    # Show which env file is being used
    env_dev = Path(__file__).parent / ".env.dev"
    env_file = Path(__file__).parent / ".env"
    if env_dev.exists():
        print(f"📄 Using environment file: .env.dev")
    elif env_file.exists():
        print(f"📄 Using environment file: .env")
    else:
        print(f"⚠️  No environment file found (.env.dev or .env)")
    print("=" * 60)

    # Configure providers
    providers = [
        SearchProviderConfig(SearchProvider.TAVILY, TAVILY_API_KEY),
        SearchProviderConfig(SearchProvider.SERPER, SERPER_API_KEY),
        SearchProviderConfig(SearchProvider.BRAVE, BRAVE_API_KEY),
        SearchProviderConfig(SearchProvider.SERPAPI, SERPAPI_API_KEY),
    ]

    # Show configured providers
    print("\n📋 Configured Providers:")
    enabled_providers = [p for p in providers if p.enabled]
    if not enabled_providers:
        print("❌ No search providers configured!")
        print("\nTo enable web search, add at least one API key to your .env file:")
        print("  - TAVILY_API_KEY")
        print("  - SERPER_API_KEY")
        print("  - BRAVE_API_KEY")
        print("  - SERPAPI_API_KEY")
        print("\nSee .env.example for details.")
        return False

    for provider in enabled_providers:
        print(f"  ✓ {provider.provider.value}")

    # Test query
    query = "latest AI developments 2026"
    print(f"\n🔎 Testing with query: '{query}'")
    print("-" * 60)

    # Perform search
    result = await search_with_fallback(providers, query, max_results=3)

    if result:
        provider = result.get("provider", "unknown")
        results_count = len(result.get("results", []))

        print(f"\n✅ SUCCESS! Got {results_count} results from {provider}")
        print("\n" + "=" * 60)
        print("📄 Formatted Results:")
        print("=" * 60)
        formatted = format_search_results(result)
        print(formatted)
        return True
    else:
        print("\n❌ FAILED! All providers failed or returned no results.")
        print("\nTroubleshooting:")
        print("  1. Verify your API keys are valid")
        print("  2. Check your internet connection")
        print("  3. Ensure you have remaining API credits")
        print("  4. Check backend logs for detailed error messages")
        return False


async def main():
    """Main entry point."""
    try:
        success = await test_search()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
