"""Calculator-only fixture override: a WIDER viewport than the project
default - same real, live-confirmed application defect and same
directory-local fixture-override pattern as tests/treaties/conftest.py and
tests/tools/conftest.py (see tests/treaties/conftest.py's docstring for the
full write-up): "Calculators" (along with "Treaties", "Tools" and "BEPS")
is completely ABSENT from the DOM below ~1600px viewport width and there is
no responsive fallback. This suite runs at the same 1680x900 viewport those
modules use so every Calculator page can be exercised end-to-end without
weakening any assertion."""
import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1680, "height": 900}}
