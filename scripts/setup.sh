#!/usr/bin/env bash
# macOS / Linux setup script for the QA Automation framework.
#
# What this does, in order: checks Python 3.11+, creates/reuses .venv,
# installs requirements.txt, installs the Playwright chromium browser,
# and creates .env from .env.example if .env does not already exist
# (never overwrites an existing .env - your real credentials are safe
# to run this again after a `git pull`).
#
# Usage (from the repo root):
#   bash scripts/setup.sh
#
# Safe to re-run any time - every step below only acts if the thing it
# would create/install isn't already there.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "== QA Automation setup (macOS/Linux) =="
echo "Repo root: $REPO_ROOT"
echo "OS: $(uname -s)"

# 1. Python version check (3.11+ - matches the interpreter this project is
# validated against; an older interpreter can still work but is untested).
PYTHON_CMD=""
for candidate in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_CMD="$candidate"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: no python interpreter found on PATH."
    if [[ "$(uname -s)" == "Darwin" ]]; then
        echo "Install Python 3.11+ via: brew install python@3.11"
        echo "(or from https://python.org/downloads/ if you don't use Homebrew)"
    else
        echo "Install Python 3.11+ via your distro's package manager, e.g.: sudo apt install python3.11 python3.11-venv"
    fi
    exit 1
fi

VERSION_OUTPUT="$("$PYTHON_CMD" --version 2>&1)"
echo "Found: $VERSION_OUTPUT"
MAJOR=$(echo "$VERSION_OUTPUT" | sed -E 's/Python ([0-9]+)\.([0-9]+).*/\1/')
MINOR=$(echo "$VERSION_OUTPUT" | sed -E 's/Python ([0-9]+)\.([0-9]+).*/\2/')
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
    echo "WARNING: Python $MAJOR.$MINOR detected - this project is validated on 3.11+. Continuing anyway, but upgrade if you hit odd errors."
fi

# 2. Virtual environment (create only if missing - re-running this script
# never touches an existing .venv's installed packages beyond step 3's
# idempotent `pip install`).
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment at .venv ..."
    "$PYTHON_CMD" -m venv .venv
else
    echo ".venv already exists - reusing it."
fi

VENV_PYTHON=".venv/bin/python"

# 3. Dependencies.
echo "Installing Python dependencies from requirements.txt ..."
"$VENV_PYTHON" -m pip install --upgrade pip --quiet
"$VENV_PYTHON" -m pip install -r requirements.txt

# 4. Playwright browser binary (chromium only - the only browser this
# project drives; see BROWSER in .env).
echo "Installing Playwright's chromium browser ..."
"$VENV_PYTHON" -m playwright install chromium
# Playwright's own OS-level dependency installer - safe to skip if it
# fails without sudo access; the browser binary above is the part that's
# actually required.
"$VENV_PYTHON" -m playwright install-deps chromium 2>/dev/null || \
    echo "(skipped install-deps - may need 'sudo python -m playwright install-deps chromium' if the browser fails to launch)"

# 5. .env - never overwrite a real one.
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example - fill in BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD before running tests."
    else
        echo "WARNING: .env.example not found - create .env by hand (see README.md > '.env Setup')."
    fi
else
    echo ".env already exists - leaving it untouched."
fi

echo ""
echo "== Setup complete =="
echo "Next steps:"
echo "  1. Activate the venv in new shells:  source .venv/bin/activate"
echo "  2. Edit .env with your real BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD"
echo "  3. Run the suite:                    python run_tests.py"
echo "See ALL_COMMANDS.md for the full command reference."
