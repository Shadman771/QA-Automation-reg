"""Shared per-test authentication helper.

Every feature/module test's `page` fixture already starts from a cached,
authenticated context (see utils/session.py + conftest.py::page) - so in
the normal case this just confirms that and logs the step, without
repeating the login UI flow. If the cached session has somehow gone stale
mid-run, it falls back to a real login so the test still passes rather than
failing on a session it can silently recover from.

The fallback login's outcome is explicitly verified (confirmed live as a
real, previously-unguarded gap: the fallback could fail - wrong .env
credentials, the login page itself broken, a slow/unavailable environment
- and every test would silently carry on with an unauthenticated page,
surfacing much later as a confusing, unrelated-looking assertion failure
deep inside the test instead of a clear "authentication failed" signal).
On a genuine failure this raises AuthenticationError, which
conftest.py's pytest_runtest_makereport hook converts into a BLOCKED
report entry automatically for every test that calls perform_login - no
per-test-file changes needed."""
from config.settings import LOGIN_EMAIL, LOGIN_PASSWORD
from pages.login_page import LoginPage
from pages.landing_page import LandingPage
from utils.session import AUTHENTICATED_HOME, wait_for_login_sync


class AuthenticationError(RuntimeError):
    """Raised when perform_login() cannot establish an authenticated
    session. Carries the live `case` so conftest.py's makereport hook can
    record a proper BLOCKED entry (screenshot, evidence, reason) without
    needing the test itself to catch anything."""
    def __init__(self, case, reason: str):
        super().__init__(reason)
        self.case = case
        self.reason = reason


def perform_login(case, page, dismiss_cookies: bool = True):
    """dismiss_cookies=False for tests (e.g. LANDING_04) that specifically
    need to observe/interact with the still-undismissed cookie banner
    themselves."""
    case.step(1, "Ensure an authenticated session (reused across this module's test cases)")
    case.action("Navigating to the workspace", kind="navigate")
    # "domcontentloaded", not "networkidle": this app keeps persistent
    # background requests going on /wta/Information (notification polling,
    # analytics, etc.) that can prevent true network-idle from ever being
    # reached - confirmed live as a real, reproducible 30s navigation
    # timeout, not a slow-network flake. wait_for_login_sync() below is the
    # actual "is the app ready" check; the navigation wait only needs the
    # document itself to have loaded.
    page.goto(AUTHENTICATED_HOME, wait_until="domcontentloaded")
    wait_for_login_sync(page, timeout_ms=15000)

    if "/auth/login" in page.url:
        case.action("Cached session was invalid/expired - logging in", kind="navigate")
        login_page = LoginPage(page)
        login_page.goto()
        case.fill(login_page.email, LOGIN_EMAIL, "Email field")
        case.fill(login_page.password, LOGIN_PASSWORD, "Password field", mask=True)
        case.click(login_page.submit, "Log In button")
        authenticated = wait_for_login_sync(page)

        if not authenticated:
            banner = ""
            try:
                banner = login_page.wait_for_banner(timeout=2000)
            except Exception:
                pass
            raise AuthenticationError(
                case,
                f"Login did not complete - still on {page.url} after submitting .env credentials"
                + (f" (banner: '{banner}')" if banner else " (no error banner detected)."),
            )
    else:
        case.action("Reusing the existing authenticated session", kind="verify")

    if dismiss_cookies:
        LandingPage(page).accept_cookies_if_present()
