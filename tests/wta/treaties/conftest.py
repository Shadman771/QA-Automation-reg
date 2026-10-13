"""Treaties-only fixture override: a WIDER viewport than the project default.

Confirmed live (scripts/discover_treaties5.py, discover_treaties6.py -
throwaway, not part of the suite) as a genuine, reproducible application
defect: the "Treaties" top-nav item (along with "Calculators", "Tools" and
"BEPS") is completely ABSENT from the DOM - not just hidden - at the
project's default 1440x900 viewport (`browser_context_args` in the root
`conftest.py`). It only appears once the viewport is >= ~1600px wide
(confirmed: 0 matches at 1440/1500, 1 match at 1600/1700), and there is no
overflow/hamburger/"More" control that exposes it at the narrower width -
those 4 nav items are simply unreachable for a real user on a common
1440-wide laptop screen. This is documented as a real, live-confirmed
application defect (see the final test run report), not an automation
workaround to hide it.

Since the Treaties FEATURE itself still needs to be exercised end-to-end,
this directory's tests run at a wider 1680x900 viewport (this project's
existing convention for a directory-local fixture override -
tests/login/conftest.py does the same for its own reason). This does not
weaken any assertion; it only changes the window size the Treaties
suite drives the real, live application at, the same way a human tester
would maximize their browser to reach the same nav item."""
import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1680, "height": 900}}
