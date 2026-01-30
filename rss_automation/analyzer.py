"""Council-powered article analyzer."""

import logging
import httpx
import asyncio
from typing import Dict, Any, List
from pathlib import Path

from .config import ANALYSIS_QUESTIONS, API_URL, API_KEY_FILE

logger = logging.getLogger("intelligence_hub.analyzer")


async def read_api_key() -> str:
    """Read API key from file."""
    key_file = Path(__file__).parent.parent / API_KEY_FILE

    if not key_file.exists():
        raise FileNotFoundError(f"API key file not found: {key_file}")

    with open(key_file, 'r') as f:
        return f.read().strip()


async def analyze_article(article: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Analyze a single article using the council.

    Args:
        article: Article dictionary
        api_key: API key for authentication

    Returns:
        Analysis results including consensus metrics
    """
    logger.info(f"Analyzing: {article['title'][:60]}...")

    # Build analysis question
    question = f"""Analyze this article and provide insights:

**Title:** {article['title']}

**Source:** {article['source']}

**Summary:**
{article['summary']}

**Link:** {article['link']}

---

Please answer these questions:

1. {ANALYSIS_QUESTIONS[0]}

2. {ANALYSIS_QUESTIONS[1]}

3. {ANALYSIS_QUESTIONS[2]}

4. {article['domain_question']} (Domain-specific question for {article['category']})

---

Please provide clear, structured answers for each question."""

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{API_URL}/council/ask",
                headers={"X-API-Key": api_key},
                json={
                    "question": question,
                    "include_web_search": True,  # Use web search for current context
                    "include_stage1": True,  # Get individual model responses
                }
            )

            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                logger.error(response.text)
                return None

            result = response.json()

            # Extract analysis
            analysis = {
                "article_id": article["id"],
                "article_title": article["title"],
                "article_link": article["link"],
                "article_source": article["source"],
                "article_category": article["category"],
                "article_published": article["published"],
                "analysis": result["answer"],
                "chairman": result["chairman"],
                "models_participated": result["models_participated"],
                "deliberation_path": result.get("deliberation_path"),
                "individual_responses": result.get("stage1", []),
                "consensus_metrics": calculate_consensus(result.get("stage1", [])),
                "timestamp": article["published"]
            }

            logger.info(f"[OK] Analysis complete - {result['models_participated']} models participated")
            return analysis

    except Exception as e:
        logger.error(f"Error analyzing article: {e}", exc_info=True)
        return None


def calculate_consensus(stage1_responses: List[Dict]) -> Dict[str, Any]:
    """
    Calculate consensus metrics from individual model responses.

    Args:
        stage1_responses: List of individual model responses

    Returns:
        Consensus metrics
    """
    if not stage1_responses:
        return {"agreement_level": "unknown", "models_count": 0}

    # Simple consensus: count models (could be enhanced with similarity analysis)
    models_count = len(stage1_responses)

    # In a more sophisticated version, we could:
    # - Analyze semantic similarity between responses
    # - Identify points of agreement vs disagreement
    # - Calculate confidence scores

    return {
        "agreement_level": "strong" if models_count >= 3 else "moderate",
        "models_count": models_count,
        "perspectives_available": True
    }


async def analyze_articles_batch(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple articles using the council.

    Args:
        articles: List of article dictionaries

    Returns:
        List of analysis results
    """
    logger.info(f"Starting batch analysis of {len(articles)} articles...")

    api_key = await read_api_key()

    analyses = []

    for i, article in enumerate(articles, 1):
        logger.info(f"Article {i}/{len(articles)}")

        analysis = await analyze_article(article, api_key)

        if analysis:
            analyses.append(analysis)
        else:
            logger.warning(f"Skipping article due to analysis failure: {article['title']}")

        # Small delay between requests to be respectful
        if i < len(articles):
            await asyncio.sleep(2)

    logger.info(f"Batch complete: {len(analyses)}/{len(articles)} successful")
    return analyses
