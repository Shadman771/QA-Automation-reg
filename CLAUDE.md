# CLAUDE.md

Guidance for any Claude Code (or other AI agent) instance opening this repository, on this device or a new one.

## Project

**QA Automation framework** for the *Regplus World Tax Analyzer (WTA)* web app, built with **Python + pytest + Playwright (sync API)**, using the **Page Object Model (POM)**.

Goal: comprehensive, evidence-rich, visually-observable regression coverage of the live application — every assertion is real, every locator comes from inspecting the actual DOM, and every run produces a professional HTML report a non-engineer can read.

This is the **single, permanent workspace** for this project. Do not create a second project/folder for a new feature or run — inspect and extend the files already here.

## Architecture (as it actually exists — read before assuming a generic layout)

```
config/settings.py       - all config, read from .env (never hardcode credentials)
pages/                   - Page Object Model: one class per page/section
utils/case.py            - Case: every test's step/action/click/fill/check helper
                            (red-highlights the live element + captures per-step evidence)
utils/highlight.py        - the red on-screen highlight
utils/session.py          - session-reuse: logs in once per run, caches storage_state
utils/auth.py             - perform_login(case, page): reuses the cached session
utils/screenshot.py       - final + per-step screenshot capture
utils/excel_utils.py      - writes test_data/<Feature>/<Feature>_Test_Cases.xlsx
utils/report_utils.py     - builds the self-contained reports/automation_report.html
utils/dashboard.py        - the live HEADLESS=false execution dashboard
tests/<feature>/          - one directory per feature/module, test_*.py files
test_data/<Feature>/      - auto-generated Excel test case files (.xlsx) — do not hand-author
conftest.py               - session lifecycle, fixtures, report/Excel generation, security gate
run_tests.py              - the CLI entry point (use this, not bare `pytest`, for full runs)
```

`tests/login/` is the one exception to session reuse: it has its own `conftest.py` that forces a fresh, unauthenticated browser context per test, because it tests the login flow itself.

The **Treaties** module (`pages/treaties_menu.py` + `pages/treaties_*_page.py`, `tests/treaties/`) covers the "Treaties" top-nav dropdown's 5 sub-pages: Full DTA, PE Clause, Other Articles, WHT Rates, MLI Data. Four of the five (Full DTA, PE Clause, Other Articles, WHT Rates) reuse `pages/wta_common.py`'s single-select `JurisdictionPanel` (heading "Select Jurisdiction", placeholder "Use the left panel to choose jurisdiction.") and render a table only after a country is selected. MLI Data is the exception — no jurisdiction panel at all; its table is server-rendered on load and sorted via a `?sort=jurisdiction:asc|desc` URL query param, toggled by clicking its sortable column headers. Watch the same rsuite-dropdown gotcha documented in `pages/pillar2_menu.py`/`pages/treaties_menu.py`: EVERY top-nav dropdown's `<li class="rs-dropdown-item">` is mounted in the DOM at once (hidden, not removed), so an unscoped `page.locator("li.rs-dropdown-item")` after opening one dropdown returns items from every dropdown — filter to `.is_visible()` (or scope tightly by exact text) rather than assuming a raw count/list reflects only the open menu.

**Known live application defect — nav viewport width**: the "Treaties", "Calculators", "Tools" and "BEPS" top-nav dropdowns are completely ABSENT from the DOM (not just hidden) below ~1600px viewport width, with no responsive/overflow fallback — confirmed 0 matches at 1440/1500px, 1 match at 1600/1700px, against this project's 1440x900 default viewport (`conftest.py`'s `browser_context_args`). This is a real, unfixed application defect, documented rather than hidden: any test suite covering one of these four dropdowns needs its own directory-local `browser_context_args` fixture override at 1680x900 (see `tests/treaties/conftest.py` and `tests/tools/conftest.py` — both apply the identical override for this identical reason). Follow this same pattern for any future module behind one of these four dropdowns.

