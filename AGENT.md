# AGENT.md

Persistent handbook for any agent (Claude Code or otherwise) continuing work on this project, on this machine or a new one. `CLAUDE.md` is the short version; this is the full one. Keep both in sync when either changes.

## 0. Read this first (AI agent quick-start)

If you are opening this repository for the first time this session: **read this entire file and `CLAUDE.md` in full before writing any code or asking the user to re-explain the project.** Together they are maintained as a complete, standalone project memory specifically so a fresh agent session (on this machine or a new one) can pick up work immediately. The user should not need to re-explain the architecture, the application's behavior, prior bug fixes, or standing conventions — if something seems missing or unclear, investigate the live code/DOM directly (section 5's rules) rather than guessing or asking first, unless genuinely blocked on something only the user can decide (credentials, which environment to target, a destructive action).

Operating norms that apply to every session, distilled from real incidents during this project's development (details throughout this file):
- **Before starting any `run_tests.py`/pytest invocation, check for an already-running one**: `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` (Windows). Two concurrent invocations against this same repo collide on `.auth/state.json`, `screenshots/`, `logs/`, `reports/` and can deadlock or crash (see section 7).
- **A single invocation of `.venv\Scripts\python.exe ...` normally shows as TWO `python.exe` processes in the process list on Windows (Python 3.11+) — this is NOT a duplicate run.** It's the stdlib venv launcher stub (`.venv\Scripts\python.exe`, near-zero CPU, just relays) plus the real interpreter it execs (`...\PythonXXX\python.exe`, does the actual work) — confirmed live by checking `ExecutablePath`/`ParentProcessId` via `Get-CimInstance Win32_Process`, not by process count alone. Killing the "parent" of this legitimate pair kills the whole run. Only treat it as a real duplicate if TWO such pairs exist (four processes, or two independent `CreationDate`-distinct launches) — verify with `ParentProcessId`/`CreationDate` before killing anything.
- **Never fabricate test results, pass/fail counts, root causes, or git/push status.** Verify directly (re-run the specific test, read the actual traceback/screenshot, check `git log`/`git ls-remote`) before reporting anything as fixed, passing, or pushed.
- **Never weaken or remove an assertion to force a pass.** A genuine live-application difference (wrong environment, real app defect, real app slowness) is a real FAIL/BLOCKED to document, not something to paper over.
- **Destructive or wide-blast-radius actions** (killing a process, force-pushing, deleting `.auth/state.json` or other generated state, resetting git state) are generally fine when they match an established, documented pattern in this file - but confirm with the user first when it's ambiguous which process/branch/environment is intended.
- Both `.md` files decay if only one is updated — when you fix something, add a convention, or learn a real app behavior, update whichever file it belongs in (see each file's own stated scope) in the same session, not "later."

## 1. Project identity

**World Tax Analyzer (WTA)** is a commercial tax-research web application (Reg Analytics / regplus) covering corporate tax rates, treaties, withholding rates, BEPS/Pillar Two data, and several tax calculators across 120+ jurisdictions. Users log in, pick a jurisdiction (and sometimes a category/income stream/calculation), and the app renders the relevant tax data, lets them export/print it, or run a calculation against it.

This repository is a **Playwright + Python + pytest** regression-testing framework for that application, built strictly as a **Page Object Model (POM)**. Its goal: comprehensive, evidence-rich, visually-observable coverage where every assertion is real (verified against the live app, not guessed) and every run produces a professional HTML report.

This is the single, permanent workspace for this project — never create a second project folder for a new feature.

## 2. Application behavior (verified live, not assumed)

### Login flow
- Login page: `<BASE_URL>` (from `.env`), fields `#email` / `#password`, submit `button[type="submit"]`.
- **The app has a real, sometimes-slow post-login provisioning screen** ("Syncing with Enterprise Cloud...", "Hold on, getting things ready for you...") before it lands on `/wta/Information`. Confirmed live on one environment this can take **~11 seconds**. Never assume login is done just because the URL briefly isn't `/auth/login`, or because a short fixed wait elapsed — `utils/session.py::wait_for_login_sync()` polls for the sync banner to disappear AND the URL to leave `/auth/login`, up to a configurable timeout. Both `utils/session.py` (session-cache bootstrap) and `utils/auth.py` (per-test fallback login) use this helper; nothing else should re-implement a fixed-wait login check.
- A genuine login failure raises `utils.auth.AuthenticationError(case, reason)`. `conftest.py`'s `pytest_runtest_makereport` hook converts that into a `BLOCKED` entry in the HTML report/Excel/dashboard automatically — no test file needs its own try/except. (pytest's own terminal line for that test still reads FAILED; that's pytest's native status, separate from our report's classification.)

### URL / environment configuration
- **Every page object's `goto()` must build its URL from `config.settings.APP_ORIGIN`** (derived from `.env`'s `BASE_URL`), never a literal domain. This was a real, shipped bug: 15 page objects had `https://regplus.kaz.com.bd/...` hardcoded, so changing `BASE_URL` in `.env` silently had no effect on those pages — they kept navigating to the old domain regardless of configuration, which looked like "login redirects to the wrong environment." Fixed; watch for this pattern in any new page object.
- This app has shipped on at least three real environments seen during development, each with **different seeded data** and a different account:

  | Name | `BASE_URL` | Account used |
  |---|---|---|
  | Staging | `https://regplus.kaz.com.bd/auth/login/` | `demo@reganalytics.com` |
  | RC (release-candidate) | `https://regplusrc.reganalytics.com/auth/login/` | `nasimsaker@gmail.com` |
  | Live/production | `https://regplus.reganalytics.com/auth/login/` | `monir.smh@gmail.com` |

  Switching environments is just editing `.env` (`BASE_URL`/`LOGIN_EMAIL`/`LOGIN_PASSWORD`) — the dynamic-env mechanism itself has been verified correct across many real switches this project; **always delete `.auth/state.json` after switching** (origin-scoped cached session, invalid across a `BASE_URL` change). A test failing on one environment because expected data doesn't exist there, or that environment simply being slower to render (see Timeouts below), is a real, expected difference, not an automation bug — don't "fix" it by weakening the assertion; note which environment it was verified against. Passwords are never written here or in any committed file — only in the gitignored `.env`.
