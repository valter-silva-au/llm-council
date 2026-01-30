# RSS Automation - Cross-Disciplinary AI Intelligence Hub

Automated RSS pipeline that uses the LLM Council to analyze news across Tech, AI/ML, Security, and Business domains.

## Overview

This system:
1. **Fetches** articles from 8 curated RSS feeds (2 per domain)
2. **Filters** to recent, high-quality articles
3. **Analyzes** using the LLM Council multi-model deliberation
4. **Publishes** to a Jekyll static site with full transparency

## Architecture

```
RSS Feeds → Fetcher → Analyzer (Council API) → Publisher (Jekyll) → GitHub Pages
```

### Modules

- **config.py**: Feed URLs, analysis questions, publishing config
- **fetcher.py**: RSS parsing, filtering, deduplication, ranking
- **analyzer.py**: Council-powered article analysis via API
- **publisher.py**: Jekyll site generation with posts and categories
- **main.py**: Orchestrates the complete pipeline

## Usage

### Local Testing

```bash
# Test with 2 articles
uv run python -m rss_automation.main --test

# Full daily digest
uv run python -m rss_automation.main
```

### GitHub Actions (Automated)

The workflow runs daily at 9 AM UTC and:
1. Fetches latest articles
2. Analyzes with council
3. Commits results to `intelligence_hub/`
4. GitHub Pages auto-deploys

**Required GitHub Secret:**
- `COUNCIL_API_KEY`: API key for council access (create via `python manage_api_keys.py`)

## Output Structure

```
intelligence_hub/
├── _config.yml           # Jekyll configuration
├── index.md              # Homepage with latest analyses
├── _posts/               # Individual analysis posts
│   └── YYYY-MM-DD-title.md
├── categories/           # Category index pages
│   ├── tech.md
│   ├── ai.md
│   ├── security.md
│   └── business.md
└── _data/
    └── metadata.json     # API-accessible metadata
```

## RSS Feeds

### Tech News (2)
- TechCrunch
- The Verge

### AI Research (2)
- arXiv CS.AI
- Papers with Code

### Security (2)
- Krebs on Security
- Schneier on Security

### Business (2)
- Reuters Technology
- Bloomberg Technology

## Analysis Format

Each article receives 4 structured questions:
1. What are the 3 main takeaways?
2. What are the potential benefits and risks?
3. How does this relate to broader industry trends?
4. [Domain-specific question based on category]

## Council Integration

- Uses the council API for all analyses
- Includes web search for current context
- Captures individual model perspectives
- Calculates consensus metrics
- Links to full deliberation archives

## Configuration

Edit `config.py` to customize:
- `RSS_FEEDS`: Add/remove feeds
- `ANALYSIS_QUESTIONS`: Change question format
- `DAILY_ARTICLE_LIMIT`: Adjust daily volume (default: 7)
- `OUTPUT_DIR`: Change site location

## Deployment

### GitHub Pages Setup

1. **Enable GitHub Pages:**
   - Go to repo Settings → Pages
   - Source: Deploy from branch
   - Branch: `master`, Folder: `/intelligence_hub`

2. **Add API Key Secret:**
   ```bash
   # Generate key
   python manage_api_keys.py

   # Add to GitHub:
   # Settings → Secrets → Actions → New repository secret
   # Name: COUNCIL_API_KEY
   # Value: llmc_xxxxx...
   ```

3. **Trigger First Run:**
   - Actions tab → Daily Intelligence Hub Digest → Run workflow

### Local Jekyll Preview

```bash
cd intelligence_hub
gem install bundler jekyll
jekyll serve

# Visit http://localhost:4000
```

## Logs

- **Console output**: Real-time progress
- **rss_automation.log**: Detailed logs (rotated daily)
- **GitHub Actions**: Workflow runs and artifacts

## Customization

### Add New Feed

```python
# In config.py
RSS_FEEDS["your_domain"].append({
    "name": "Feed Name",
    "url": "https://example.com/feed.xml",
    "category": "tech",  # or ai, security, business
    "domain_question": "Your domain-specific question?"
})
```

### Change Publishing Schedule

```yaml
# In .github/workflows/daily-digest.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours instead of daily
```

### Adjust Article Limit

```python
# In config.py
DAILY_ARTICLE_LIMIT = 10  # Increase from default 7
```

## Error Handling

- Feed fetch failures are logged but don't stop the pipeline
- Analysis failures skip that article and continue
- Empty results prevent publishing (fail-safe)
- Debug artifacts uploaded on GitHub Actions failure

## Future Enhancements

From council guidance:
- Weekly trend analysis summaries
- "Helpful analysis?" feedback buttons
- Auto-tagging of sensitive topics
- Strategic impact scoring
- Multi-language support

## Credits

**Analyzed by the LLM Council**

- Chairman selection rotates per deliberation
- Models: Claude Opus 4.5, DeepSeek R1, Mistral Large, Amazon Nova Premier
- Full transparency with consensus metrics and individual perspectives

---

*Built following LLM Council strategic guidance (2026-01-30)*
