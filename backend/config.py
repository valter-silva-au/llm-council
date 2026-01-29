"""Configuration for the LLM Council."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

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

# Active configuration based on provider
if API_PROVIDER == "bedrock":
    COUNCIL_MODELS = BEDROCK_COUNCIL_MODELS
    CHAIRMAN_MODEL = BEDROCK_CHAIRMAN_MODEL
else:
    COUNCIL_MODELS = OPENROUTER_COUNCIL_MODELS
    CHAIRMAN_MODEL = OPENROUTER_CHAIRMAN_MODEL

# Data directory for conversation storage
DATA_DIR = "data/conversations"