- Several API endpoints are still hardcoded to one environment's domain in a few places (`pages/wta/calculator_rate_finder_page.py::CORPORATE_RATE_API`, `pages/wta/calculator_repatriation_page.py::REPATRIATION_TREATY_API`, `tests/wta/tools/test_projects.py::PROJECT_API`) because their subdomain-naming scheme isn't mechanically derivable from `BASE_URL` across environments (e.g. prod inserts `.api.` into the subdomain, RC doesn't). These specific tests are tied to whichever environment's seeded data they were built against; this is a known, documented limitation, not yet generalized.
- `page.request.*()` calls bypass this app's auth entirely (it's a JWT bearer token read from `localStorage`, not a cookie `page.request` sends) and get a silent `401`. Any direct API verification/cleanup must go through the browser's own authenticated call (`page.expect_response(...)` around the action that triggers it) or an in-app UI flow — never a bare `page.request.get/post(...)` against this app's API.

### Known UI gotchas (apply to any new page object)
- **Every top-nav dropdown** (`Treaties`, `Pillar 2`, `Calculators`, `Tools`, `BEPS`) mounts ALL its `<li class="rs-dropdown-item">` items in the DOM at once, hidden rather than removed. An unscoped `page.locator("li.rs-dropdown-item")` after opening one dropdown returns items from every dropdown. Filter to `.is_visible()` or scope tightly by exact text.
- **`Treaties`, `Calculators`, `Tools`, `BEPS`** dropdowns are completely ABSENT from the DOM below ~1600px viewport width (no responsive fallback) — any suite covering one needs a directory-local `browser_context_args` override at 1680x900 (see `tests/wta/treaties/conftest.py`, `tests/wta/tools/conftest.py`, `tests/wta/calculator/conftest.py`).
- rsuite `SelectPicker` components' `aria-expanded` attribute can read `"false"` for a moment right after a genuinely successful click (a React render-commit race) — don't trust it as an "is it open" signal; check whether the listbox's `[role='option']` children are actually visible instead (see `pages/wta/calculator_repatriation_page.py::_ensure_open()`).
- Neither Calculator nor Tools sub-pages support a direct deep link — `page.goto()` to their URL redirects to `/wta/Information`. Reach them only via their menu's `open_item()`.

