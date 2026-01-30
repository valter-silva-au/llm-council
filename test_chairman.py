#!/usr/bin/env python3
"""Test script to diagnose Chairman model issues."""

import asyncio
import sys
import logging
from backend.config import CHAIRMAN_MODEL, API_PROVIDER

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

async def test_chairman():
    """Test the Chairman model directly."""
    print("🔍 Testing Chairman Model")
    print("=" * 60)
    print(f"API Provider: {API_PROVIDER}")
    print(f"Chairman Model: {CHAIRMAN_MODEL}")
    print("=" * 60)

    # Import the appropriate query function
    if API_PROVIDER == "bedrock":
        from backend.bedrock import query_model
    else:
        from backend.openrouter import query_model

    # Simple test message
    test_messages = [
        {"role": "user", "content": "Hello! Please respond with a brief greeting."}
    ]

    print("\n📤 Sending test message to Chairman...")
    print("-" * 60)

    try:
        response = await query_model(CHAIRMAN_MODEL, test_messages, timeout=60.0)

        if response is None:
            print("\n❌ FAILED! Chairman returned None")
            print("\nPossible causes:")
            print("  1. Model identifier is incorrect")
            print("  2. AWS credentials not configured")
            print("  3. Model not available in your region")
            print("  4. Insufficient permissions")
            print("  5. Bedrock quota exceeded")
            print("\nCheck the logs above for detailed error messages.")
            return False
        else:
            content = response.get('content', '')
            print(f"\n✅ SUCCESS! Chairman responded")
            print(f"Response length: {len(content)} chars")
            print("-" * 60)
            print("Response preview:")
            print(content[:500])
            if len(content) > 500:
                print("...")
            return True

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_alternative_chairman():
    """Test with an alternative Nova model."""
    print("\n" + "=" * 60)
    print("🔧 Testing Alternative Chairman Model")
    print("=" * 60)

    alternative_model = "us.amazon.nova-lite-v1:0"
    print(f"Trying: {alternative_model}")
    print("-" * 60)

    if API_PROVIDER == "bedrock":
        from backend.bedrock import query_model
    else:
        from backend.openrouter import query_model

    test_messages = [
        {"role": "user", "content": "Hello! Please respond with a brief greeting."}
    ]

    try:
        response = await query_model(alternative_model, test_messages, timeout=60.0)

        if response is None:
            print("\n❌ Alternative model also failed")
            return False
        else:
            content = response.get('content', '')
            print(f"\n✅ Alternative model works!")
            print(f"Response: {content[:200]}")
            print("\n💡 Consider switching BEDROCK_CHAIRMAN_MODEL to this model in config.py")
            return True

    except Exception as e:
        print(f"\n❌ Alternative model exception: {e}")
        return False


async def main():
    """Main entry point."""
    try:
        success = await test_chairman()

        if not success:
            print("\n" + "=" * 60)
            print("Attempting alternative model test...")
            await test_alternative_chairman()

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
