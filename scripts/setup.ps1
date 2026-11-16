# Windows setup script for the QA Automation framework.
#
# What this does, in order: checks Python 3.11+, creates/reuses .venv,
# installs requirements.txt, installs the Playwright chromium browser,
# and creates .env from .env.example if .env does not already exist
# (never overwrites an existing .env - your real credentials are safe
# to run this again after a `git pull`).
#
# Usage (from the repo root, in PowerShell):
#   .\scripts\setup.ps1
#
# Safe to re-run any time - every step below only acts if the thing it
# would create/install isn't already there.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "== QA Automation setup (Windows) ==" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"

# 1. Python version check (3.11+ - matches the interpreter this project is
# validated against; an older interpreter can still work but is untested).
function Get-PythonCommand {
    foreach ($candidate in @("python", "py")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) { return $candidate }
    }
    return $null
}

$pythonCmd = Get-PythonCommand
if (-not $pythonCmd) {
    Write-Host "ERROR: Python was not found on PATH. Install Python 3.11+ from https://python.org/downloads/ (check 'Add python.exe to PATH' during install), then re-run this script." -ForegroundColor Red
    exit 1
}

$versionOutput = & $pythonCmd --version 2>&1
Write-Host "Found: $versionOutput"
if ($versionOutput -match "Python (\d+)\.(\d+)") {
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        Write-Host "WARNING: Python $major.$minor detected - this project is validated on 3.11+. Continuing anyway, but upgrade if you hit odd errors." -ForegroundColor Yellow
    }
}

# 2. Virtual environment (create only if missing - re-running this script
# never touches an existing .venv's installed packages beyond step 3's
# idempotent `pip install`).
$venvPath = Join-Path $RepoRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at .venv ..."
    & $pythonCmd -m venv $venvPath
} else {
    Write-Host ".venv already exists - reusing it."
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"

# 3. Dependencies.
Write-Host "Installing Python dependencies from requirements.txt ..."
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $RepoRoot "requirements.txt")

# 4. Playwright browser binary (chromium only - the only browser this
# project drives; see BROWSER in .env).
Write-Host "Installing Playwright's chromium browser ..."
& $venvPython -m playwright install chromium

# 5. .env - never overwrite a real one.
$envPath = Join-Path $RepoRoot ".env"
$envExamplePath = Join-Path $RepoRoot ".env.example"
if (-not (Test-Path $envPath)) {
    if (Test-Path $envExamplePath) {
        Copy-Item $envExamplePath $envPath
        Write-Host "Created .env from .env.example - fill in BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD before running tests." -ForegroundColor Yellow
    } else {
        Write-Host "WARNING: .env.example not found - create .env by hand (see README.md > '.env Setup')." -ForegroundColor Yellow
    }
} else {
    Write-Host ".env already exists - leaving it untouched."
}

Write-Host ""
Write-Host "== Setup complete ==" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Activate the venv in new shells:  .venv\Scripts\activate"
Write-Host "  2. Edit .env with your real BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD"
Write-Host "  3. Run the suite:                    python run_tests.py"
Write-Host "See ALL_COMMANDS.md for the full command reference."