### Feature/module structure (as it exists, not generic)
See `CLAUDE.md` for the full per-module breakdown (Treaties, Tools, Calculator, Pillar 2, etc.) — it's kept current and is the faster reference. This file focuses on cross-cutting architecture.

## 3. Automation architecture

```
config/settings.py   - ALL config, read from .env. APP_ORIGIN, DEFAULT_TIMEOUT_MS,
                        NAVIGATION_TIMEOUT_MS, ASSERTION_TIMEOUT_MS, DEPLOYMENT_SUCCESS_THRESHOLD
                        (alias: SUCCESS_THRESHOLD) all live here - never hardcode in a test/page.
pages/                - POM: one class per page/section, goto() built from APP_ORIGIN
utils/case.py         - Case: step/action/click/fill/check/verify_visible - every test uses this,
                        never raw page.click()/page.fill()
utils/highlight.py     - the red on-screen highlight drawn before each action
utils/session.py       - session-cache bootstrap + wait_for_login_sync()
utils/auth.py          - perform_login(case, page) + AuthenticationError
utils/screenshot.py    - final + per-step screenshot capture
utils/excel_utils.py   - writes test_data/<Feature>/<Feature>_Test_Cases.xlsx (auto-generated)
utils/report_utils.py  - builds reports/automation_report.html
utils/publish.py       - best-effort push of the report to GitHub Pages (see section 6)
utils/dashboard.py     - the live HEADLESS=false execution dashboard
utils/cleanup.py       - pre-run cleanup; tolerates a file locked by a second concurrent run
                        (prints a warning and skips it, rather than crashing the whole run).
                        Its `onexc` handler reads the exception INSTANCE directly, not a
                        tuple - `shutil.rmtree`'s `onexc` (Python 3.12+) differs from the
                        older deprecated `onerror` 3-tuple convention; using `exc_info[1]`
                        here (a real, shipped bug, fixed 2026-10-15) crashed the handler
                        itself with "TypeError: 'PermissionError' object is not
                        subscriptable" - taking down the WHOLE run before a single test
                        executed, every time cleanup hit a locked file, which defeated the
                        entire point of this best-effort wrapper. If you ever see that
                        exact TypeError again, it's a regression of this fix.
pages/wta/              - every page object for the WTA (World Tax Analyzer) parent module
pages/login_page.py,
pages/landing_page.py   - platform-level, OUTSIDE pages/wta/ (pre-product: login, product picker)
tests/<feature>/        - platform-level test dirs: login/, dashboard/
tests/wta/<feature>/    - every WTA feature's tests (information, pillar2, news, forms,
                        regulations, treaties, tools, calculator)
test_data/<Feature>/    - auto-generated Excel, platform-level features only - never hand-edit
test_data/WTA/<Feature>/  - auto-generated Excel, every WTA feature - never hand-edit either
conftest.py             - fixtures, session lifecycle, BLOCKED-conversion hook, report/Excel generation
run_tests.py            - CLI entry point (prefer this over bare pytest for full runs)
```

