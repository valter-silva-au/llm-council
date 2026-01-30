#!/bin/bash
# Script to add secrets from .env file to GitHub repository
# Usage: ./add_github_secrets.sh

REPO="valter-silva-au/llm-council"

echo "Adding secrets to GitHub repository: $REPO"
echo "=========================================="
echo ""

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed"
    echo "Install with: brew install gh (Mac) or apt install gh (Linux)"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI is not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    echo "Create a .env file with your credentials first"
    exit 1
fi

echo "Reading credentials from .env file..."
echo ""

# Source the .env file (this loads variables into the environment)
set -a
source .env
set +a

# Function to add secret
add_secret() {
    local name=$1
    local value=$2

    if [ -n "$value" ]; then
        echo "  Adding: $name"
        if gh secret set "$name" --body "$value" --repo "$REPO" 2>/dev/null; then
            echo "    ✓ Success"
        else
            echo "    ✗ Failed"
        fi
    else
        echo "  Skipping: $name (not found in .env)"
    fi
}

echo "Adding secrets from .env..."
echo ""

# AWS Bedrock
add_secret "API_PROVIDER" "$API_PROVIDER"
add_secret "AWS_REGION" "$AWS_REGION"
add_secret "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID"
add_secret "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY"
add_secret "AWS_SESSION_TOKEN" "$AWS_SESSION_TOKEN"
add_secret "AWS_BEARER_TOKEN_BEDROCK" "$AWS_BEARER_TOKEN_BEDROCK"

# Web Search
add_secret "TAVILY_API_KEY" "$TAVILY_API_KEY"
add_secret "BRAVE_API_KEY" "$BRAVE_API_KEY"

# YouTube
add_secret "YOUTUBE_CLIENT_ID" "$YOUTUBE_CLIENT_ID"
add_secret "YOUTUBE_CLIENT_SECRET" "$YOUTUBE_CLIENT_SECRET"

# Other APIs
add_secret "GOOGLE_AI_API_KEY" "$GOOGLE_AI_API_KEY"
add_secret "PERPLEXITY_API_KEY" "$PERPLEXITY_API_KEY"
add_secret "FIRECRAWL_API_KEY" "$FIRECRAWL_API_KEY"
add_secret "JINA_API_KEY" "$JINA_API_KEY"
add_secret "KAGI_API_KEY" "$KAGI_API_KEY"
add_secret "OPENWEATHER_API_KEY" "$OPENWEATHER_API_KEY"

echo ""
echo "Adding Council API key..."
if [ -f "test_api_key.txt" ]; then
    COUNCIL_KEY=$(cat test_api_key.txt | tr -d '\n')
    if [ -n "$COUNCIL_KEY" ]; then
        add_secret "COUNCIL_API_KEY" "$COUNCIL_KEY"
    fi
else
    echo "⚠ test_api_key.txt not found. Generate with: python manage_api_keys.py"
fi

echo ""
echo "=========================================="
echo "✓ Secrets added successfully!"
echo ""
echo "Verify secrets at:"
echo "https://github.com/$REPO/settings/secrets/actions"
