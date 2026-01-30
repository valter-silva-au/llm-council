# LLM Council PowerShell Scripts

Convenient PowerShell scripts for managing the LLM Council application on Windows.

## Quick Start

```powershell
# Start both services
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1

# Or restart everything at once
.\scripts\restart-all.ps1

# Check status
.\scripts\status.ps1

# View logs
.\scripts\logs.ps1
```

## Available Scripts

### Service Management

#### `start-backend.ps1`
Starts the FastAPI backend server on port 8001.
- Uses `uv run python -m backend.main` (falls back to direct python if uv not found)
- Enables DEBUG mode automatically
- Logs to `scripts/.backend.log`
- Saves PID to `scripts/.backend.pid`

```powershell
.\scripts\start-backend.ps1
```

#### `start-frontend.ps1`
Starts the Vite dev server on port 5173.
- Runs in hidden window (no console popup)
- Logs to `scripts/.frontend.log`
- Saves PID to `scripts/.frontend.pid`

```powershell
.\scripts\start-frontend.ps1
```

#### `stop-backend.ps1`
Stops the backend server gracefully.
- Kills process and any children (uvicorn workers)
- Cleans up port 8001 if needed
- Removes PID file

```powershell
.\scripts\stop-backend.ps1
```

#### `stop-frontend.ps1`
Stops the frontend server gracefully.
- Kills process and any children (Vite spawns multiple node processes)
- Cleans up ports 5173-5175 if needed
- Removes PID file

```powershell
.\scripts\stop-frontend.ps1
```

### Convenience Scripts

#### `restart-backend.ps1` ⭐
**Use this after code changes!**

Stops and restarts the backend, loading your latest code changes.

```powershell
.\scripts\restart-backend.ps1
```

#### `restart-frontend.ps1`
Stops and restarts the frontend (rarely needed - Vite hot-reloads).

```powershell
.\scripts\restart-frontend.ps1
```

#### `restart-all.ps1` ⭐⭐
**Most useful after pulling code updates!**

Restarts both backend and frontend in sequence.

```powershell
.\scripts\restart-all.ps1
```

#### `status.ps1`
Shows current status of both services.

```powershell
.\scripts\status.ps1
```

**Example output:**
```
============================================================
LLM Council Status
============================================================

Backend:
  Status: Running
  PID: 12345
  URL: http://localhost:8001
  Started: 1/30/2026 10:00:00 AM

Frontend:
  Status: Running
  PID: 67890
  URL: http://localhost:5173
  Started: 1/30/2026 10:00:05 AM
```

#### `logs.ps1`
View logs in real-time (follows like `tail -f`).

```powershell
# Backend logs only (default)
.\scripts\logs.ps1

# Frontend logs
.\scripts\logs.ps1 frontend

# Both logs with color coding
.\scripts\logs.ps1 both

# Show last 100 lines
.\scripts\logs.ps1 -Lines 100
```

**Tip:** Use this to debug issues in real-time while using the application.

## Common Workflows

### After Making Code Changes

```powershell
# If you changed backend code
.\scripts\restart-backend.ps1

# If you changed frontend code (usually auto-reloads, but if not:)
.\scripts\restart-frontend.ps1

# To restart everything
.\scripts\restart-all.ps1
```

### Debugging Issues

```powershell
# 1. Check if services are running
.\scripts\status.ps1

# 2. View logs in real-time
.\scripts\logs.ps1

# 3. In another terminal, use the app and watch logs
# (Keep logs.ps1 running)

# 4. Check error logs
Get-Content scripts\.backend.err
Get-Content scripts\.frontend.err
```

### Daily Development

```powershell
# Morning: Start everything
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1

# Work on code...
# After backend changes:
.\scripts\restart-backend.ps1

# Evening: Stop everything
.\scripts\stop-backend.ps1
.\scripts\stop-frontend.ps1
```

### After Git Pull

```powershell
# Restart to load new code
.\scripts\restart-all.ps1

# Check logs for any issues
.\scripts\logs.ps1
```

## Troubleshooting

### "Backend is already running"

```powershell
# Stop it first
.\scripts\stop-backend.ps1

# Then start again
.\scripts\start-backend.ps1
```

### Stale PID Files

If a service crashed but PID file remains:

```powershell
# Backend
.\scripts\stop-backend.ps1  # Cleans up stale PID
.\scripts\start-backend.ps1

# Or just delete manually
Remove-Item scripts\.backend.pid
Remove-Item scripts\.frontend.pid
```

### Port Already in Use

```powershell
# Backend (port 8001)
$proc = Get-NetTCPConnection -LocalPort 8001 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $proc -Force

# Frontend (port 5173)
$proc = Get-NetTCPConnection -LocalPort 5173 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $proc -Force
```

### View Error Messages

```powershell
# Backend errors
Get-Content scripts\.backend.err -Tail 50

# Frontend errors
Get-Content scripts\.frontend.err -Tail 50

# Live error monitoring
Get-Content scripts\.backend.err -Wait
```

### Scripts Won't Run (Execution Policy)

```powershell
# Check current policy
Get-ExecutionPolicy

# If it's Restricted, enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Log Files

All log files are in the `scripts/` directory:

- `.backend.log` - Backend stdout (INFO logs)
- `.backend.err` - Backend stderr (ERROR logs)
- `.backend.pid` - Backend process ID
- `.frontend.log` - Frontend stdout (Vite logs)
- `.frontend.err` - Frontend stderr (errors)
- `.frontend.pid` - Frontend process ID

**Note:** These files are gitignored (start with `.`)

## Environment

The backend automatically uses `.env.dev` if it exists, otherwise falls back to `.env`.

The start scripts enable `DEBUG=true` automatically for detailed logging.

## Tips

1. **Keep logs.ps1 running** in a separate terminal while developing for real-time debugging

2. **Use status.ps1** to quickly check if services are running

3. **restart-all.ps1** is your friend after pulling code updates

4. **Backend restart is quick** (~2 seconds), so restart liberally after code changes

5. **Frontend usually hot-reloads** automatically, rarely needs restart

6. **Check .err files** if services fail to start - they contain error details

## Script Locations

All scripts must be run from the project root:

```powershell
# Correct
.\scripts\start-backend.ps1

# Also works (from scripts directory)
cd scripts
.\start-backend.ps1

# Wrong - won't work
cd backend
..\scripts\start-backend.ps1  # Can't find project root
```
