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
DEPLOYMENT_SUCCESS_THRESHOLD = float(os.getenv("DEPLOYMENT_SUCCESS_THRESHOLD", "95"))

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

if not BASE_URL or not LOGIN_EMAIL or not LOGIN_PASSWORD:
    raise RuntimeError(
        "BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD must be set in .env "
        "(see .env.example)."
    )
