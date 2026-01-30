# View LLM Council logs in real-time
param(
    [Parameter(Position=0)]
    [ValidateSet("backend", "frontend", "both")]
    [string]$Service = "backend",

    [Parameter()]
    [int]$Lines = 50
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendLog = "$ProjectRoot\scripts\.backend.log"
$FrontendLog = "$ProjectRoot\scripts\.frontend.log"

function Show-Log {
    param($LogFile, $ServiceName)

    if (-not (Test-Path $LogFile)) {
        Write-Host "$ServiceName log not found: $LogFile" -ForegroundColor Red
        return
    }

    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "$ServiceName Logs (last $Lines lines, live updates)" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host ""

    Get-Content $LogFile -Tail $Lines -Wait
}

switch ($Service) {
    "backend" {
        Show-Log -LogFile $BackendLog -ServiceName "Backend"
    }
    "frontend" {
        Show-Log -LogFile $FrontendLog -ServiceName "Frontend"
    }
    "both" {
        Write-Host "Showing both logs (backend in GREEN, frontend in CYAN)" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
        Write-Host ""

        # Show both logs with color coding
        Get-Content $BackendLog, $FrontendLog -Tail $Lines -Wait | ForEach-Object {
            if ($_ -match "backend") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "frontend|vite") {
                Write-Host $_ -ForegroundColor Cyan
            } else {
                Write-Host $_
            }
        }
    }
}
