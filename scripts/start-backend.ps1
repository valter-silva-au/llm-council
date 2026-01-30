# Start the LLM Council backend server
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = "$ProjectRoot\scripts\.backend.pid"

# Check if already running
if (Test-Path $PidFile) {
    $ExistingPid = Get-Content $PidFile
    $Process = Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Backend is already running (PID: $ExistingPid)" -ForegroundColor Yellow
        Write-Host "Use .\stop-backend.ps1 to stop it first"
        exit 1
    }
    Remove-Item $PidFile
}

Write-Host "Starting LLM Council backend..." -ForegroundColor Cyan

# Set DEBUG mode
$env:DEBUG = "true"

# Change to project root
Push-Location $ProjectRoot

try {
    # Start the backend
    # Check if uv is available and prefer it, otherwise use python directly
    $UvPath = Get-Command uv -ErrorAction SilentlyContinue

    if ($UvPath) {
        Write-Host "Using uv runtime..." -ForegroundColor Cyan
        $Process = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "backend.main" `
            -PassThru -NoNewWindow -RedirectStandardOutput "$ProjectRoot\scripts\.backend.log" `
            -RedirectStandardError "$ProjectRoot\scripts\.backend.err" -WorkingDirectory $ProjectRoot
    } else {
        Write-Host "Using direct python execution..." -ForegroundColor Cyan
        $Process = Start-Process -FilePath "python" -ArgumentList "-m", "backend.main" `
            -PassThru -NoNewWindow -RedirectStandardOutput "$ProjectRoot\scripts\.backend.log" `
            -RedirectStandardError "$ProjectRoot\scripts\.backend.err" -WorkingDirectory $ProjectRoot
    }

    # Save PID
    $Process.Id | Out-File $PidFile -NoNewline

    # Wait a moment and check if it started
    Start-Sleep -Seconds 2

    if ($Process.HasExited) {
        Write-Host "Backend failed to start. Check .backend.err for details:" -ForegroundColor Red
        Get-Content "$ProjectRoot\scripts\.backend.err" | Select-Object -Last 10
        exit 1
    }

    Write-Host "Backend started successfully!" -ForegroundColor Green
    Write-Host "  PID: $($Process.Id)"
    Write-Host "  URL: http://localhost:8001"
    Write-Host "  Logs: scripts\.backend.log"
    Write-Host "  Debug mode: ON"
}
finally {
    Pop-Location
}
