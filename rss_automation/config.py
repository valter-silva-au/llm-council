"""Configuration for RSS automation pipeline."""

# RSS Feed Sources (8 feeds across 4 domains)
RSS_FEEDS = {
    "tech_news": [
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "category": "tech",
            "domain_question": "What is the market impact of this development?"
        },
        {
            "name": "The Verge",
            "url": "https://www.theverge.com/rss/index.xml",
            "category": "tech",
            "domain_question": "How will this affect consumer technology adoption?"
        }
    ],
    "ai_research": [
        {
            "name": "arXiv CS.AI",
            "url": "http://export.arxiv.org/rss/cs.AI",
            "category": "ai",
            "domain_question": "What technical breakthroughs could emerge from this research?"
        },
        {
            "name": "Papers with Code",
            "url": "https://paperswithcode.com/rss",
            "category": "ai",
            "domain_question": "What practical applications does this enable?"
        }
    ],
    "security": [
        {
            "name": "Krebs on Security",
            "url": "https://krebsonsecurity.com/feed/",
            "category": "security",
            "domain_question": "What are the cybersecurity implications for organizations?"
        },
        {
            "name": "Schneier on Security",
            "url": "https://www.schneier.com/feed/atom/",
            "category": "security",
            "domain_question": "What defensive measures should be considered?"
        }
    ],
    "business": [
        {
            "name": "Reuters Technology",
            "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "category": "business",
            "domain_question": "What are the business and strategic implications?"
        },
        {
            "name": "Bloomberg Technology",
            "url": "https://feeds.bloomberg.com/technology/news.rss",
            "category": "business",
            "domain_question": "How will this impact market dynamics?"
        }
    ]
}

# Analysis Questions (3 generic + 1 domain-specific)
ANALYSIS_QUESTIONS = [
    "What are the 3 main takeaways from this article?",
    "What are the potential benefits and risks discussed?",
    "How does this relate to broader industry trends?",
    # Domain-specific question added based on feed config
]

# Publishing Configuration
DAILY_ARTICLE_LIMIT = 7  # Top 5-7 articles per day
MIN_QUALITY_SCORE = 0.6  # Minimum quality threshold

# Council API Configuration
API_URL = "http://localhost:8001/api/v1"
API_KEY_FILE = "test_api_key.txt"

# Output Configuration
OUTPUT_DIR = "intelligence_hub"
CATEGORIES = ["tech", "ai", "security", "business"]

# Consensus Configuration
MIN_CONSENSUS_THRESHOLD = 0.75  # 75% agreement = strong consensus
