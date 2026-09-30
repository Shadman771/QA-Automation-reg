import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (  # noqa: E402
    HEADLESS, BROWSER, BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD, REPORTS_DIR,
    DEPLOYMENT_SUCCESS_THRESHOLD,
)
from utils.screenshot import capture, finalize_evidence  # noqa: E402
from utils.failure_log import write_failure_log  # noqa: E402
from utils.excel_utils import write_feature_excel  # noqa: E402
from utils.report_utils import build_html_report  # noqa: E402
from utils import dashboard  # noqa: E402
from utils.session import ensure_session_cached  # noqa: E402

SESSION_RESULTS = []
SESSION_START = None
DASHBOARD_PORT = None


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {**browser_type_launch_args, "headless": HEADLESS, "slow_mo": 0 if HEADLESS else 120}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1440, "height": 900}}


@pytest.fixture(scope="session")
def _auth_state_path(browser):
    """Logs in once per pytest session (or reuses a still-valid cached
    session) - see utils/session.py. Session-scoped so a full module/suite
    run only pays the real login UI flow once, not once per test case.
    Reuses pytest-playwright's own session-scoped `browser` fixture rather
    than launching a second Playwright instance."""
    return ensure_session_cached(browser)


@pytest.fixture
def page(browser, browser_context_args, _auth_state_path):
    """Default `page` fixture: every feature/module test starts from an
    already-authenticated context (storage_state reuse), instead of each
    test repeating the login UI flow. tests/login/ overrides this back to
    a fresh, unauthenticated context via its own conftest.py, since those
    tests exercise the login flow itself."""
    context = browser.new_context(storage_state=str(_auth_state_path), **browser_context_args)
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture
def result(page):
    def _record(case, actual: str, ok: bool, failed_step: str = "", expected: str = ""):
        screenshot_path = capture(page, case.feature, case.id, ok)
        evidence = finalize_evidence(case.evidence, case.feature, case.id, ok)
        entry = {
            "id": case.id,
            "feature": case.feature,
            "title": case.title,
            "description": case.description,
            "precondition": case.precondition,
            "test_data": case.test_data,
            "steps": case.steps,
            "expected": expected or case.description,
            "actual": actual,
            "assertions": case.assertions,
            "result": "PASS" if ok else "FAIL",
            "screenshot": str(screenshot_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "evidence": evidence,
        }
        SESSION_RESULTS.append(entry)
        if not ok:
            last_assertion = case.assertions[-1]["text"] if case.assertions else "-"
            write_failure_log(
                case.feature, case.id, case.title,
                failed_step or last_assertion,
                expected or case.description, actual, last_assertion,
                url=page.url,
            )
        dashboard.finish_case(entry["result"])
        return entry
    return _record


@pytest.fixture
def blocked(page):
    """Records a BLOCKED case: the test case cannot be validated (e.g. an
    incomplete source spec) rather than failed."""
    def _record(case, reason: str):
        screenshot_path = None
        try:
            screenshot_path = capture(page, case.feature, case.id, False)
        except Exception:
            pass
        try:
            evidence = finalize_evidence(case.evidence, case.feature, case.id, False)
        except Exception:
            evidence = []
        entry = {
            "id": case.id,
            "feature": case.feature,
            "title": case.title,
            "description": case.description,
            "precondition": case.precondition,
            "test_data": case.test_data,
            "steps": case.steps,
            "expected": case.description,
            "actual": f"BLOCKED - {reason}",
            "assertions": case.assertions,
            "result": "BLOCKED",
            "screenshot": str(screenshot_path.relative_to(PROJECT_ROOT)).replace("\\", "/") if screenshot_path else "",
            "evidence": evidence,
        }
        SESSION_RESULTS.append(entry)
        dashboard.finish_case("BLOCKED")
        return entry
    return _record


def pytest_sessionstart(session):
    global SESSION_START, DASHBOARD_PORT
    SESSION_START = time.time()
    DASHBOARD_PORT = dashboard.start_server()
    if DASHBOARD_PORT:
        print(f"\nLive dashboard: http://127.0.0.1:{DASHBOARD_PORT}/dashboard.html  (opening in your browser)")
        dashboard.open_browser(DASHBOARD_PORT)
    else:
        print("\nLive dashboard: could not bind a local port - continuing without it.")


def pytest_collection_finish(session):
    dashboard.init_session(len(session.items), BASE_URL, LOGIN_EMAIL)


def pytest_sessionfinish(session, exitstatus):
    if not SESSION_RESULTS:
        return

    end = time.time()
    duration = end - (SESSION_START or end)

    by_feature = {}
    for c in SESSION_RESULTS:
        by_feature.setdefault(c["feature"], []).append(c)
    for feature, cases in by_feature.items():
        write_feature_excel(feature, cases)

    import json
    (REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "execution_results.json").write_text(
        json.dumps(SESSION_RESULTS, indent=2), encoding="utf-8"
    )

    total = len(SESSION_RESULTS)
    passed = sum(1 for c in SESSION_RESULTS if c["result"] == "PASS")
    failed = sum(1 for c in SESSION_RESULTS if c["result"] == "FAIL")
    blocked_n = sum(1 for c in SESSION_RESULTS if c["result"] == "BLOCKED")
    executed = passed + failed
    pass_rate = round((passed / executed * 100), 2) if executed else 0.0

    meta = {
        "title": "QA Automation Report - Regplus World Tax Analyzer",
        "app_url": BASE_URL,
        "env_line": f"Account: {LOGIN_EMAIL}",
        "start": datetime.fromtimestamp(SESSION_START).strftime("%Y-%m-%d %H:%M:%S"),
        "end": datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S"),
        "duration": f"{duration:.1f}s",
        "browser": f"{BROWSER} ({'headless' if HEADLESS else 'headed'})",
        "mode": "headless" if HEADLESS else "headed",
        "deployment_threshold": DEPLOYMENT_SUCCESS_THRESHOLD,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    report_path = build_html_report(SESSION_RESULTS, meta, REPORTS_DIR / "automation_report.html")

    # Credential scan: the report must never contain the plaintext password.
    report_text = report_path.read_text(encoding="utf-8")
    if LOGIN_PASSWORD and LOGIN_PASSWORD in report_text:
        raise RuntimeError(
            f"SECURITY: the generated report at {report_path} contains the plaintext "
            "LOGIN_PASSWORD from .env. A test case must have echoed it into test_data/"
            "actual text - fix the offending test before this report is published."
        )

    dashboard.finish_session()

    report_uri = report_path.resolve().as_uri()
    print("\n" + "=" * 60)
    print("QA EXECUTION COMPLETED")
    print("=" * 60)
    print(f"Total Test Cases: {total}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Blocked: {blocked_n}")
    print(f"Pass Rate: {pass_rate}%")
    deployment_ok = executed > 0 and pass_rate >= DEPLOYMENT_SUCCESS_THRESHOLD
    print(f"Deployment Status: {'DEPLOYMENT SUCCESSFUL' if deployment_ok else 'DEPLOYMENT BLOCKED'} "
          f"(threshold: {DEPLOYMENT_SUCCESS_THRESHOLD}%)")
    print(f"HTML Report: {report_path}")
    print(f"Open it:   {report_uri}")
    if DASHBOARD_PORT:
        print(f"Live Dashboard was at: http://127.0.0.1:{DASHBOARD_PORT}/dashboard.html")

    import webbrowser
    try:
        webbrowser.open(report_uri)
    except Exception:
        pass
    print("=" * 60)

    # Best-effort publish to GitHub Pages so there's a stable public link,
    # not just the local file path - see utils/publish.py and README.md >
    # "Public report link". Never fails the run if publishing doesn't work
    # (no network, stale git credentials, etc.).
    from utils.publish import publish_report
    public_url = publish_report(report_path)

    print()
    print("=" * 60)
    print("              QA AUTOMATION EXECUTION COMPLETED")
    print("=" * 60)
    print()
    if failed == 0 and blocked_n == 0:
        print("[OK] Test Execution Completed Successfully")
    else:
        print(f"[!!] Test Execution Completed - {failed} Failed, {blocked_n} Blocked")
    print()
    print("Final Report:")
    if public_url:
        print(f"  Public: {public_url}")
    else:
        print("  Public: not published this run (see README.md > 'Public report link')")
    print(f"  Local:  {report_uri}")
    print()
    print("Click the link above to open the report directly.")
    print("=" * 60)