### Parent module structure
WTA is one product among several the app offers (Workspace / World Tax Analyzer / Transfer Pricing Analyzer / RegBriefings tabs) - `pages/wta/`, `tests/wta/<feature>/`, `test_data/WTA/<Feature>/` hold everything specific to it. `login`/`dashboard` sit OUTSIDE `wta/` at every level because they're the platform shell that exists before a product is even chosen. `config/settings.py::feature_dir(base, feature)` is the one shared rule every feature-keyed output directory (test_data, screenshots, logs) uses to decide platform-level vs. nested-under-its-parent-module; its `NON_WTA_FEATURES` set currently lists `{"Login", "Dashboard"}` - everything else is treated as WTA. A future parent module (e.g. a `tpa` module for Transfer Pricing Analyzer) gets the identical shape as a sibling of `wta`: `pages/tpa/`, `tests/tpa/<feature>/`, `test_data/TPA/<Feature>/`, registered in `run_tests.py`'s `FEATURE_PATHS` the same way `WTA_FEATURE_PATHS`/the `"wta"` aggregate key are - and `feature_dir()`/`NON_WTA_FEATURES` would need generalizing from a two-way platform/WTA split into a real module lookup at that point.

### Fixtures
- `page` (root `conftest.py`): every feature test starts from an already-authenticated context (`storage_state` reuse). Sets `DEFAULT_TIMEOUT_MS`/`NAVIGATION_TIMEOUT_MS` as Playwright defaults.
- `tests/login/conftest.py` overrides `page` to a genuinely fresh, unauthenticated context — the one deliberate exception, since those tests exercise login itself.
- `result(case, actual, ok)`: records a PASS/FAIL entry (screenshot + evidence + failure log on FAIL).
- `blocked(case, reason)`: records a BLOCKED entry directly, for a test that can determine up front it cannot be validated (e.g. an incomplete spec). Most auth-driven BLOCKED entries happen automatically via the `pytest_runtest_makereport` hook instead (see section 2) — you don't need to call this for a login failure.

### Timeouts
`DEFAULT_TIMEOUT_MS` (default 60000) and `NAVIGATION_TIMEOUT_MS` (default 30000) are applied globally via `page.set_default_timeout()`/`set_default_navigation_timeout()` in every `page` fixture. `ASSERTION_TIMEOUT_MS` (default 60000) is used by `Case.verify_visible()` and is available for any explicit `expect()`/custom-assertion timeout a test wants to pass. Override any of them per-run via `.env`, no code changes needed.

**`DEFAULT_TIMEOUT_MS`/`ASSERTION_TIMEOUT_MS` were raised from 15000 to 60000 (2026-10-14)** after a direct, timed, isolated reproduction against a newly-added Live account: loading a cached session cold (the normal per-test path) can take up to ~60s for real page content to become visible/actionable, even though the app's own "Syncing with Enterprise Cloud" banner clears from the DOM within 1-4s - that banner clearing is NOT a reliable "content is ready" signal (see `utils/session.py::wait_for_login_sync()`). This isn't universal to every environment/account - some load in under 10s - but the ceiling needs to cover the slowest confirmed-real case without weakening what's actually being waited for. If you add a raw `locator.wait_for(...)`/`page.evaluate(...)` call that doesn't go through `Case.click()`/`Case.fill()`/`Case.verify_visible()`, it bypasses these centralized timeouts entirely and will fail on a slow environment even though the framework-wide fix is in place - route through `Case` instead (see `tests/dashboard/test_landing.py`'s LANDING_21/24/33/34/35/37/39 fixes for the exact pattern: add a `case.verify_visible(...)` on the element the raw DOM script depends on, before calling it).

### Waits
Prefer condition-based waits: Playwright's own action/locator auto-waiting (now backed by the centralized timeouts above), `pages/wta/wta_common.py::wait_for_content(locator, timeout=...)` for "did the async-rendered content show up", and `utils/session.py::wait_for_login_sync()` for the post-login provisioning screen. **`page.wait_for_timeout(ms)` fixed waits are still used throughout the suite** (over 100 files) as short settle/debounce buffers after an interaction, not as the primary correctness mechanism — this is a known, accepted trade-off (rewriting all of them to condition-based waits was assessed as high-risk/low-value busywork across a huge surface area, not attempted wholesale). When you hit a REAL flake traceable to insufficient waiting, fix that specific call site with a proper condition-based wait rather than a longer fixed sleep; don't do a blind global sweep.

**Every page object's `goto()` (and the two menu `open_item()`s that wait after a dropdown click) uses `wait_until="domcontentloaded"`, never `"networkidle"`.** This app keeps persistent background requests going on its authenticated pages (notification polling, analytics) that can prevent true network-idle from ever being reached — confirmed live as a real, reproducible 30-second navigation timeout cascading across nearly every feature, not a slow-network flake. `utils/session.py::wait_for_login_sync()` (or the test's own subsequent `wait_for_content`/`verify_visible` calls) is the actual "is it ready" check; the navigation wait only needs the document to exist. If you add a new page object, copy this pattern — don't reach for `networkidle` even though it reads as the "safer" choice.

