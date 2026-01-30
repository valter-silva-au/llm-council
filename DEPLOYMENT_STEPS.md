# Intelligence Hub Deployment Steps

## ✅ Completed
- [x] RSS automation pipeline built
- [x] GitHub Actions workflow configured
- [x] API key secret added to GitHub

## Next Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub:
   https://github.com/valter-silva-au/llm-council

2. Click **Settings** (top menu)

3. Scroll down to **Pages** (left sidebar under "Code and automation")

4. Under **Source**:
   - Select: **Deploy from a branch**
   - Branch: **master**
   - Folder: **/intelligence_hub**
   - Click **Save**

5. GitHub will show: "Your site is ready to be published at..."
   - Note: First deployment may take 1-2 minutes

### 2. Trigger First Workflow Run

#### Option A: Manual Trigger (Recommended for first run)

1. Go to **Actions** tab in your repository

2. Click **"Daily Intelligence Hub Digest"** in the left sidebar

3. Click **"Run workflow"** button (top right)

4. Select branch: **master**

5. Click **"Run workflow"** (green button)

6. Watch the workflow execute (takes ~5-10 minutes):
   - Fetches RSS feeds
   - Analyzes 5-7 articles with council
   - Generates Jekyll site
   - Commits results
   - Auto-deploys to GitHub Pages

#### Option B: Wait for Scheduled Run

The workflow runs automatically daily at 9 AM UTC.

### 3. View Your Live Site

After the workflow completes:

**URL will be:**
```
https://valter-silva-au.github.io/llm-council/
```

Or check the exact URL in:
- Settings → Pages → "Your site is live at..."

### 4. Monitor Workflow Execution

**During first run, watch for:**
- ✅ RSS feeds fetching successfully
- ✅ Council analysis completing (4 models)
- ✅ Jekyll site generation
- ✅ Git commit and push
- ✅ Pages deployment

**Check workflow logs:**
- Actions → Daily Intelligence Hub Digest → Latest run → View logs

### 5. Verify Deployment

Once live, check:
- [ ] Homepage loads with latest analyses
- [ ] Category pages work (Tech, AI, Security, Business)
- [ ] Individual analysis posts display correctly
- [ ] Individual model perspectives expand/collapse
- [ ] About page renders properly
- [ ] Navigation works

### Troubleshooting

**If workflow fails:**
1. Check Actions logs for errors
2. Verify API key secret is correct
3. Ensure backend is running (for API calls)
4. Check rss_automation.log in workflow artifacts

**If Pages don't deploy:**
1. Verify Pages is enabled in Settings
2. Check branch and folder are correct (master, /intelligence_hub)
3. Wait 1-2 minutes for first deployment
4. Check Actions → pages-build-deployment workflow

**If analyses seem incomplete:**
1. Review the committed files in intelligence_hub/_posts/
2. Check that all 4 models participated (in post frontmatter)
3. Verify web search was enabled in analyzer.py

## Expected First Run Results

- **Duration**: 5-10 minutes
- **Articles analyzed**: 5-7 (from last 24 hours)
- **Files created**:
  - intelligence_hub/_posts/*.md (5-7 files)
  - intelligence_hub/index.md (updated)
  - intelligence_hub/_data/metadata.json (updated)
- **New commit**: "Daily Intelligence Hub Digest - YYYY-MM-DD"

## Customization (Optional)

After successful deployment, you can:

### Change Schedule
Edit `.github/workflows/daily-digest.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours instead of daily
```

### Adjust Article Count
Edit `rss_automation/config.py`:
```python
DAILY_ARTICLE_LIMIT = 10  # Increase from default 7
```

### Add Custom Domain
Settings → Pages → Custom domain
(Requires DNS CNAME configuration)

## Success Checklist

- [ ] GitHub Pages enabled
- [ ] First workflow run completed successfully
- [ ] Site is live and accessible
- [ ] Analyses display correctly
- [ ] Navigation works
- [ ] Categories populate correctly
- [ ] Individual perspectives show/hide properly

---

**Ready to launch!** 🚀

Start with enabling GitHub Pages, then trigger the first workflow run.
