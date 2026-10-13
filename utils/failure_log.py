"""Detailed developer-facing failure report, written only for FAIL/BLOCKED
test cases (see README > Failure diagnostics)."""
from pathlib import Path

from config.settings import LOGS_DIR, feature_dir as _feature_dir

TEMPLATE = """========================================
FAILURE REPORT
========================================

Feature:        {feature}
Test Case ID:   {case_id}
Title:          {title}

FAILED STEP:
{failed_step}

EXPECTED:
{expected}

ACTUAL:
{actual}

ASSERTION:
{assertion}

CONSOLE ERRORS:
{console_errors}

PAGE STATE:
URL: {url}

ROOT-CAUSE INVESTIGATION:
{root_cause}

========================================
"""


def write_failure_log(feature: str, case_id: str, title: str, failed_step: str,
                       expected: str, actual: str, assertion_text: str,
                       url: str = "", console_errors=None, root_cause: str = "Not investigated."):
    out_dir = _feature_dir(LOGS_DIR, feature)
    out_dir.mkdir(parents=True, exist_ok=True)
    console_block = "\n".join(console_errors) if console_errors else "None captured."
    content = TEMPLATE.format(
        feature=feature, case_id=case_id, title=title, failed_step=failed_step,
        expected=expected, actual=actual, assertion=assertion_text,
        console_errors=console_block, url=url, root_cause=root_cause,
    )
    out = out_dir / f"{case_id}_failure.log"
    out.write_text(content, encoding="utf-8")
    return out
