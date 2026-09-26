# Start unofun (Windows PowerShell) - opens 3 windows: API, worker, web.
# Run setup.ps1 once first.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .\.venv\Scripts\Activate.ps1; python -m app.workers.runner"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "unofun is starting..." -ForegroundColor Green
Write-Host "Open http://localhost:3000 in your browser." -ForegroundColor Green
Write-Host "Close the three PowerShell windows to stop everything." -ForegroundColor DarkGray
