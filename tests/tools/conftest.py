"""Tools-only fixture override: a WIDER viewport than the project default -
same real, live-confirmed application defect and same directory-local
fixture-override pattern as tests/treaties/conftest.py (see that file's
docstring for the full write-up): "Tools" (along with "Treaties",
"Calculators" and "BEPS") is completely ABSENT from the DOM below ~1600px
viewport width and there is no responsive fallback. Confirmed for "Tools"
specifically: 0 matches at 1440/1500, 1 match at 1600/1700. This suite runs
at the same 1680x900 viewport Treaties uses so the Tools module can be
exercised end-to-end without weakening any assertion."""
import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1680, "height": 900}}
