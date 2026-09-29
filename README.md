# QA_Automation — Regplus World Tax Analyzer

Playwright + Pytest regression framework, built from the real application
(discovered via live browser inspection, not assumed markup). Current scope:
**Login**, the **post-login landing page/Dashboard**, and the **World Tax
Analyzer (WTA) module**: the **Information** workspace, all 6 **Pillar 2**
dropdown sub-pages (Information, Compliance Calendar, Forms, Simulator,
Country Commentary, Regulation, News), the top-level **News**,
**Forms** and **Regulations** modules, and all 5 **Treaties** dropdown
sub-pages (Full DTA, PE Clause, Other Articles, WHT Rates, MLI Data).

## Architecture

```text
QA_Automation/
├── tests/login/          Login test cases
├── tests/dashboard/      Landing page test cases
├── tests/wta_information/  WTA Information workspace test cases
├── tests/wta_pillar2/    Pillar 2 menu + all 6 sub-page test cases
├── tests/wta_news/       WTA News (top-level) test cases
├── tests/wta_forms/      WTA Forms (top-level) test cases
├── tests/wta_regulations/  WTA Regulations (top-level) test cases
├── tests/treaties/       Treaties menu + all 5 sub-page test cases
├── pages/                Page Object Model - login_page.py, landing_page.py,
│                         wta_common.py (shared JurisdictionPanel/CategoryTree),
│                         information_page.py, pillar2_menu.py,
│                         pillar2_information_page.py,
│                         pillar2_compliance_calendar_page.py,
│                         pillar2_forms_page.py,
│                         pillar2_country_commentary_page.py,
│                         pillar2_regulation_page.py, pillar2_news_page.py,
│                         news_page.py, forms_page.py, regulations_page.py,
│                         treaties_menu.py, treaties_full_dta_page.py,
│                         treaties_pe_clauses_page.py,
│                         treaties_other_articles_page.py,
│                         treaties_wht_rates_page.py, treaties_mli_data_page.py
├── utils/                logger, screenshot (+ per-step evidence),
│                         highlight, Excel writer, HTML report builder,
│                         failure-log writer, cleanup, Case model
├── test_data/            One Excel workbook per feature (generated)
├── screenshots/PASS|FAIL/<Feature>/<CaseID>/   final shot + per-step evidence
├── logs/<Feature>/       action log + failure logs
├── reports/              automation_report.html + execution_results.json
├── config/settings.py    reads .env
├── conftest.py           fixtures, session-level report/Excel/summary
├── run_tests.py          entry point (see ALL_COMMANDS.md)
└── .env                  BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD / HEADLESS
```

## How a test case is built

Every test:
1. Builds a `Case` (utils/case.py) with the ID, title, description,
   precondition, test data and steps.
2. Drives the app through a page object.
3. Calls `case.check(...)` for each meaningful assertion (logged live).
4. Calls the `result(...)` fixture, which screenshots the page, writes the
   Excel/report row, and — on failure — writes a failure log.
5. Asserts `ok` so pytest reports the real pass/fail.

Nothing here is a placeholder: every locator in `pages/login_page.py` and
`pages/landing_page.py` came from inspecting the live DOM, and every
"Actual Result" is generated from what the browser actually returned.

## Watching it run

- `HEADLESS=false` by default (`.env`) - the browser is visible.
- Every run opens a **live dashboard** in your default browser
  (`http://127.0.0.1:8787/dashboard.html`, port auto-increments if busy):
  overall progress bar, pass/fail/blocked counts, the current test case's
  step list (pending → running → done), the current action (click/type/
  navigate/verify), the current assertion (pass/fail), and a live scrolling
  log - all polling `reports/live_state.json` every 400ms.
- In the actual test browser, the exact element being clicked, typed into,
  or verified is outlined in **red** for a moment before the action fires
  (`utils/highlight.py`), so you can follow the automation visually.
