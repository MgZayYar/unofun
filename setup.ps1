# unofun one-time setup (Windows PowerShell)
# Right-click -> "Run with PowerShell". Installs everything and builds the database.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Require-Command($name, $hint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "MISSING: $name" -ForegroundColor Red
        Write-Host $hint
        Write-Host ""
        exit 1
    }
    Write-Host "found: $name" -ForegroundColor Green
}

Require-Command python "Install Python 3.12 from https://www.python.org/downloads/ (tick 'Add python.exe to PATH')"
Require-Command node   "Install Node.js 20 LTS from https://nodejs.org/"
Require-Command npm    "Comes with the Node.js installer above."
Require-Command ffmpeg "Install from https://www.gyan.dev/ffmpeg/builds/ -> extract -> add its bin folder to PATH."

if (-not (Test-Path "$root\.env")) {
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host ""
    Write-Host "Created .env - open it in VS Code and set JWT_SECRET_KEY (any long random string)" -ForegroundColor Yellow
    Write-Host "and OPENAI_API_KEY (needed for translation; voice TTS itself is free)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location "$root\backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -q -e ".[dev]"
python -m alembic upgrade head
Write-Host "Database created." -ForegroundColor Green

Write-Host ""
Write-Host "Setting up frontend (this takes a minute)..." -ForegroundColor Cyan
Set-Location "$root\frontend"
npm install --no-audit --no-fund

Write-Host ""
Write-Host "Done! Now run:  .\start.ps1" -ForegroundColor Green
Write-Host "Then open http://localhost:3000 and register an account." -ForegroundColor Green
