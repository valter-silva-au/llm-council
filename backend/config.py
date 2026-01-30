"""Configuration for the LLM Council."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env.dev if it exists, otherwise fall back to .env
env_dev = Path(__file__).parent.parent / ".env.dev"
if env_dev.exists():
    load_dotenv(env_dev, override=True)
else:
    load_dotenv(override=True)

# Explicitly set AWS credentials as environment variables for boto3
# This ensures boto3 uses these credentials even when running as a daemon
if os.getenv("AWS_ACCESS_KEY_ID"):
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
if os.getenv("AWS_SECRET_ACCESS_KEY"):
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
if os.getenv("AWS_SESSION_TOKEN"):
    os.environ["AWS_SESSION_TOKEN"] = os.getenv("AWS_SESSION_TOKEN")

# Logging configuration
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("llm_council")

# API Provider selection: "openrouter" or "bedrock"
API_PROVIDER = os.getenv("API_PROVIDER", "openrouter")

# Web Search configuration - Multiple providers with fallback
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Enable web search if ANY provider has a key
ENABLE_WEB_SEARCH = any([TAVILY_API_KEY, SERPER_API_KEY, BRAVE_API_KEY, SERPAPI_API_KEY])

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# OpenRouter council members
OPENROUTER_COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]
OPENROUTER_CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
OPENROUTER_TITLE_MODEL = "google/gemini-2.5-flash"  # Fast model for title generation

# Amazon Bedrock configuration
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

# Bedrock council members - HEAVYWEIGHT configuration (Jan 2026)
# Recommended by Gemini for maximum reasoning power
BEDROCK_COUNCIL_MODELS = [
    "us.anthropic.claude-opus-4-5-20251101-v1:0",  # The Lead Thinker - SOTA generalist
    "us.deepseek.r1-v1:0",                          # The Critic - Deep reasoning/CoT
    "mistral.mistral-large-2407-v1:0",              # The Specialist - Open-weight powerhouse
    "us.amazon.nova-premier-v1:0",                  # The Orchestrator - Complex synthesis
]
# Chairman: Nova Premier excels at aggregating diverse perspectives
BEDROCK_CHAIRMAN_MODEL = "us.amazon.nova-premier-v1:0"
BEDROCK_TITLE_MODEL = "us.amazon.nova-lite-v1:0"  # Fast model for title generation

# Active configuration based on provider
if API_PROVIDER == "bedrock":
    COUNCIL_MODELS = BEDROCK_COUNCIL_MODELS
    CHAIRMAN_MODEL = BEDROCK_CHAIRMAN_MODEL
    TITLE_MODEL = BEDROCK_TITLE_MODEL
else:
    COUNCIL_MODELS = OPENROUTER_COUNCIL_MODELS
    CHAIRMAN_MODEL = OPENROUTER_CHAIRMAN_MODEL
    TITLE_MODEL = OPENROUTER_TITLE_MODEL

# Data directory for conversation storage
DATA_DIR = "data/conversations"
