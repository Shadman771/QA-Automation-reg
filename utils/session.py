"""Authenticated-session reuse.

Logs in once, using the SAME `browser` object pytest-playwright already
launches for the test session (never a second, separately-managed
Playwright instance - nesting `sync_playwright()` inside pytest-playwright's
own event loop raises "Sync API inside the asyncio loop"), and caches the
resulting storage_state (cookies + localStorage) to disk under
.auth/state.json. The root conftest.py's `page` fixture then loads every
feature/module test's context from that cached state, so a full module run
performs the real login UI flow once instead of once per test case. If the
cached state has gone stale (expired session), it's regenerated
automatically.

tests/login/ deliberately opts out of this (see its own conftest.py) since
those tests exercise the login page/flow itself and must start from a
genuinely unauthenticated context.
"""
from pathlib import Path

from config.settings import BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD, PROJECT_ROOT

AUTH_DIR = PROJECT_ROOT / ".auth"
AUTH_STATE_PATH = AUTH_DIR / "state.json"

# Login redirects to /wta/Information (see pages/login_page.py, tests/login).
# Reused here as a stable "am I actually logged in" probe URL.
AUTHENTICATED_HOME = BASE_URL.split("/auth/")[0] + "/wta/Information"


def wait_for_login_sync(page, timeout_ms: int = 30000) -> bool:
    """Waits out the app's own post-login provisioning screen ("Syncing
    with Enterprise Cloud...", "Hold on, getting things ready for you...")
    instead of assuming a fixed short wait is enough. Confirmed live this
    can take ~11s on the Live environment - a fixed 1s wait (the previous
    implementation) reliably mis-detected a real, successful login as
    failed because the app was still mid-provisioning, not actually stuck
    on /auth/login. Polls for either a stable authenticated state (no
    longer /auth/login AND the sync banner is gone) or timeout. Returns
    True if authenticated-looking, False if still on /auth/login at
    timeout (a genuine failure, not a slow one)."""
    import time
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            syncing = page.get_by_text("Syncing with Enterprise Cloud", exact=False).count() > 0
        except Exception:
            syncing = False
        if not syncing and "/auth/login" not in page.url:
            return True
        page.wait_for_timeout(500)
    return "/auth/login" not in page.url


def _state_is_valid(browser) -> bool:
    if not AUTH_STATE_PATH.exists():
        return False
    context = None
    try:
        context = browser.new_context(storage_state=str(AUTH_STATE_PATH))
        page = context.new_page()
        # "domcontentloaded", not "networkidle" - see utils/auth.py's
        # perform_login() for why: this app's authenticated pages keep
        # persistent background requests going that can prevent true
        # network-idle from ever being reached.
        page.goto(AUTHENTICATED_HOME, wait_until="domcontentloaded", timeout=20000)
        return wait_for_login_sync(page, timeout_ms=15000)
    except Exception:
        return False
    finally:
        if context is not None:
            context.close()


def _login_and_cache(browser) -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    try:
        page = context.new_page()
        # "domcontentloaded", not "networkidle" - see utils/wait.py. Waits
        # explicitly for the email field itself to be ready rather than
        # assuming the navigation wait alone means the login form has
        # rendered.
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.locator("#email").wait_for(state="visible", timeout=20000)
        page.locator("#email").fill(LOGIN_EMAIL)
        page.locator("#password").fill(LOGIN_PASSWORD)
        page.locator('button[type="submit"]').click()
        authenticated = wait_for_login_sync(page)
        if not authenticated:
            raise RuntimeError(
                f"Session-cache login failed: still on {page.url} after submitting "
                f".env credentials and waiting out the post-login sync screen. "
                f"Check .env / the live app."
            )
        context.storage_state(path=str(AUTH_STATE_PATH))
    finally:
        context.close()


def ensure_session_cached(browser) -> Path:
    """Returns a path to a valid storage_state file, logging in once (and
    only once) if no still-valid cached session exists. `browser` must be
    pytest-playwright's own session-scoped Browser fixture - see
    conftest.py::_auth_state_path."""
    if not _state_is_valid(browser):
        _login_and_cache(browser)
    return AUTH_STATE_PATH
