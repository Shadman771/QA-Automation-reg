"""Login's own tests must start from a genuinely unauthenticated context -
they exercise the login page/flow itself (invalid credentials, empty
submit, masked password, etc.). This overrides the root conftest.py's
session-reuse `page` fixture back to a plain, fresh, unauthenticated
context per test (pytest-playwright's default behavior) for this
directory only."""
import pytest

from config.settings import DEFAULT_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS


@pytest.fixture
def page(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    pg = context.new_page()
    pg.set_default_timeout(DEFAULT_TIMEOUT_MS)
    pg.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    yield pg
    context.close()
