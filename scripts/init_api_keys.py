"""Initialize API keys database for GitHub Actions workflow."""

import json
import hashlib
from pathlib import Path

# Read the API key from file
api_key = Path("test_api_key.txt").read_text().strip()

# Hash it
key_hash = hashlib.sha256(api_key.encode()).hexdigest()

# Create API keys database
api_keys_db = {
    "keys": {
        key_hash: {
            "name": "GitHub Actions",
            "description": "API key for GitHub Actions workflow",
            "created_at": "2026-01-30T00:00:00",
            "rate_limit": 100,
            "rate_window": 3600,
            "usage": {}
        }
    }
}

# Save to database
Path("data").mkdir(exist_ok=True)
with open("data/api_keys.json", "w") as f:
    json.dump(api_keys_db, f, indent=2)

print("[OK] API key added to database")
