# All Commands

Copy-paste reference. Run everything from the `QA_Automation/` folder with the
venv activated:

```bash
cd QA_Automation
.venv\Scripts\activate      # Windows
```

## First-Time Setup

**One-command setup (recommended)** - detects your OS, creates/reuses `.venv`,
installs dependencies, installs Playwright's chromium browser, and creates
`.env` from `.env.example` if you don't already have one (never overwrites a
real `.env`). Safe to re-run any time, e.g. after a `git pull`:

```powershell
# Windows (PowerShell)
.\scripts\setup.ps1
```

```bash
# macOS / Linux
bash scripts/setup.sh
```

**Manual setup**, if you'd rather do each step yourself:

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows: .venv\Scripts\activate
source .venv/bin/activate    # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env      # Windows; macOS/Linux: cp .env.example .env
                             # then fill in BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD
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

Runs every feature in `FEATURE_PATHS` (Login, Dashboard, every WTA feature:
Information, Pillar2, News, Forms, Regulations, Treaties, Tools, Calculator, every
RegBriefings feature: My Briefs, World Tax Brief, Transfer Pricing Brief, Tax Treaty
Brief, Archive, Preferences, every TPA feature: Home, National Rules, International
Guidelines, News, Forms, Regulations, Case Law, and every Workspace feature: Dashboard,
Entities, Calendar), cleans previous screenshots/logs/report first, regenerates
the HTML report and per-feature Excel files, and prints the report path. Runs headed by
default (`HEADLESS=false` in `.env`) and opens the live dashboard
(`http://127.0.0.1:8787/dashboard.html`) automatically - see README.md > "Watching it run".

## Run an Entire Parent Module Only (WTA, RegBriefings, or TPA)

**The dedicated command for "run only this parent feature and all its sub-features, nothing
from any other parent feature."** Each of these maps straight to that module's own test
directory (`tests/wta` / `tests/regbriefings` / `tests/tpa`) - confirmed live via `--collect-only` that
each one picks up exactly its own module's tests and nothing else (249 for WTA, 50 for
RegBriefings, 105 for TPA as of this writing, zero overlap):

```bash
python run_tests.py --feature Wta               # EVERY WTA feature at once (Information, Pillar2, News, Forms,
                                                 # Regulations, Treaties, Tools, Calculator) - nothing from RegBriefings/TPA

python run_tests.py --feature Regbriefings      # EVERY RegBriefings feature at once (My Briefs, World Tax Brief,
                                                 # Transfer Pricing Brief, Tax Treaty Brief, Archive, Preferences) -
                                                 # nothing from WTA/TPA

python run_tests.py --feature Tpa               # EVERY TPA feature at once (Home, National Rules, International
                                                 # Guidelines, News, Forms, Regulations, Case Law) - nothing from WTA/RegBriefings

python run_tests.py --feature Workspace         # EVERY Workspace feature at once (Dashboard, Entities, Calendar) -
                                                 # nothing from WTA/RegBriefings/TPA
```

Verify the isolation yourself at any time with:

```bash
python -m pytest tests/wta --collect-only -q          # only WTA tests
python -m pytest tests/regbriefings --collect-only -q  # only RegBriefings tests
python -m pytest tests/tpa --collect-only -q           # only TPA tests
python -m pytest tests/workspace --collect-only -q    # only Workspace tests
```

For an entirely new parent module added later (see "Adding a Feature" below), the same
`--feature <modulename>` aggregate-key pattern applies automatically once it's registered
in `run_tests.py`'s `FEATURE_PATHS`.

## Run One Feature (a single sub-feature within a parent module, or a platform-level feature)

