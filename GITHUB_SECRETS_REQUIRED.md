# Required GitHub Secrets for RSS Automation

The RSS automation workflow requires two secrets to be configured in GitHub:

## 1. COUNCIL_API_KEY

**Purpose:** Authentication for the council API calls from the RSS automation pipeline.

**How to get it:**
```bash
# Generate a new API key
python manage_api_keys.py

# Follow the prompts to create a key named "GitHub Actions RSS Automation"
# Copy the generated key (starts with llmc_)
```

**How to add to GitHub:**
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `COUNCIL_API_KEY`
5. Value: Paste the `llmc_xxxxx...` key
6. Click "Add secret"

## 2. OPENROUTER_API_KEY

**Purpose:** Used by the backend to call OpenRouter API for LLM models.

**How to get it:**
1. Go to https://openrouter.ai/
2. Sign in and go to Keys
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-`)

**How to add to GitHub:**
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `OPENROUTER_API_KEY`
5. Value: Paste your OpenRouter API key
6. Click "Add secret"

## Verification

After adding both secrets, you should see them listed in:
- Settings → Secrets and variables → Actions → Repository secrets

Both should show as "Updated [timestamp]" but the values remain hidden.

## What the Workflow Does

With these secrets configured, the workflow will:

1. **Start backend server** using `OPENROUTER_API_KEY`
   - Loads environment variables
   - Starts FastAPI server on localhost:8001
   - Waits for server to be ready

2. **Run RSS automation** using `COUNCIL_API_KEY`
   - Authenticates API calls to the council
   - Fetches and analyzes articles
   - Generates Jekyll site content

3. **Deploy to Pages**
   - Uploads generated site
   - Deploys to GitHub Pages

## Security Notes

- Secrets are encrypted and never exposed in logs
- Secrets are only available to workflows in your repository
- You can rotate secrets anytime by updating them in Settings
- The backend server runs only during workflow execution
- No secrets are committed to the repository

## Testing Locally

To test the full pipeline locally before triggering the workflow:

```bash
# Make sure you have both keys set up
echo "OPENROUTER_API_KEY=sk-or-v1-xxx..." > .env
echo "llmc_xxx..." > test_api_key.txt

# Start backend
uv run python -m backend.main &

# Wait a moment for startup, then run automation
uv run python -m rss_automation.main --test

# Check results
ls intelligence_hub/_posts/
```

## Troubleshooting

**If workflow fails with "Connection refused":**
- Backend didn't start properly
- Check backend.log in workflow artifacts
- Verify OPENROUTER_API_KEY is set correctly

**If workflow fails with "401 Unauthorized":**
- COUNCIL_API_KEY is invalid or expired
- Regenerate the key and update the secret

**If workflow fails with "No analyses produced":**
- Backend couldn't reach OpenRouter
- Check OPENROUTER_API_KEY is valid
- Verify you have OpenRouter credits

## Monitoring

You can monitor the workflow execution in:
- Actions tab → Daily Intelligence Hub Digest → Latest run

Look for these steps:
1. ✓ Install dependencies
2. ✓ Create API key file
3. ✓ Create .env file with OpenRouter API key
4. ✓ Start backend server (should show "Backend is ready!")
5. ✓ Run RSS automation pipeline
6. ✓ Commit and push results
7. ✓ Deploy to GitHub Pages
