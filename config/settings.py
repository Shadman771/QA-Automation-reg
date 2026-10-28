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
# 60000, not 15000: same confirmed-live slow-environment reasoning as
# ASSERTION_TIMEOUT_MS below - this governs every click()/fill() project-wide
# (via page.set_default_timeout()), and on a slow account/environment an
# element can legitimately still be unactionable up to ~60s after
# navigation, not just the one heading verify_visible() checks.
DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "60000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("NAVIGATION_TIMEOUT_MS", "30000"))
# 60000, not 15000: confirmed live (direct, timed, isolated reproduction
# against the Live environment/account) that loading a cached session cold
# (the normal per-test path once a module's first test has logged in) can
# take up to ~60s for real page content to actually render, even though the
# app's own "Syncing with Enterprise Cloud" banner text disappears from the
# DOM within ~1-4s - that banner clearing is NOT a reliable "content is
# ready" signal (see utils/session.py::wait_for_login_sync), so
# Case.verify_visible() - the one place that genuinely waits for real
# visible content - needs a ceiling long enough to not time out before
# slower accounts/environments legitimately finish rendering. This does not
# weaken any assertion: it still requires the real element to actually
# become visible, it just stops giving up early on a confirmed-real, slower
# live environment.
ASSERTION_TIMEOUT_MS = int(os.getenv("ASSERTION_TIMEOUT_MS", "60000"))

DEPLOYMENT_SUCCESS_THRESHOLD = float(
    os.getenv("DEPLOYMENT_SUCCESS_THRESHOLD", os.getenv("SUCCESS_THRESHOLD", "95"))
)

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

# The only features OUTSIDE any parent module - the platform/pre-product
# shell (login, the post-login landing page's product picker). These
# nest directly under base/<Feature>, no module segment.
PLATFORM_FEATURES = {"Login", "Dashboard"}

# Real module lookup (generalized from the old two-way platform/WTA split,
# per this file's own prior TODO): every feature belonging to a parent
# module OTHER than WTA must be listed here under that module's segment
# name, matching its own tests/<module>/, pages/<module>/ structure. A
# feature NOT in PLATFORM_FEATURES and NOT listed here defaults to "WTA" -
# preserves identical behavior for every pre-existing WTA feature without
# needing to enumerate them all.
OTHER_MODULE_FEATURES = {
    "RegBriefings": {
        "RegBriefings Menu",
        "RegBriefings My Briefs",
        "RegBriefings World Tax Brief",
        "RegBriefings Transfer Pricing Brief",
        "RegBriefings Tax Treaty Brief",
        "RegBriefings Archive",
        "RegBriefings Preferences",
    },
}


def feature_dir(base: Path, feature: str) -> Path:
    """base/<Feature> for a platform-level feature, base/<Module>/<Feature>
    for a feature belonging to a registered parent module (see
    OTHER_MODULE_FEATURES), base/WTA/<Feature> otherwise - the one shared
    rule every feature-keyed output directory (test_data, screenshots,
    logs) should use."""
    if feature in PLATFORM_FEATURES:
        return base / feature
    for module_name, features in OTHER_MODULE_FEATURES.items():
        if feature in features:
            return base / module_name / feature
    return base / "WTA" / feature

if not BASE_URL or not LOGIN_EMAIL or not LOGIN_PASSWORD:
    raise RuntimeError(
        "BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD must be set in .env "
        "(see .env.example)."
    )