The **Tools** module (`pages/tools_menu.py`, `pages/tools_projects_page.py`, `pages/tools_questionnaire_creator_page.py`, `tests/tools/`) covers the "Tools" top-nav dropdown's 2 sub-pages: **Projects** (`/wta/Project`, a real project-management workspace — create/rename/delete projects, each holding a table of saved items) and **Questionnaire Creator** (`/wta/QuestionnaireCreator`, a rich-text questionnaire builder — click tree questions to insert them into a Syncfusion editor, "Start Over" to reset with a confirm dialog, "Add to Project" to save into a Projects workspace). Distinct gotcha from Treaties: neither Tools page supports a direct full-page deep link — `page.goto()` straight to `/wta/Project` or `/wta/QuestionnaireCreator` redirects to `/wta/Information` instead (no server-side SPA route for a hard link), so unlike every Treaties page object, the Tools page objects have no `goto()` — `pages/tools_menu.py::ToolsMenu.open_item()` (click through the dropdown) is the only supported way in, and this is asserted as real, documented application behavior in `tests/tools/test_tools_navigation.py::test_toolsmenu_03_...`, not silently worked around. Projects tests create only uniquely-named, self-cleaning test data (`ToolsQA_<tag>_<timestamp>`, deleted again before the test ends) since this is a real shared account with dozens of pre-existing projects from prior manual/automation use.

## Project rules & conventions

- **Strict Page Object Model**: every locator lives in `pages/`, never inline in a test. Locators must come from inspecting the real live DOM (a throwaway Playwright discovery script is the standard way to do this in this repo) — never guessed.
- **Prefer explicit, resilient locators**: `get_by_role`, `get_by_label`, `get_by_text`, `get_by_alt_text`, stable `#id`/`name` attributes. Avoid absolute XPath, `nth-child`, or auto-generated class names unless there's no reliable alternative.
- **Test data stays out of test logic**: `.env` for credentials/config, `test_data/<Feature>/*.xlsx` for generated test case records (auto-written by `utils/excel_utils.py` from each run's results — don't hand-edit these files, they're regenerated every run).
- **Never hardcode credentials** anywhere in `pages/`, `tests/`, or committed files. Read them from `config/settings.py` (which reads `.env`). `.env` is gitignored; `.env.example` holds placeholders only.
- **Never weaken an assertion to force a pass.** If the live app genuinely misbehaves, that's a real, documented FAIL — fix the automation if the automation is wrong, but never soften the check that caught a real problem.
- **Every test uses `Case`** (`utils/case.py`) for its steps/actions/clicks/fills/checks — this is what drives the live red-highlight, the live dashboard, and the per-step evidence screenshots. Don't call raw `page.click()`/`page.fill()` in a test.
- **Every meaningful assertion has a human-readable message** via `case.check(text, ok, expected=..., actual=..., locator=...)`.
- **Keep `HEADLESS=false` as the default** in `.env` — the browser must stay visible unless explicitly overridden (`--headless` / `HEADLESS=true`).
- **Login/session reuse**: don't re-implement per-test login. Non-Login feature tests call `utils/auth.py::perform_login(case, page)`, which reuses the cached authenticated session (see `utils/session.py`) and only logs in for real if the cache is stale.
- **Reports/logs/screenshots are regenerated, not maintained by hand.** `run_tests.py` cleans the previous run's generated artifacts (screenshots, logs, report) before each run unless `--keep` is passed; it never touches source code, test cases, or docs.
- **Security**: the report build has a hard gate in `conftest.py` that raises if the plaintext `LOGIN_PASSWORD` ever appears in the generated HTML report — never bypass or remove this check.

## Commands

Full command reference: [ALL_COMMANDS.md](ALL_COMMANDS.md). The essentials:

```bash
python run_tests.py                     # full suite (the standard way to run this project)
python run_tests.py --feature login     # one feature only, e.g. login, dashboard, information,
                                         # pillar2, news, forms, regulations, treaties, tools
python run_tests.py --test LOGIN_05     # one specific Test Case ID
python run_tests.py --smoke             # @pytest.mark.smoke only
python run_tests.py --regression        # @pytest.mark.regression only
python run_tests.py --headed / --headless
python run_tests.py --keep              # skip pre-run cleanup of screenshots/logs/report
```

`python run_tests.py` is preferred over bare `pytest` because it also handles cleanup, headless/headed overrides, and prints the final report path — but `pytest tests/login/test_login.py -v` works directly too when debugging a single file.

After any run, the HTML report is at `reports/automation_report.html` (also auto-opened in the browser and printed as a `file://` link in the terminal).

## Adding a feature

See [ALL_COMMANDS.md](ALL_COMMANDS.md) > "Adding a Feature". In short: page object in `pages/`, tests in `tests/<feature>/`, add the feature to `FEATURE_PATHS` in `run_tests.py`, then `python run_tests.py --feature <Name>`.
