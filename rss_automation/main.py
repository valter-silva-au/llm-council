"""Main orchestrator for RSS automation pipeline."""

import asyncio
import logging
import sys
from pathlib import Path

from .config import RSS_FEEDS, DAILY_ARTICLE_LIMIT
from .fetcher import (
    fetch_all_feeds,
    filter_recent_articles,
    deduplicate_articles,
    rank_articles,
    select_top_articles
)
from .analyzer import analyze_articles_batch
from .publisher import publish_analyses

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("rss_automation.log")
    ]
)

logger = logging.getLogger("intelligence_hub")


async def run_daily_digest():
    """
    Run the complete daily digest pipeline.

    Steps:
    1. Fetch articles from all RSS feeds
    2. Filter to recent articles (last 24 hours)
    3. Deduplicate and rank
    4. Select top N articles
    5. Analyze with council
    6. Publish to Jekyll site
    """
    logger.info("=" * 60)
    logger.info("Starting Daily Intelligence Hub Digest")
    logger.info("=" * 60)

    try:
        # Step 1: Fetch all articles
        logger.info("\n[1/6] Fetching RSS feeds...")
        articles = fetch_all_feeds(RSS_FEEDS)

        if not articles:
            logger.error("No articles fetched. Exiting.")
            return False

        # Step 2: Filter to recent articles
        logger.info("\n[2/6] Filtering to recent articles...")
        recent_articles = filter_recent_articles(articles, hours=24)

        if not recent_articles:
            logger.warning("No recent articles found. Trying last 48 hours...")
            recent_articles = filter_recent_articles(articles, hours=48)

        if not recent_articles:
            logger.error("No articles found in last 48 hours. Exiting.")
            return False

        # Step 3: Deduplicate
        logger.info("\n[3/6] Deduplicating articles...")
        unique_articles = deduplicate_articles(recent_articles)

        # Step 4: Rank and select top articles
        logger.info("\n[4/6] Ranking and selecting top articles...")
        ranked_articles = rank_articles(unique_articles)
        selected_articles = select_top_articles(ranked_articles, limit=DAILY_ARTICLE_LIMIT)

        logger.info(f"\nSelected {len(selected_articles)} articles for analysis:")
        for i, article in enumerate(selected_articles, 1):
            logger.info(f"  {i}. [{article.category}] {article.title[:60]}...")

        # Step 5: Analyze with council
        logger.info("\n[5/6] Analyzing articles with LLM Council...")
        logger.info("This may take several minutes...")

        articles_dict = [article.to_dict() for article in selected_articles]
        analyses = await analyze_articles_batch(articles_dict)

        if not analyses:
            logger.error("No analyses produced. Exiting.")
            return False

        logger.info(f"\nSuccessfully analyzed {len(analyses)} articles")

        # Step 6: Publish to Jekyll site
        logger.info("\n[6/6] Publishing to Jekyll site...")
        publish_analyses(analyses)

        logger.info("\n" + "=" * 60)
        logger.info("Daily Digest Complete!")
        logger.info("=" * 60)
        logger.info(f"\nGenerated {len(analyses)} analyses")
        logger.info(f"Site published to: intelligence_hub/")
        logger.info("\nNext steps:")
        logger.info("  1. Review the generated content in intelligence_hub/")
        logger.info("  2. Test Jekyll locally: cd intelligence_hub && jekyll serve")
        logger.info("  3. Commit and push to GitHub to deploy via GitHub Pages")

        return True

    except Exception as e:
        logger.error(f"\n[ERROR] Pipeline failed: {e}", exc_info=True)
        return False


async def test_pipeline():
    """
    Test the pipeline with a smaller subset (useful for development).
    """
    logger.info("=" * 60)
    logger.info("Running Test Pipeline (Limited Articles)")
    logger.info("=" * 60)

    try:
        # Test with just 2 articles
        logger.info("\n[1/6] Fetching RSS feeds...")
        articles = fetch_all_feeds(RSS_FEEDS)

        logger.info("\n[2/6] Filtering to recent articles...")
        recent_articles = filter_recent_articles(articles, hours=168)  # Last week for testing

        logger.info("\n[3/6] Deduplicating articles...")
        unique_articles = deduplicate_articles(recent_articles)

        logger.info("\n[4/6] Selecting 2 articles for test...")
        test_articles = unique_articles[:2]

        logger.info(f"\nTest articles:")
        for i, article in enumerate(test_articles, 1):
            logger.info(f"  {i}. [{article.category}] {article.title[:60]}...")

        logger.info("\n[5/6] Analyzing with council...")
        articles_dict = [article.to_dict() for article in test_articles]
        analyses = await analyze_articles_batch(articles_dict)

        logger.info("\n[6/6] Publishing test site...")
        publish_analyses(analyses)

        logger.info("\n[OK] Test pipeline complete!")
        logger.info(f"Generated {len(analyses)} test analyses")

        return True

    except Exception as e:
        logger.error(f"\n[ERROR] Test pipeline failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="LLM Council RSS Automation - Cross-Disciplinary AI Intelligence Hub"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (analyze only 2 articles)"
    )

    args = parser.parse_args()

    if args.test:
        success = asyncio.run(test_pipeline())
    else:
        success = asyncio.run(run_daily_digest())

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