**`Case.verify_visible()` actually waits** (up to `ASSERTION_TIMEOUT_MS`) for the element rather than doing an instant `is_visible()` check — `Locator.is_visible()` alone does NOT auto-retry the way `.click()`/`expect()` do. This was a real, previously-masked gap: it worked for a long time only because `networkidle` navigation happened to pre-render everything before any assertion ran; removing `networkidle` exposed it. If you ever add a new instant-check helper to `Case`, make it wait the same way.

## 4. Execution rules

```bash
python run_tests.py                     # full suite - the standard way to run this project
python run_tests.py --feature wta       # every WTA feature at once (the whole parent module)
python run_tests.py --feature calculator  # one WTA feature (also: information, pillar2, news,
                                           # forms, regulations, treaties, tools)
python run_tests.py --feature login     # a platform-level feature (also: dashboard)
python run_tests.py --test LOGIN_05     # one specific Test Case ID
python run_tests.py --smoke             # @pytest.mark.smoke only, ALL features (not just one)
python run_tests.py --regression        # @pytest.mark.regression only, ALL features
python run_tests.py --headed / --headless
python run_tests.py --keep              # skip pre-run cleanup of screenshots/logs/report
```

Verify collection before trusting a marker run: `python -m pytest --collect-only -m smoke` / `-m regression`. As of this writing: 245 total tests, 62 smoke + 183 regression (no gaps/overlap), spanning every feature — smoke/regression have never actually been scoped to one feature in this codebase; if that's ever observed, it's almost certainly the IDE's test runner being scoped to a folder/file, not `pytest -m smoke` itself. Confirm with the collect-only command above before assuming the framework is broken.

**Never run two `run_tests.py`/pytest invocations concurrently against this repo** — they share `.auth/state.json`, `screenshots/`, `logs/`, `reports/`, and the live application's own account/session. A second run's cleanup step can delete or lock files the first run is actively using (confirmed live, reproducible). Check for a running process (`Get-CimInstance Win32_Process -Filter "Name='python.exe'"` on Windows) before starting one.

A single-test or filtered pytest invocation still regenerates `reports/automation_report.html` for just that invocation (the report reflects whatever ran in THAT process, not a cumulative history) — running one debug test after a full suite will overwrite the full report with a 1-test one. Re-run the full suite before trusting/publishing "the final report" if you've run anything narrower since.

## 5. Development rules

- Inspect before modifying — read the actual current code, don't assume a generic layout.
- Preserve existing coverage; never remove/weaken an assertion to force a pass. A genuine application difference (wrong environment, real app bug) is a real FAIL or BLOCKED, not something to paper over.
- Strict POM: every locator in `pages/`, never inline in a test, never guessed — confirm it against the live DOM first (a throwaway Playwright discovery script, not committed, is the normal way to do this here).
- Every test uses `Case` for its steps/actions/clicks/fills/checks.
- Fix root causes. When a test fails, determine whether it's a genuine value mismatch, a missing element, a wrong locator, a navigation problem, a timeout, an authentication problem, an application defect, or an unavailable dependency — state which, with evidence, not a guess.
- Run the directly-affected tests after a change; run smoke and ideally full regression before pushing anything non-trivial.
- Never fabricate pass/fail counts, root causes, or git/push status — report only what was actually run/observed.

