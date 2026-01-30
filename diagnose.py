#!/usr/bin/env python3
"""Comprehensive diagnostic for LLM Council issues."""

import sys
import os
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*60)
print("LLM COUNCIL DIAGNOSTIC")
print("="*60)

# 1. Check Python version and location
print(f"\n1. Python Info:")
print(f"   Version: {sys.version}")
print(f"   Executable: {sys.executable}")

# 2. Check working directory
print(f"\n2. Working Directory:")
print(f"   {os.getcwd()}")

# 3. Check if backend imports
print(f"\n3. Testing Backend Imports:")
try:
    from backend.config import (
        ENABLE_WEB_SEARCH, TAVILY_API_KEY, BRAVE_API_KEY,
        COUNCIL_MODELS, CHAIRMAN_MODEL
    )
    print(f"   ✓ config.py imported")
    print(f"   - ENABLE_WEB_SEARCH: {ENABLE_WEB_SEARCH}")
    print(f"   - TAVILY_API_KEY: {'SET' if TAVILY_API_KEY else 'NOT SET'}")
    print(f"   - BRAVE_API_KEY: {'SET' if BRAVE_API_KEY else 'NOT SET'}")
    print(f"   - Models: {len(COUNCIL_MODELS)}")
    print(f"   - Chairman: {CHAIRMAN_MODEL}")
except Exception as e:
    print(f"   ✗ ERROR importing config: {e}")
    sys.exit(1)

try:
    from backend.search_providers import search_with_fallback, SearchProvider, SearchProviderConfig
    print(f"   ✓ search_providers.py imported")
except Exception as e:
    print(f"   ✗ ERROR importing search_providers: {e}")
    sys.exit(1)

try:
    from backend.council import perform_web_search, run_full_council
    print(f"   ✓ council.py imported")
except Exception as e:
    print(f"   ✗ ERROR importing council: {e}")
    sys.exit(1)

# 4. Check if [SEARCH] logging is in the code
print(f"\n4. Checking Code Content:")
import inspect
council_source = inspect.getsource(perform_web_search)
if "[SEARCH]" in council_source:
    print(f"   ✓ [SEARCH] logging found in perform_web_search")
else:
    print(f"   ✗ [SEARCH] logging NOT found in perform_web_search")
    print(f"   WARNING: Code might not be updated!")

# 5. Test web search directly
print(f"\n5. Testing Web Search:")
import asyncio

async def test_search():
    try:
        result = await perform_web_search("test query")
        if result:
            print(f"   ✓ Web search works! Returned {len(result)} chars")
        else:
            print(f"   ⚠ Web search returned None (might be disabled or failed)")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_search())

# 6. Check AWS credentials
print(f"\n6. AWS Credentials:")
try:
    import boto3
    from backend.config import AWS_REGION
    client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
    print(f"   ✓ Boto3 client created for region: {AWS_REGION}")

    # Try a simple call
    try:
        response = client.list_foundation_models()
        print(f"   ✓ AWS credentials VALID (can list models)")
    except Exception as e:
        if "AccessDenied" in str(e) or "Authentication" in str(e):
            print(f"   ✗ AWS credentials EXPIRED or INVALID")
            print(f"      Error: {str(e)[:100]}")
        else:
            print(f"   ⚠ Unexpected error: {str(e)[:100]}")
except Exception as e:
    print(f"   ✗ ERROR with boto3: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