```bash
python run_tests.py --feature Login             # platform-level (outside any parent module)
python run_tests.py --feature Dashboard         # platform-level

python run_tests.py --feature Information       # WTA Information workspace
python run_tests.py --feature Pillar2           # Pillar 2 menu + all 6 sub-pages
python run_tests.py --feature News              # WTA News (top-level)
python run_tests.py --feature Forms             # WTA Forms (top-level)
python run_tests.py --feature Regulations       # WTA Regulations (top-level)
python run_tests.py --feature Treaties          # Treaties menu + all 5 sub-pages (Full DTA, PE Clause, Other Articles, WHT Rates, MLI Data)
python run_tests.py --feature Tools             # Tools menu + Projects + Questionnaire Creator
python run_tests.py --feature Calculator        # Calculators menu + all 6 sub-pages: Corporate Rate Finder,
                                                 # Repatriation Calculator, WHT Router, Loss Relief Calculator,
                                                 # CIT Calculator, Interest And Penalties

python run_tests.py --feature Mybriefs                # RegBriefings > My Briefs (landing/dashboard view)
python run_tests.py --feature Worldtaxbrief            # RegBriefings > World Tax Brief
python run_tests.py --feature Transferpricingbrief     # RegBriefings > Transfer Pricing Brief
python run_tests.py --feature Taxtreatybrief           # RegBriefings > Tax Treaty Brief
python run_tests.py --feature Archive                  # RegBriefings > Archive (year-based past briefs)
python run_tests.py --feature Preferences              # RegBriefings > Preferences (brief/jurisdiction subscriptions)

python run_tests.py --feature Tpahome                   # TPA > Home
python run_tests.py --feature Nationalrules              # TPA > Information > National Rules
python run_tests.py --feature Internationalguidelines    # TPA > Information > International Guidelines
python run_tests.py --feature Tpanews                     # TPA > News
python run_tests.py --feature Tpaforms                    # TPA > Forms
python run_tests.py --feature Tparegulations               # TPA > Regulations
python run_tests.py --feature Caselaw                       # TPA > Case Law
python run_tests.py --feature Tpatreaties                   # TPA > Treaties (TP Articles) - note: TPA has no
                                                              # Calculator feature at all (confirmed absent on
                                                              # RC/Staging/Live), so there is no --feature for it
python run_tests.py --feature Tpacommentary                  # TPA > Commentary
python run_tests.py --feature Tpatools                        # TPA > Tools (nav + all 4 real sub-pages:
                                                                # Templates, Analyzer, Projects, FAR Questionnaire)
python run_tests.py --feature Tpabeps                           # TPA > BEPS - both real sub-pages at once:
                                                                  # BEPS Questionnaire, BEPS Mapper
python run_tests.py --feature Bepsquestionnaire                 # TPA > BEPS > BEPS Questionnaire only
python run_tests.py --feature Bepsmapper                        # TPA > BEPS > BEPS Mapper only

python run_tests.py --feature Workspacedashboard                 # Workspace > Dashboard (Risk Heatmap + News feed) -
                                                                  # "dashboard" was already taken by the platform
                                                                  # execution dashboard (tests/dashboard), so this
                                                                  # product's own Dashboard uses this non-colliding key
python run_tests.py --feature Entities                           # Workspace > Entities (data grid + Add Entity wizard)
python run_tests.py --feature Calendar                           # Workspace > Calendar (Agenda/Calendar toggle +
                                                                  # Create New Event modal)
```

### Workspace: per-environment runs and the report

Environment is chosen by which `.env` block is uncommented (Staging / RC / Live), not by a
flag. To run the Workspace scope in each environment:

```bash
# 1. In .env, uncomment exactly ONE block (BASE_URL / LOGIN_EMAIL / LOGIN_PASSWORD) -
#    "#Reg RC", "#Reg Staging" or "#Reg Live" - and comment the other two.
# 2. Clear the cached login so the new environment gets a fresh session:
rm -f .auth/state.json                     # PowerShell: Remove-Item .auth\state.json
# 3. Run:
python run_tests.py --feature Workspace                    # all 3 modules (17 tests)
python run_tests.py --feature Workspace --smoke            # critical path only (7 tests)
python run_tests.py --feature Workspace --regression       # regression only (10 tests)
```

All 17 Workspace tests are read-only (modals are opened and cancelled, never saved), so the
same command is safe on Live with no exclusions. Each run regenerates
`reports/automation_report.html` (auto-opened at the end; printed as a `file://` link) and
`test_data/Workspace/<Feature>/*.xlsx`. The report covers only that run, so to keep one per
environment, copy it before the next run, e.g.
`cp reports/automation_report.html reports/Workspace_RC_report.html`.

