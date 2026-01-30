"""Publisher for Intelligence Hub - generates Jekyll site."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json

from .config import OUTPUT_DIR, CATEGORIES

logger = logging.getLogger("intelligence_hub.publisher")


def init_site_structure():
    """Initialize the Jekyll site structure."""
    base_dir = Path(OUTPUT_DIR)

    dirs = [
        base_dir,
        base_dir / "_posts",
        base_dir / "_data",
        base_dir / "assets",
        base_dir / "categories"
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Site structure initialized at {base_dir}")


def generate_jekyll_config():
    """Generate _config.yml for Jekyll."""
    config = """# Cross-Disciplinary AI Intelligence Hub
title: "AI Intelligence Hub"
description: "AI-curated analysis from the LLM Council"
baseurl: ""
url: "https://yourusername.github.io"

# Build settings
markdown: kramdown
theme: minima

# Collections
collections:
  analyses:
    output: true
    permalink: /analysis/:year/:month/:day/:title/

# Navigation
header_pages:
  - categories/tech.md
  - categories/ai.md
  - categories/security.md
  - categories/business.md
  - about.md

# Council info
council:
  name: "LLM Council"
  description: "Multi-model AI deliberation system"
  api_url: "https://github.com/valter-silva-au/llm-council"
"""

    output_file = Path(OUTPUT_DIR) / "_config.yml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config)

    logger.info("Generated _config.yml")


def generate_index_page(analyses: List[Dict]):
    """Generate index.md homepage."""
    content = f"""---
layout: home
title: "AI Intelligence Hub"
---

# Cross-Disciplinary AI Intelligence Hub

**AI-Curated Analysis from the LLM Council**

Welcome to the Intelligence Hub - where multiple AI models deliberate on technology, AI research, security, and business news to provide you with diverse, synthesized insights.

## Latest Analyses

"""

    for analysis in analyses[:10]:  # Show latest 10
        date = analysis["article_published"][:10]
        content += f"""
### [{analysis["article_title"]}]({analysis["article_link"]})

**Source:** {analysis["article_source"]} | **Category:** {analysis["article_category"]} | **Date:** {date}

**Council Analysis:**
{analysis["analysis"][:300]}...

[Read Full Analysis →](/analysis/{date.replace('-', '/')}/{analysis["article_id"]})

---
"""

    content += """
## About

This site is powered by the **LLM Council** - a multi-model AI deliberation system featuring:
- Claude Opus 4.5
- DeepSeek R1
- Mistral Large
- Amazon Nova Premier

Each analysis represents collective intelligence from multiple AI perspectives, synthesized into actionable insights.

## Categories

- [Tech News](/categories/tech) - Market impacts and consumer technology
- [AI Research](/categories/ai) - Technical breakthroughs and applications
- [Security](/categories/security) - Cybersecurity implications
- [Business](/categories/business) - Strategic and market dynamics

---

*Analyses updated daily. Powered by the [LLM Council](https://github.com/valter-silva-au/llm-council).*
"""

    output_file = Path(OUTPUT_DIR) / "index.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Generated index.md")


def generate_analysis_post(analysis: Dict):
    """
    Generate a Jekyll post for an analysis.

    Args:
        analysis: Analysis dictionary
    """
    date = analysis["article_published"][:10]
    timestamp = analysis["article_published"]

    # Create filename: YYYY-MM-DD-title.md
    safe_title = analysis["article_title"][:50].lower()
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in safe_title)
    safe_title = safe_title.replace(" ", "-")
    filename = f"{date}-{safe_title}.md"

    # Generate frontmatter and content
    content = f"""---
layout: post
title: "{analysis['article_title']}"
date: {timestamp}
categories: [{analysis['article_category']}]
source: "{analysis['article_source']}"
original_link: "{analysis['article_link']}"
chairman: "{analysis['chairman']}"
models: {analysis['models_participated']}
consensus: "{analysis['consensus_metrics']['agreement_level']}"
---

# {analysis['article_title']}

**Source:** [{analysis['article_source']}]({analysis['article_link']})
**Published:** {date}
**Category:** {analysis['article_category'].upper()}

---

## Council Analysis

{analysis['analysis']}

---

## Deliberation Details

**Chairman:** {analysis['chairman']}
**Models Participated:** {analysis['models_participated']}
**Consensus Level:** {analysis['consensus_metrics']['agreement_level']}

"""

    # Add individual perspectives if available
    if analysis.get('individual_responses'):
        content += "\n### Individual Model Perspectives\n\n"
        for resp in analysis['individual_responses']:
            model_name = resp['model'].split('.')[-1]  # Get short name
            content += f"<details>\n<summary><strong>{model_name}</strong></summary>\n\n"
            content += f"{resp['response'][:500]}...\n\n"
            content += "</details>\n\n"

    # Add link to full deliberation if available
    if analysis.get('deliberation_path'):
        delib_name = Path(analysis['deliberation_path']).name
        content += f"\n[View Complete Deliberation Archive →](https://github.com/valter-silva-au/llm-council/tree/master/deliberations/{delib_name})\n\n"

    content += """
---

*This analysis was generated by the LLM Council - a multi-model AI deliberation system.
[Learn more →](https://github.com/valter-silva-au/llm-council)*
"""

    # Write post file
    posts_dir = Path(OUTPUT_DIR) / "_posts"
    output_file = posts_dir / filename

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    logger.debug(f"Generated post: {filename}")


def generate_category_pages():
    """Generate category index pages."""
    for category in CATEGORIES:
        content = f"""---
layout: page
title: "{category.upper()}"
permalink: /categories/{category}/
---

# {category.upper()} News & Analysis

Latest AI council analyses in the {category} category.

{{{{ site.categories.{category} }}}}
"""

        category_dir = Path(OUTPUT_DIR) / "categories"
        output_file = category_dir / f"{category}.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

    logger.info(f"Generated {len(CATEGORIES)} category pages")


def generate_metadata_json(analyses: List[Dict]):
    """Generate metadata JSON for API/programmatic access."""
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_analyses": len(analyses),
        "categories": {},
        "latest_analyses": []
    }

    # Count by category
    for analysis in analyses:
        category = analysis["article_category"]
        metadata["categories"][category] = metadata["categories"].get(category, 0) + 1

    # Latest 20 analyses (lightweight)
    for analysis in analyses[:20]:
        metadata["latest_analyses"].append({
            "id": analysis["article_id"],
            "title": analysis["article_title"],
            "source": analysis["article_source"],
            "category": analysis["article_category"],
            "published": analysis["article_published"],
            "link": analysis["article_link"]
        })

    # Write metadata
    output_file = Path(OUTPUT_DIR) / "_data" / "metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Generated metadata.json")


def publish_analyses(analyses: List[Dict]):
    """
    Publish analyses to Jekyll site.

    Args:
        analyses: List of analysis dictionaries
    """
    logger.info(f"Publishing {len(analyses)} analyses...")

    # Initialize site structure
    init_site_structure()

    # Generate config
    generate_jekyll_config()

    # Generate category pages
    generate_category_pages()

    # Generate posts for each analysis
    for analysis in analyses:
        generate_analysis_post(analysis)

    # Generate homepage
    generate_index_page(analyses)

    # Generate metadata
    generate_metadata_json(analyses)

    logger.info(f"[OK] Published {len(analyses)} analyses to {OUTPUT_DIR}")
    logger.info(f"Site ready at: {Path(OUTPUT_DIR).absolute()}")
