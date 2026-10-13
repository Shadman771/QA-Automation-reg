"""Single entry point for the QA_Automation suite.

    python run_tests.py                     # everything (Final Suite)
    python run_tests.py --feature Login      # one feature only
    python run_tests.py --feature Dashboard
    python run_tests.py --test LOGIN_04      # one Test Case ID
    python run_tests.py --smoke              # smoke suite only
    python run_tests.py --regression         # regression suite only
    python run_tests.py --headed             # visible browser (overrides .env)
    python run_tests.py --headless           # headless (overrides .env)
    python run_tests.py --keep               # do not clean previous runtime data first

The HTML report and per-feature Excel files are (re)generated at the end of
every run; the terminal prints the final report path.
"""
import argparse
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Parent module -> main feature -> subfeature/page -> test cases, mirrored
# physically: tests/wta/<feature>/, pages/wta/<feature>_page.py,
# test_data/WTA/<Feature>/. "login" and "dashboard" sit OUTSIDE the "wta"
# parent module - they're the pre-product/platform shell (auth, the
# post-login landing page's product picker), not part of the World Tax
# Analyzer product itself. Future parent modules (e.g. a "tpa" module for
# Transfer Pricing Analyzer) would get their own tests/<module>/,
# pages/<module>/, test_data/<MODULE>/ siblings of "wta" here, following
# the exact same pattern - see AGENT.md.
WTA_FEATURE_PATHS = {
    "information": "tests/wta/information",
    "pillar2": "tests/wta/pillar2",
    "news": "tests/wta/news",
    "forms": "tests/wta/forms",
    "regulations": "tests/wta/regulations",
    "treaties": "tests/wta/treaties",
    "tools": "tests/wta/tools",
    "calculator": "tests/wta/calculator",
}

FEATURE_PATHS = {
    "login": "tests/login",
    "dashboard": "tests/dashboard",
    "wta": "tests/wta",  # every WTA feature at once - the parent module
    **WTA_FEATURE_PATHS,
}


def main():
    parser = argparse.ArgumentParser(description="Run the QA_Automation Playwright suite.")
    parser.add_argument("--feature", help="Run one feature only, e.g. --feature Login")
    parser.add_argument("--test", help="Run one Test Case ID, e.g. --test LOGIN_04")
    parser.add_argument("--smoke", action="store_true", help="Run only @pytest.mark.smoke tests")
    parser.add_argument("--regression", action="store_true", help="Run only @pytest.mark.regression tests")
    parser.add_argument("--headed", action="store_true", help="Force a visible browser")
    parser.add_argument("--headless", action="store_true", help="Force headless")
    parser.add_argument("--keep", action="store_true", help="Keep previous run's screenshots/logs/report")
    args, extra = parser.parse_known_args()

    if not args.keep:
        from utils.cleanup import clean_runtime
        clean_runtime()

    if args.headed:
        os.environ["HEADLESS"] = "false"
    if args.headless:
        os.environ["HEADLESS"] = "true"

    pytest_args = ["-v", "--color=yes"]

    if args.test:
        pytest_args += ["-k", args.test.strip().lower()]
        print("Running single test case: %s" % args.test)
    elif args.feature:
        key = args.feature.strip().lower()
        module = FEATURE_PATHS.get(key)
        if not module:
            print("Unknown feature '%s'. Known features: %s" % (args.feature, ", ".join(FEATURE_PATHS)))
            return 2
        pytest_args.append(module)
        print("Running feature: %s" % args.feature)
    else:
        pytest_args.append("tests")
        print("Running the FULL SUITE: %s" % ", ".join(FEATURE_PATHS))

    if args.smoke:
        pytest_args += ["-m", "smoke"]
    elif args.regression:
        pytest_args += ["-m", "regression"]

    pytest_args += extra
    print("=" * 60)
    print("QA AUTOMATION - PLAYWRIGHT + PYTEST")
    print("=" * 60)
    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main())
