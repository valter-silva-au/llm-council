"""RSS feed fetcher for the Intelligence Hub."""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

logger = logging.getLogger("intelligence_hub.fetcher")


class Article:
    """Represents an RSS article."""

    def __init__(self, entry: Dict, feed_config: Dict):
        """
        Initialize article from RSS entry.

        Args:
            entry: RSS feed entry
            feed_config: Feed configuration dict
        """
        self.title = entry.get("title", "")
        self.link = entry.get("link", "")
        self.summary = entry.get("summary", entry.get("description", ""))
        self.published = self._parse_date(entry)
        self.source = feed_config["name"]
        self.category = feed_config["category"]
        self.domain_question = feed_config["domain_question"]

        # Generate unique ID
        self.id = hashlib.md5(self.link.encode()).hexdigest()[:12]

    def _parse_date(self, entry: Dict) -> datetime:
        """Parse publication date."""
        if "published_parsed" in entry and entry["published_parsed"]:
            return datetime(*entry["published_parsed"][:6])
        return datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "published": self.published.isoformat(),
            "source": self.source,
            "category": self.category,
            "domain_question": self.domain_question
        }


def fetch_feed(feed_config: Dict) -> List[Article]:
    """
    Fetch articles from a single RSS feed.

    Args:
        feed_config: Feed configuration dict

    Returns:
        List of Article objects
    """
    logger.info(f"Fetching {feed_config['name']}...")

    try:
        feed = feedparser.parse(feed_config["url"])

        if feed.bozo:
            logger.warning(f"Feed parse warning for {feed_config['name']}: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:10]:  # Take up to 10 recent articles
            try:
                article = Article(entry, feed_config)
                articles.append(article)
            except Exception as e:
                logger.error(f"Error parsing entry: {e}")
                continue

        logger.info(f"Fetched {len(articles)} articles from {feed_config['name']}")
        return articles

    except Exception as e:
        logger.error(f"Error fetching {feed_config['name']}: {e}")
        return []


def fetch_all_feeds(feeds_config: Dict[str, List[Dict]]) -> List[Article]:
    """
    Fetch articles from all configured feeds.

    Args:
        feeds_config: Complete feeds configuration

    Returns:
        List of all articles
    """
    logger.info("Starting RSS feed fetch...")

    all_articles = []

    for domain, feeds in feeds_config.items():
        logger.info(f"Fetching {domain}...")
        for feed_config in feeds:
            articles = fetch_feed(feed_config)
            all_articles.extend(articles)

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles


def filter_recent_articles(articles: List[Article], hours: int = 24) -> List[Article]:
    """
    Filter articles to only recent ones.

    Args:
        articles: List of articles
        hours: Maximum age in hours

    Returns:
        Filtered list of recent articles
    """
    cutoff = datetime.now() - timedelta(hours=hours)
    recent = [a for a in articles if a.published >= cutoff]

    logger.info(f"Filtered to {len(recent)} articles from last {hours} hours")
    return recent


def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """
    Remove duplicate articles based on title similarity.

    Args:
        articles: List of articles

    Returns:
        Deduplicated list
    """
    seen_titles = set()
    unique_articles = []

    for article in articles:
        # Simple deduplication by title (could be enhanced with similarity scoring)
        title_normalized = article.title.lower().strip()

        if title_normalized not in seen_titles:
            seen_titles.add(title_normalized)
            unique_articles.append(article)
        else:
            logger.debug(f"Duplicate removed: {article.title}")

    logger.info(f"Deduplicated: {len(articles)} -> {len(unique_articles)} articles")
    return unique_articles


def rank_articles(articles: List[Article]) -> List[Article]:
    """
    Rank articles by recency and source priority.

    Args:
        articles: List of articles

    Returns:
        Sorted list of articles
    """
    # Simple ranking: newer = higher priority
    sorted_articles = sorted(articles, key=lambda a: a.published, reverse=True)

    logger.info(f"Ranked {len(sorted_articles)} articles")
    return sorted_articles


def select_top_articles(articles: List[Article], limit: int = 7) -> List[Article]:
    """
    Select top N articles for analysis.

    Args:
        articles: List of articles
        limit: Maximum number to select

    Returns:
        Top articles
    """
    # Balance across categories
    selected = []
    per_category = {}

    for article in articles:
        category = article.category
        per_category[category] = per_category.get(category, 0) + 1

        # Try to balance: take best from each category
        if len(selected) < limit:
            selected.append(article)

    logger.info(f"Selected {len(selected)} articles for analysis")
    logger.info(f"Category distribution: {per_category}")

    return selected[:limit]
