# All Commands

Copy-paste reference. Run everything from the `QA_Automation/` folder with the
venv activated:

```bash
cd QA_Automation
.venv\Scripts\activate      # Windows
```

## First-Time Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env      # then fill in BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD
```

## `.env` Setup

Edit `.env` in this folder:

```env
BASE_URL=https://your-app/auth/login/
LOGIN_EMAIL=you@example.com
LOGIN_PASSWORD=your-password
HEADLESS=false
DEPLOYMENT_SUCCESS_THRESHOLD=95
```

Any change here is picked up automatically on the next run - nothing else
needs editing. `DEPLOYMENT_SUCCESS_THRESHOLD` (default `95`) drives the
report's "Deployment Successful / Deployment Blocked" banner - the run's
pass rate is compared against it; no HTML/JS edits required to change it.

## Run Everything (Final Suite)

```bash
python run_tests.py
```

Runs every feature in `FEATURE_PATHS` (Login, Dashboard, Information,
Pillar2, News, Forms, Regulations, Treaties, Tools), cleans previous screenshots/logs/report
first, regenerates the HTML report and per-feature Excel files, and prints
the report path. Runs headed by default (`HEADLESS=false` in `.env`) and
opens the live dashboard (`http://127.0.0.1:8787/dashboard.html`)
automatically - see README.md > "Watching it run".

## Run One Feature

```bash
python run_tests.py --feature Login
python run_tests.py --feature Dashboard
python run_tests.py --feature Information      # WTA Information workspace
python run_tests.py --feature Pillar2           # Pillar 2 menu + all 6 sub-pages
python run_tests.py --feature News              # WTA News (top-level)
python run_tests.py --feature Forms             # WTA Forms (top-level)
python run_tests.py --feature Regulations       # WTA Regulations (top-level)
python run_tests.py --feature Treaties          # Treaties menu + all 5 sub-pages (Full DTA, PE Clause, Other Articles, WHT Rates, MLI Data)
python run_tests.py --feature Tools             # Tools menu + Projects + Questionnaire Creator
python run_tests.py --feature Calculator        # Calculators menu + Corporate Rate Finder
```

## Run One Test Case

```bash
python run_tests.py --test LOGIN_04
python run_tests.py --test LANDING_02
python run_tests.py --test Information_05
python run_tests.py --test P2Info_04
python run_tests.py --test FullDta_02
python run_tests.py --test MLIData_03
python run_tests.py --test Projects_03
python run_tests.py --test QuestionnaireCreator_05
```

## Run Smoke Suite

```bash
python run_tests.py --smoke
```

## Run Regression Suite

```bash
python run_tests.py --regression
```

## Headed / Headless

```bash
python run_tests.py --headed        # visible browser, overrides .env
python run_tests.py --headless      # no visible browser, overrides .env
```

## Keep Previous Runtime Data

```bash
python run_tests.py --keep          # skip the pre-run cleanup
```

## Session Reuse (login once per run, not once per test)

A run logs in once and caches the session to `.auth/state.json` (see
README.md > "Authentication / session reuse"); every subsequent test in
that run reuses it automatically - nothing to do. Delete `.auth/` (or just
let it expire) to force a fresh login on the next run:

```bash
rm -rf .auth
```

`tests/login/` is unaffected - it always starts unauthenticated, by design.

## Debug One Test with Playwright's Own Runner

```bash
python -m pytest tests/login/test_login.py::test_login_04_invalid_credentials -v -s
```

## Generated Artifacts (after any run)

```text
reports/automation_report.html         self-contained HTML report (final screenshot + per-step evidence gallery)
reports/execution_results.json         every recorded field, per test case (includes the "evidence" list)
test_data/<Feature>/<Feature>_Test_Cases.xlsx
screenshots/PASS/<Feature>/<CaseID>/<CaseID>.png            final full-page screenshot
screenshots/PASS/<Feature>/<CaseID>/step_NN_<kind>_<label>.png   per-step highlighted evidence
screenshots/FAIL/<Feature>/<CaseID>/...                      same layout, FAIL bucket
logs/<Feature>/<Feature>.log
logs/<Feature>/<CaseID>_failure.log     (only for FAIL/BLOCKED cases)
```

Every `Case.click` / `Case.fill` / `Case.verify_visible` / `Case.check(locator=...)` call captures a
small screenshot right after the element is red-highlighted (`utils/case.py::_capture_evidence`,
`utils/highlight.py`), staged under `screenshots/_pending/` until the case's PASS/FAIL outcome is known,
then moved into the final bucket by `utils/screenshot.py::finalize_evidence` (called from the `result`/
`blocked` fixtures in `conftest.py`). `utils/report_utils.py` renders that list as a "Step-by-Step
Evidence" gallery on each test case's report card, in addition to the final full-page screenshot.

## Adding a Feature

1. Add its page object under `pages/` (reuse `pages/wta_common.py`'s `JurisdictionPanel`/`CategoryTree`
   for any WTA module with the "Jurisdictions [and Categories/Filters]" left panel).
2. Add its tests under `tests/<feature>/`.
3. Add the feature to `FEATURE_PATHS` in `run_tests.py`.
4. `python run_tests.py --feature <Name>`

## Discovery scripts

There is no committed `scripts/discover.py` (the live DOM was inspected with throwaway Playwright
scripts run directly via `python`, per the file-header convention "locators came from a discovery
script, not guessed" that every `pages/*.py` file documents). To re-discover a page after a UI change,
write a short script that logs in (see any `pages/*_page.py` docstring for the login flow), navigates to
the page, and dumps `document.querySelectorAll(...)` / `page.evaluate(...)` results for the elements you
need, then update the relevant `pages/*.py` locator.
