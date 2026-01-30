"""
RSS Automation Package for LLM Council Intelligence Hub.

This package implements a complete RSS automation pipeline that:
1. Fetches articles from curated RSS feeds across multiple domains
2. Filters, deduplicates, and ranks articles
3. Analyzes articles using the LLM Council API
4. Publishes analyses to a Jekyll static site for GitHub Pages

Usage:
    # Run daily digest
    python -m rss_automation.main

    # Test with 2 articles
    python -m rss_automation.main --test
"""

__version__ = "1.0.0"
__author__ = "LLM Council"
__description__ = "Cross-Disciplinary AI Intelligence Hub - RSS Automation Pipeline"
