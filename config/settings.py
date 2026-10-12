"""Central configuration, read from .env. Changing .env changes the next run
without touching this file."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = os.getenv("BASE_URL", "").strip()

# The app's origin (scheme + host, no path) derived from BASE_URL - e.g.
# "https://regplus.kaz.com.bd" from "https://regplus.kaz.com.bd/auth/login/".
# Every page object's goto() must build its URL from this, never hardcode a
# domain: a hardcoded "https://regplus.kaz.com.bd/wta/..." silently ignores
# a different BASE_URL (confirmed live - the exact bug that caused
# .env's BASE_URL change to a different environment to not take effect,
# surfacing as "it logs in fine, then redirects to the old domain" on any
# page object that still had its old literal URL).
APP_ORIGIN = BASE_URL.split("/auth/")[0] if BASE_URL else ""

LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "").strip()
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "").strip()
HEADLESS = os.getenv("HEADLESS", "false").strip().lower() == "true"
BROWSER = os.getenv("BROWSER", "chromium").strip()
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))

# Centralized Playwright timeouts (applied in conftest.py's `page` fixture
# to EVERY action/locator and navigation project-wide via
# page.set_default_timeout()/set_default_navigation_timeout() - confirmed
# live this was previously dead config: TIMEOUT above was read but never
# actually applied anywhere, so every call silently used Playwright's
# built-in 30s default instead of anything in .env).
DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("NAVIGATION_TIMEOUT_MS", "30000"))
ASSERTION_TIMEOUT_MS = int(os.getenv("ASSERTION_TIMEOUT_MS", "15000"))

DEPLOYMENT_SUCCESS_THRESHOLD = float(
    os.getenv("DEPLOYMENT_SUCCESS_THRESHOLD", os.getenv("SUCCESS_THRESHOLD", "95"))
)

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

if not BASE_URL or not LOGIN_EMAIL or not LOGIN_PASSWORD:
    raise RuntimeError(
        "BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD must be set in .env "
        "(see .env.example)."
    )