## 6. Git / publishing

- `origin` (`shadmanshilon/Reg-Automation`) has a **persistent, unresolved push-permission** issue (`! [remote rejected] ... permission denied`) — confirmed across every branch, dozens of attempts, over the whole project history. Always attempt it (per house rule: never claim success without the command succeeding), but don't be surprised when it fails.
- `newrepo` (`Shadman771/QA-Automation-reg`) **does** accept pushes. `utils/publish.py` now targets this remote automatically (`git push newrepo <current-branch>:main`) after every run, publishing `docs/index.html` for GitHub Pages at `https://shadman771.github.io/QA-Automation-reg/`. GitHub Pages needs a one-time manual enable on that repo (Settings → Pages → Source: branch `main`, folder `/docs`) that no agent here can do without `gh` CLI or API credentials — ask the user if it's ever not live.
- `upstream` (`Shadman771/Reg-Automation`) exists but hasn't been actively used this project.

## 7. Troubleshooting

| Symptom | Likely cause | Where to look |
|---|---|---|
| A whole feature fails at its very first navigation step, no other symptom | Stale cached JWT in `.auth/state.json` (origin-scoped; doesn't help across a `.env` `BASE_URL` change either) | Delete `.auth/state.json`, re-run |
| "It logs in fine, then redirects to a different domain" | A page object's `goto()` has a hardcoded URL instead of `APP_ORIGIN` | `grep -rn "self.page.goto(\"https://" pages/` |
| A protected feature's test fails with a confusing, unrelated-looking assertion | Login actually failed (check for an `AuthenticationError`/BLOCKED entry instead of assuming the test's own assertion is wrong) | The HTML report's BLOCKED filter |
| `run_tests.py` crashes immediately with `PermissionError` on a log/screenshot file | A second `run_tests.py`/pytest process is running concurrently against this same repo | Check running python processes; don't run two at once |
| Real login appears to fail/bounce back to `/auth/login` intermittently | The app's post-login "Syncing with Enterprise Cloud" screen can take ~11s; a short fixed wait mis-detects this as failure | Confirm `utils/session.py::wait_for_login_sync()` is actually being used on the code path in question, not a reintroduced fixed wait |
| The "final report" looks tiny / shows far fewer tests than expected | A narrower pytest invocation (single test/feature) ran after the full suite and overwrote `reports/automation_report.html` | Re-run the full suite |
| `pytest -m smoke` "only runs Calculator" (or similar) | Almost always the IDE's test runner UI being scoped to a folder, not pytest's own marker selection | Verify with `pytest --collect-only -m smoke` directly in a terminal |
| Tests fail right after an `.env` switch to a new URL/account, URL is correct but content/assertions time out | The new account/environment is genuinely slower to render than previously-tested ones (confirmed: up to ~60s) - the dynamic `.env` read itself is working correctly | Check the failure screenshot for the "Syncing with Enterprise Cloud" splash still showing; confirm with an isolated timed script before assuming a code bug; see the Timeouts section above |
| Two `python.exe` processes show up for what you (or the user) believe was one invocation | Almost always the normal Windows venv-launcher stub pair (see section 0), NOT a duplicate run | Check `ExecutablePath`/`ParentProcessId`/`CreationDate` via `Get-CimInstance Win32_Process` before killing anything - a real duplicate is a SECOND such pair, not just two processes |
| `run_tests.py` crashes with `TypeError: '<SomeException>' object is not subscriptable`, traceback points into `utils/cleanup.py::_on_error` | Regression of the `onexc` exception-instance-vs-tuple fix (see section 3, `utils/cleanup.py` entry) | Confirm `_on_error` reads `exc_info` directly, not `exc_info[1]` |
| A `--regression`/`--smoke`/full-suite run's final result count is lower than the known collected total, with no corresponding FAILED/BLOCKED entries for the gap | An entire test file/feature silently produced zero `Case`/`result()` entries - almost always a fixture/import/collection-level error in that file, not a per-test assertion failure, so it won't show up in the custom HTML/Excel report at all | Compare `python -m pytest tests -m <marker> --collect-only -q`'s total against the run's actual result count per feature (see `reports/execution_results.json`); re-run the suspect file directly with `-v` to see pytest's own error output |

