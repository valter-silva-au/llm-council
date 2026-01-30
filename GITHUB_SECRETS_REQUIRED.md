# Required GitHub Secrets for RSS Automation

The RSS automation workflow requires multiple secrets to be configured in GitHub.

## Quick Setup (Recommended)

Use the provided script to add all secrets at once:

**PowerShell (Windows):**
```powershell
.\add_github_secrets.ps1
```

**Bash (Linux/Mac):**
```bash
chmod +x add_github_secrets.sh
./add_github_secrets.sh
```

## Manual Setup

If you prefer to add secrets manually, here's what's required:

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

## 2. AWS Bedrock Credentials

**Purpose:** Used by the backend to call AWS Bedrock for LLM models.

**Required secrets:**
- `API_PROVIDER` - Set to "bedrock"
- `AWS_REGION` - AWS region (e.g., "us-west-2")
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_SESSION_TOKEN` - Your AWS session token (if using temporary credentials)
- `AWS_BEARER_TOKEN_BEDROCK` - Bedrock-specific bearer token

**How to get AWS credentials:**
1. Go to AWS Console → IAM
2. Create or use existing credentials with Bedrock access
3. Generate access keys

**How to add to GitHub:**
Use the provided script (recommended) or add each secret manually:
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret" for each credential
4. Add all AWS-related secrets listed above

## 3. Web Search API Keys

**Required for council web search functionality:**
- `TAVILY_API_KEY` - Tavily search API
- `BRAVE_API_KEY` - Brave search API

## 4. Other Optional API Keys

These are optional but recommended:
- `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`
- `GOOGLE_AI_API_KEY`
- `PERPLEXITY_API_KEY`
- `FIRECRAWL_API_KEY`
- `JINA_API_KEY`
- `KAGI_API_KEY`
- `OPENWEATHER_API_KEY`

## Verification

After adding all secrets, you should see them listed in:
- Settings → Secrets and variables → Actions → Repository secrets

All secrets should show as "Updated [timestamp]" but the values remain hidden.

Expected secrets count: ~15+ (depending on which optional keys you add)

## What the Workflow Does

With these secrets configured, the workflow will:

1. **Start backend server** using AWS Bedrock credentials
   - Loads all environment variables (.env file)
   - Configures AWS Bedrock access
   - Starts FastAPI server on localhost:8001
   - Waits for server to be ready

2. **Run RSS automation** using `COUNCIL_API_KEY`
   - Authenticates API calls to the council
   - Fetches articles from RSS feeds
   - Analyzes with council (using Bedrock models)
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
# Make sure you have your .env file set up with AWS credentials
# (Should already exist with API_PROVIDER=bedrock, AWS credentials, etc.)

# Make sure you have the council API key
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
- Verify AWS credentials are set correctly

**If workflow fails with "401 Unauthorized":**
- COUNCIL_API_KEY is invalid or expired
- Regenerate the key: `python manage_api_keys.py`
- Update the secret in GitHub

**If workflow fails with "No analyses produced":**
- Backend couldn't reach AWS Bedrock
- Check AWS credentials are valid and not expired
- Verify AWS session token hasn't expired (temporary credentials)
- Check that your AWS account has Bedrock access enabled

**If workflow fails with AWS auth errors:**
- AWS session tokens expire (usually 1-12 hours)
- Regenerate AWS credentials and update secrets
- Consider using long-term IAM credentials instead

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