(`--feature` is case-insensitive, matching `run_tests.py`'s own lookup.)

### BEPS: smoke / regression / per-environment

`--feature` combines freely with `--smoke` / `--regression` (the feature
selects the test path, the marker filters within it), so BEPS needs no
special-case commands of its own:

```bash
python run_tests.py --feature Tpabeps --smoke            # BEPS smoke only
python run_tests.py --feature Tpabeps --regression       # BEPS regression only
python run_tests.py --feature Bepsquestionnaire --smoke   # one sub-feature, smoke only
python run_tests.py --feature Bepsmapper --regression     # one sub-feature, regression only
```

Environment selection is **not** a command-line flag anywhere in this
project - it is the `.env` block toggle (Staging / RC / Live), picked up
automatically on the next run. Switch environment, then run any command
above unchanged. Delete `.auth/state.json` after switching if you want to
force a fresh login (`utils/session.py` already auto-detects an
origin mismatch, so this is belt-and-braces rather than required).

**Live/production caution for BEPS Questionnaire**: `BepsQuestionnaire_02`
through `_06` write to **account-level persisted** questionnaire draft
content - `_02`/`_05`/`_06` confirm `Start Over`, which wipes the real
draft, and `_03`/`_04` insert questions into it. Against Live, run only the
read-only subset instead of the whole feature:

```bash
# Live-safe BEPS subset: all 7 Mapper tests + Questionnaire _01/_07 only
python -m pytest tests/tpa/beps -k "mapper or questionnaire_01 or questionnaire_07" -v
```

BEPS Mapper is entirely read-only and safe to run in full on any
environment. See [TPA/BEPS/BEPS_BUSINESS_EXPLORATION.md](TPA/BEPS/BEPS_BUSINESS_EXPLORATION.md)
> "Environment coverage" for the full rationale and recorded results.

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
python run_tests.py --test CRF_07                 # Corporate Rate Finder
python run_tests.py --test RepCalc_17              # Repatriation Calculator
python run_tests.py --test WhtRouter_06            # WHT Router
python run_tests.py --test LossRelief_06           # Loss Relief Calculator
python run_tests.py --test CIT_07                  # CIT Calculator
python run_tests.py --test IAP_06                  # Interest And Penalties
python run_tests.py --test MyBriefs_03              # RegBriefings > My Briefs
python run_tests.py --test WorldTaxBrief_05         # RegBriefings > World Tax Brief
python run_tests.py --test TransferPricingBrief_05  # RegBriefings > Transfer Pricing Brief
python run_tests.py --test TaxTreatyBrief_05        # RegBriefings > Tax Treaty Brief
python run_tests.py --test Archive_05               # RegBriefings > Archive
python run_tests.py --test Prefs_07                 # RegBriefings > Preferences
python run_tests.py --test TpaHome_03                # TPA > Home
python run_tests.py --test NationalRules_07          # TPA > National Rules
python run_tests.py --test InternationalGuidelines_03 # TPA > International Guidelines
python run_tests.py --test TpaNews_05                 # TPA > News
python run_tests.py --test TpaForms_04                # TPA > Forms
python run_tests.py --test TpaRegulations_06           # TPA > Regulations
python run_tests.py --test CaseLaw_06                   # TPA > Case Law
python run_tests.py --test TpaTreaties_02                # TPA > Treaties (TP Articles)
python run_tests.py --test BepsQuestionnaire_05            # TPA > BEPS > BEPS Questionnaire
python run_tests.py --test BepsMapper_03                    # TPA > BEPS > BEPS Mapper
python run_tests.py --test TpaCommentary_03                # TPA > Commentary
python run_tests.py --test TpaToolsNav_02                   # TPA > Tools navigation ("more" menu/submenu)
python run_tests.py --test TpaTemplates_04                  # TPA > Tools > Templates
python run_tests.py --test TpaAnalyzer_06                   # TPA > Tools > Analyzer
python run_tests.py --test TpaProjects_04                   # TPA > Tools > Projects
python run_tests.py --test TpaFar_06                         # TPA > Tools > FAR Questionnaire
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

## Git Workflow

Pull/branch/commit/push/PR/merge/conflict-resolution commands for this repo
live in a separate reference: [GIT_WORKFLOW.md](GIT_WORKFLOW.md). It also
covers this project's multi-remote setup and the auto-generated "publish
latest QA report" commits `utils/publish.py` creates after each run.

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

**For a new WTA feature** (part of the World Tax Analyzer product):
1. Add its page object under `pages/wta/` (reuse `pages/wta/wta_common.py`'s `JurisdictionPanel`/`CategoryTree`
   for any module with the "Jurisdictions [and Categories/Filters]" left panel).
2. Add its tests under `tests/wta/<feature>/`.
3. Add the feature to `WTA_FEATURE_PATHS` in `run_tests.py`.
4. `python run_tests.py --feature <name>`

**For a platform-level feature** (not part of any product, like Login/Dashboard): the same
pattern at the top level instead - `pages/`, `tests/<feature>/`, `FEATURE_PATHS` directly.

**For an entirely new parent module** (a product sibling to WTA): mirror the WTA shape -
`pages/<module>/`, `tests/<module>/<feature>/`, `test_data/<Module>/<Feature>/` - and
register it in `run_tests.py` the same way `WTA_FEATURE_PATHS`/the `"wta"` aggregate key
are, and in `config/settings.py::OTHER_MODULE_FEATURES` (generalized from the old
two-way platform/WTA split specifically to support this) so `feature_dir()` nests its
output under the right module segment. **RegBriefings, TPA and Workspace are all real,
built examples of this** (`pages/regbriefings/` + `REGBRIEFINGS_FEATURE_PATHS`/
`"regbriefings"`; `pages/tpa/` + `TPA_FEATURE_PATHS`/`"tpa"`; `pages/workspace/` +
`WORKSPACE_FEATURE_PATHS`/`"workspace"`, all in `run_tests.py`, with
`test_data/RegBriefings/<Feature>/`, `test_data/TPA/<Feature>/` and
`test_data/Workspace/<Feature>/` respectively) - follow their exact structure for the
next new parent module. If a sub-feature's natural key would collide with an existing
one (Workspace's own "Dashboard" page collided with the pre-existing platform-level
execution dashboard's `--feature dashboard`), pick a non-colliding key (`workspacedashboard`)
and document the collision/choice in `CLAUDE.md`, the same way this file documents it.
See `AGENT.md` > "Parent module structure" and `CLAUDE.md` > "RegBriefings" / "TPA" /
"Workspace".

## Discovery scripts

There is no committed `scripts/discover.py` (the live DOM was inspected with throwaway Playwright
scripts run directly via `python`, per the file-header convention "locators came from a discovery
script, not guessed" that every `pages/*.py` file documents). To re-discover a page after a UI change,
write a short script that logs in (see any `pages/*_page.py` docstring for the login flow), navigates to
the page, and dumps `document.querySelectorAll(...)` / `page.evaluate(...)` results for the elements you
need, then update the relevant `pages/*.py` locator.
