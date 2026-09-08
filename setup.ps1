# =============================================================
#  Yatra-Setu Project Setup Script
#  Run this in PowerShell from inside the cloned repo folder.
# =============================================================

Write-Host "=== Yatra-Setu Project Setup ===" -ForegroundColor Cyan
Write-Host ""

# --- 1. Check Python ---
Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "  Python not found." -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  IMPORTANT: check 'Add Python to PATH' during install, then re-run this script." -ForegroundColor Red
    exit 1
} else {
    $pyVersion = python --version
    Write-Host "  Found: $pyVersion" -ForegroundColor Green
}

# --- 2. Check pip ---
Write-Host "[2/7] Checking pip..." -ForegroundColor Yellow
python -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  pip not found for this Python. Installing..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
} else {
    Write-Host "  pip is available." -ForegroundColor Green
}

# --- 3. Check git ---
Write-Host "[3/7] Checking git..." -ForegroundColor Yellow
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "  Git not found." -ForegroundColor Red
    Write-Host "  Please install Git from https://git-scm.com/downloads and re-run this script." -ForegroundColor Red
    exit 1
} else {
    Write-Host "  Git is available." -ForegroundColor Green
}

# --- 4. Check Docker Desktop (for Redis) ---
Write-Host "[4/7] Checking Docker..." -ForegroundColor Yellow
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "  Docker not found." -ForegroundColor Red
    Write-Host "  Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    Write-Host "  NOTE: Docker requires virtualization enabled in your BIOS/UEFI." -ForegroundColor Red
    Write-Host "  If Docker Desktop shows a 'Virtualization support not detected' error," -ForegroundColor Red
    Write-Host "  you'll need to enable Intel VT-x / AMD-V in your BIOS settings manually." -ForegroundColor Red
    Write-Host "  Re-run this script once Docker is installed and running." -ForegroundColor Red
    exit 1
} else {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Docker is installed but not running. Please open Docker Desktop and wait for it to start." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Docker is installed and running." -ForegroundColor Green
}

# --- 5. Set up Python virtual environment ---
Write-Host "[5/7] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Host "  Created new virtual environment." -ForegroundColor Green
} else {
    Write-Host "  Virtual environment already exists." -ForegroundColor Green
}

& ".\venv\Scripts\Activate.ps1"

Write-Host "  Installing Python packages from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip *> $null
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Failed to install some packages. Check the error above." -ForegroundColor Red
    exit 1
}
Write-Host "  Packages installed." -ForegroundColor Green

# --- 6. Install Playwright's browser binary ---
Write-Host "[6/7] Installing Playwright's Chromium browser..." -ForegroundColor Yellow
python -m playwright install chromium
Write-Host "  Chromium installed." -ForegroundColor Green

# --- 7. Start Redis via Docker, then run Django migrations ---
Write-Host "[7/7] Starting Redis and running database setup..." -ForegroundColor Yellow

$redisRunning = docker ps --filter "ancestor=redis" --filter "status=running" -q
if (-not $redisRunning) {
    Write-Host "  Starting a Redis container in the background..." -ForegroundColor Yellow
    docker run -d -p 6379:6379 --name yatra-redis redis *> $null
    Start-Sleep -Seconds 3
} else {
    Write-Host "  Redis container already running." -ForegroundColor Green
}

Write-Host "  Note: this project currently uses SQLite, so no .env file is required." -ForegroundColor Yellow
Write-Host "  This means your database will start EMPTY and separate from anyone else's." -ForegroundColor Yellow
Write-Host "  Scraped data will not be shared across machines until the project moves to a shared database." -ForegroundColor Yellow
Write-Host ""

python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Migration failed. Check your .env database settings." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setup complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the project, open THREE separate terminals in this folder and run:" -ForegroundColor Cyan
Write-Host "  1) .\venv\Scripts\Activate.ps1 ; python manage.py runserver" -ForegroundColor White
Write-Host "  2) .\venv\Scripts\Activate.ps1 ; celery -A config worker --loglevel=info --pool=solo" -ForegroundColor White
Write-Host "  3) .\venv\Scripts\Activate.ps1 ; celery -A config beat --loglevel=info" -ForegroundColor White
Write-Host ""
Write-Host "Then visit http://127.0.0.1:8000/admin to log in." -ForegroundColor White
