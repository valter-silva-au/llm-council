# PowerShell script to add secrets from .env file to GitHub repository
# Usage: .\add_github_secrets.ps1

$REPO = "valter-silva-au/llm-council"

Write-Host "Adding secrets to GitHub repository: $REPO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if gh CLI is installed
if (!(Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Error: gh CLI is not installed" -ForegroundColor Red
    Write-Host "Install with: winget install GitHub.cli"
    exit 1
}

# Check if authenticated
try {
    gh auth status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: gh CLI is not authenticated" -ForegroundColor Red
        Write-Host "Run: gh auth login"
        exit 1
    }
} catch {
    Write-Host "Error: gh CLI is not authenticated" -ForegroundColor Red
    Write-Host "Run: gh auth login"
    exit 1
}

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    Write-Host "Create a .env file with your credentials first"
    exit 1
}

Write-Host "Reading credentials from .env file..." -ForegroundColor Cyan
Write-Host ""

# Read .env file and parse key-value pairs
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and !$line.StartsWith("#")) {
        if ($line -match "^export\s+(.+)=(.+)$") {
            # Handle export statements
            $key = $Matches[1].Trim()
            $value = $Matches[2].Trim().Trim("'").Trim('"')
            $envVars[$key] = $value
        } elseif ($line -match "^(.+)=(.+)$") {
            $key = $Matches[1].Trim()
            $value = $Matches[2].Trim().Trim("'").Trim('"')
            $envVars[$key] = $value
        }
    }
}

# Function to add secret
function Add-GitHubSecret {
    param($Name, $Value)
    if ($Value) {
        Write-Host "  Adding: $Name" -ForegroundColor Yellow
        gh secret set $Name --body $Value --repo $REPO
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✓ Success" -ForegroundColor Green
        } else {
            Write-Host "    ✗ Failed" -ForegroundColor Red
        }
    } else {
        Write-Host "  Skipping: $Name (not found in .env)" -ForegroundColor Gray
    }
}

Write-Host "Adding secrets from .env..." -ForegroundColor Cyan
Write-Host ""

# AWS Bedrock
Add-GitHubSecret "API_PROVIDER" $envVars["API_PROVIDER"]
Add-GitHubSecret "AWS_REGION" $envVars["AWS_REGION"]
Add-GitHubSecret "AWS_ACCESS_KEY_ID" $envVars["AWS_ACCESS_KEY_ID"]
Add-GitHubSecret "AWS_SECRET_ACCESS_KEY" $envVars["AWS_SECRET_ACCESS_KEY"]
Add-GitHubSecret "AWS_SESSION_TOKEN" $envVars["AWS_SESSION_TOKEN"]
Add-GitHubSecret "AWS_BEARER_TOKEN_BEDROCK" $envVars["AWS_BEARER_TOKEN_BEDROCK"]

# Web Search
Add-GitHubSecret "TAVILY_API_KEY" $envVars["TAVILY_API_KEY"]
Add-GitHubSecret "BRAVE_API_KEY" $envVars["BRAVE_API_KEY"]

# YouTube
Add-GitHubSecret "YOUTUBE_CLIENT_ID" $envVars["YOUTUBE_CLIENT_ID"]
Add-GitHubSecret "YOUTUBE_CLIENT_SECRET" $envVars["YOUTUBE_CLIENT_SECRET"]

# Other APIs
Add-GitHubSecret "GOOGLE_AI_API_KEY" $envVars["GOOGLE_AI_API_KEY"]
Add-GitHubSecret "PERPLEXITY_API_KEY" $envVars["PERPLEXITY_API_KEY"]
Add-GitHubSecret "FIRECRAWL_API_KEY" $envVars["FIRECRAWL_API_KEY"]
Add-GitHubSecret "JINA_API_KEY" $envVars["JINA_API_KEY"]
Add-GitHubSecret "KAGI_API_KEY" $envVars["KAGI_API_KEY"]
Add-GitHubSecret "OPENWEATHER_API_KEY" $envVars["OPENWEATHER_API_KEY"]

Write-Host ""
Write-Host "Adding Council API key..." -ForegroundColor Cyan
if (Test-Path "test_api_key.txt") {
    $councilKey = Get-Content "test_api_key.txt" -Raw
    $councilKey = $councilKey.Trim()
    if ($councilKey) {
        Add-GitHubSecret "COUNCIL_API_KEY" $councilKey
    }
} else {
    Write-Host "⚠ test_api_key.txt not found. Generate with: python manage_api_keys.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ Secrets added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify secrets at:" -ForegroundColor Cyan
Write-Host "https://github.com/$REPO/settings/secrets/actions" -ForegroundColor Cyan