## 7a. Known open items (as of 2026-10-15)

- **A `--regression` run against RC (183 tests) produced only 169 recorded results** (159 PASS, 10 FAIL) - the entire "Tools QuestionnaireCreator" feature (4 regression tests) produced zero `Case`/`result()` entries in that run, even though each of its 4 tests passes/fails normally when run directly (confirmed by re-running them in isolation afterward - they're real, working tests, not a collection-level defect). This points to a setup/fixture-level error specific to running late in a long sequential session (memory/resource pressure, a stale dashboard connection, etc.) rather than a code bug in the feature itself - not yet root-caused with direct evidence; if you hit this again, capture pytest's own `-v` terminal output for that specific file during a FULL regression run (not in isolation) to see the actual error.
- **The 10 real FAILs from that same run are mostly explained by RC's seeded data differing from whichever environment each assertion was originally verified against**, not code defects: `LANDING_34` expected 25 Asia-Pacific countries (confirmed on an earlier environment) but RC shows 22; `CRF_09`/`CRF_10`/`CRF_11` reference Bangladesh/2024 rate values that differ from the documented Live-environment calculation-validation anchor (55%) because RC's data is independently seeded; `Projects_07`/`Projects_08` fail their API-endpoint check because `tests/wta/tools/test_projects.py::PROJECT_API` is hardcoded to one environment's domain (see section 2's "Several API endpoints are still hardcoded..." note) and RC's actual endpoint differs. None of these were deeply re-verified line-by-line against RC's specific live data - treat them as plausible-but-not-fully-confirmed until someone does that verification on RC specifically.
- Full regression suite has not yet been re-run end-to-end since the `ASSERTION_TIMEOUT_MS`/`DEFAULT_TIMEOUT_MS` bump and the `cleanup.py` fix together, against any environment, with a clean single process. Worth doing before trusting a published report's numbers as fully current.

## 8. Maintenance

- **Add a WTA feature**: page object in `pages/wta/` (goto from `APP_ORIGIN`), tests in `tests/wta/<feature>/`, add to `WTA_FEATURE_PATHS` in `run_tests.py`, run `python run_tests.py --feature <name>`. For a platform-level feature (not part of any product), the same pattern at the top level instead (`pages/`, `tests/<feature>/`, `FEATURE_PATHS`). Full walkthrough: `ALL_COMMANDS.md` > "Adding a Feature".
- **Add a test case**: follow the `Case`-driven pattern in any existing test in the same module; Excel/report entries are generated automatically from the run, never hand-authored.
- **Update environment variables**: add to `config/settings.py` with a sensible default, document in `.env.example`, mention here if it affects cross-cutting behavior (timeouts, thresholds).
- **Validate and push**: run the directly-affected tests, then ideally the full suite, review `git status`/`git diff` for anything unexpected (especially nothing from `.env` or real credentials), commit, push to `newrepo` (and attempt `origin` honestly reporting its known failure).

## 9. New-device setup

```powershell
git clone <repo-url>
cd QA_Automation
python -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install
copy .env.example .env              # macOS/Linux: cp .env.example .env
# edit .env: BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD at minimum
python run_tests.py --test LOGIN_01 # sanity check
python run_tests.py --feature login # one feature
python run_tests.py --smoke         # smoke
python run_tests.py                 # full regression
# then open reports/automation_report.html
```

Not independently re-verified on a clean machine as of this writing — if you do so, update this section with what actually happened rather than assuming it's correct.