- Every one of those highlighted moments is also saved as a **per-step
  evidence screenshot** (`utils/case.py::Case._capture_evidence`), staged
  under `screenshots/_pending/` and moved into the case's PASS/FAIL bucket
  once its outcome is known (`utils/screenshot.py::finalize_evidence`,
  wired up in `conftest.py`'s `result`/`blocked` fixtures). The HTML report
  renders that full list as a labeled "Step-by-Step Evidence" gallery on
  each test case's card (`utils/report_utils.py`), alongside the final
  full-page screenshot - so the red highlight from every step, not just
  whatever was on screen at the very end, is visible in the saved evidence.

## Authentication / session reuse

A full module or suite run logs in **once**, not once per test case.
`conftest.py`'s `_auth_state_path` (session-scoped) calls
`utils/session.py::ensure_session_cached()`, which logs in through the real
UI (reusing pytest-playwright's own `browser` fixture - never a second
Playwright instance) and caches the resulting `storage_state` (cookies +
localStorage) to `.auth/state.json`. The default `page` fixture then builds
every test's context from that cached state, so each test starts already
authenticated instead of repeating the login form. If the cached session
has gone stale, it's detected and refreshed automatically (`_state_is_valid`
probes `/wta/Information` before trusting the cache).

Every non-Login test's `_login`/`_login_and_open` helper now just calls
`utils/auth.py::perform_login(case, page)`, which confirms the session (and
falls back to a real login only if it isn't already authenticated) - see
that module's docstring. This cut the full 64-case suite from ~9m17s to
~7m06s in testing.

`tests/login/conftest.py` overrides the `page` fixture back to a plain,
fresh, unauthenticated context for that directory only - those tests
exercise the login page/flow itself (invalid credentials, empty submit,
masked password, valid-credentials redirect) and must never start
pre-authenticated. `.auth/` is gitignored.

## Setup & running

See [ALL_COMMANDS.md](ALL_COMMANDS.md) for every command. Quick start:

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env      # fill in BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD
python run_tests.py
```

## Credentials

Read only from `.env` (never committed - see `.gitignore`). The report is
scanned for the plaintext password before it's written (`conftest.py`,
`pytest_sessionfinish`); the run fails loudly if one leaks in.

## Reports

`reports/automation_report.html` is self-contained (screenshots embedded as
base64), filterable by result, and every test case expands to show
description, precondition, test data, steps, expected/actual result,
assertions, and (on failure) the failure diagnostics.

Embedded screenshots (the final-state shot and the full per-step evidence
gallery) are downscaled and re-encoded as JPEG before embedding
(`utils/report_utils.py::_b64_image`, requires `Pillow`) — final shots at
900px wide / quality 60, step-evidence thumbnails at 420px / quality 50 —
so the report stays a few MB instead of ballooning past 100MB on a run
with hundreds of highlighted step screenshots. Full-resolution PNGs are
always kept on disk under `screenshots/`, untouched.

The run also auto-opens the finished report in your default browser and
prints its `file://` URI at the end of every execution.

The report header shows a dynamic **Deployment Successful / Deployment
Blocked** banner with a pass-rate gauge. It compares the run's actual pass
rate against `DEPLOYMENT_SUCCESS_THRESHOLD` in `.env` (default `95`,
i.e. 95%) — change that value and the next report uses it automatically,
no code changes needed. This is computed in `utils/report_utils.py::build_html_report`
from `config/settings.py::DEPLOYMENT_SUCCESS_THRESHOLD`.

## Adding / updating / removing a feature

- **Add**: new page object + tests + register in `run_tests.py`'s
  `FEATURE_PATHS`, then `python run_tests.py --feature <Name>`.
- **Update**: edit that feature's page object/tests only.
- **Remove**: delete its `tests/<feature>/`, `pages/<feature>_page.py`,
  `test_data/<Feature>/`, `screenshots/*/<Feature>/`, `logs/<Feature>/`, and
  its `FEATURE_PATHS` entry.

## Troubleshooting

- **`RuntimeError: BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD must be set`** —
  fill in `.env` (copy from `.env.example`).
- **Browser doesn't launch** — run `python -m playwright install chromium`.
- **A selector broke after an app UI change** — re-run discovery: open the
  page with Playwright, dump `document.querySelectorAll(...)`, and update
  the relevant `pages/*.py` locator.
