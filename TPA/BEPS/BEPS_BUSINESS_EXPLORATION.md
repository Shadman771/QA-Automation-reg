# TPA > BEPS — Business Exploration

Covers the two real sub-features found live under TPA's "BEPS" submenu
(nested inside the unlabeled "more" overflow menu alongside
Treaties/Commentary/Tools - see `pages/tpa/tpa_common.py`). Confirmed via a
full nav HTML dump (scratchpad discovery script, not part of the suite):
the "BEPS" submenu toggle has exactly 2 children, no more, no invented
5/6-feature shape:

```
TPA
  BEPS
    BEPS Questionnaire  -> /tpa/BEPSQuestionnaireCreator
    BEPS Mapper          -> /tpa/beps
```

Exploration status legend: Explored / Automated / Tested / Blocked /
Unverified / Not Applicable.

## BEPS Questionnaire

| Field | Value |
|---|---|
| Route | `/tpa/BEPSQuestionnaireCreator` |
| Exploration status | **Explored, Automated, Tested** — 7/7 RC, 7/7 Staging; on Live `_01`/`_07` Tested and `_02`–`_06` **intentionally excluded** for production safety (see "Environment coverage" below) |
| Business purpose | Build a free-form BEPS-focused questionnaire/memo by inserting pre-authored questions (grouped by BEPS topic) into a rich-text document, then exporting or saving it to a Project. |

**Confirmed live, not assumed**: this page is structurally byte-identical
to WTA's own Tools > Questionnaire Creator
(`pages/wta/tools_questionnaire_creator_page.py`) and to TPA's own FAR
Questionnaire's underlying flow - same Syncfusion rich-text editor
(`div.e-content`), same `Start Over` / `Export` / `Add to Project` toolbar,
same left "Questions" tree grouped by topic. Topics confirmed live: "The
digital economy" (Hybrid mismatch arrangements), "Controlled Foreign
Companies regimes", "Interest deductions/other financial payments",
"Harmful tax practices", "Treaty abuse", "Artificial avoidance of
Permanent Establishment status", "Transfer pricing and intangibles",
"Transfer pricing and risk/capital", "TP and other high risk
transactions", "Data and methodologies", "Disclosure of aggressive tax
planning", "Transfer pricing documentation", "Dispute resolution
mechanisms", "A multilateral instrument".

**Available functionality (confirmed live)**:
- Click a leaf question -> inserted as a formatted block into the editor (editor content length grows).
- `Start Over` -> confirmation dialog ("Confirm Start Over", No/Yes); "Yes" empties the editor, "No" leaves it unchanged.
- `Export` -> icon-only controls present (not driven further this round - presence-only, consistent with the "don't invent destructive/irreversible download assertions" scope decision used elsewhere in this project).
- `Add to Project` -> present only once the editor has content (absent, not merely disabled, on an empty editor - same confirmed gotcha as WTA's own page).
- `Ask AI` -> present (confirmed live, presence-only this round; a real AI-generation round trip is not a deterministic repeatable assertion).
- The editor carries pre-existing, account-level draft content from prior manual/automation use on this shared account (same as WTA's own page) - tests never assume a blank starting state.

**Business rules / validations confirmed live**: none beyond the Start Over confirmation gate - this is a free-form authoring tool, not a structured record with required-field validation (no "duplicate questionnaire name", no save/submit gating found - there is exactly one questionnaire document per account, not a list of many).

**Dependencies**: `Add to Project` saves into the same Projects workspace used by TPA Tools > Projects (not independently re-verified end-to-end this round, consistent with how TPA Tools' own Add-to-Project flows are scoped - verified at the level of "the action is available", not a full save-and-confirm-in-Projects round trip, to avoid duplicating that coverage).

**CRUD coverage**: Create (insert question) / Update (insert another) / Delete (Start Over) are all exercised; there is no "questionnaire listing" to browse (single document per account), so no Read/List/pagination/search test applies here - not invented.

### RESOLVED (2026-11-12): post-Start-Over tree expansion — root cause and fix

Previously status **Blocked** (`_02`-`_06` failing in-suite while passing
standalone). Now **Tested** — 7/7 on RC and 7/7 on Staging, with every
original assertion intact. Nothing was skipped, deleted or weakened; the
tests were failing for a real reason, and that reason was found.

**Root cause — three compounding facts, none of them a wait-tuning issue.**
Diagnosed by dumping the tree's real DOM across a full toggle cycle and by
polling the tree's existence from the moment of navigation (throwaway
discovery scripts, the standard method in this repo):

1. **The toggle icon's class is a CONSTANT, not a state indicator.** The
   row's toggle `<span>` reads `icon-plus` in *every* state — freshly
   expanded, collapsed, and re-expanded alike. So the old approach, which
   located the affordance as `span.icon-plus` and implicitly treated a
   match as meaning "collapsed", was reading a value that never changes.
   The ONLY observable expansion state is the topic row's own child `<ul>`:
   `class="... pl-5 flex flex-col"` / `display: flex` when **expanded**
   versus `class="... pl-5 hidden"` / `display: none` when **collapsed**
   (Tailwind's `hidden`).
2. **The tree is absent from the DOM for ~1.5s after `goto()` returns** —
   measured as `count == 0` immediately after navigation, with the fixture
   leaf first becoming visible ~1.50s later. `Locator.is_visible()` does
   **not** auto-wait, so a bare visibility probe taken right after `goto()`
   returns `False` for a tree that is simply still rendering.
3. **Combined, (1) and (2) inverted the logic.** The old helper probed the
   leaf's visibility immediately after `goto()`, misread "still rendering"
   as "collapsed", and blind-clicked the toggle — thereby **collapsing a
   topic that was already expanded**. After that the leaf could never
   appear: the 10s `wait_for_content` was burned, then the leaf click burned
   its full 60s timeout. That is exactly the signature recorded in
   `logs/TPA BEPS Questionnaire/` (expand click, ~11s gap, ~61s gap, fail),
   repeated identically for `_02`-`_06`.

This also explains the standalone-vs-in-suite asymmetry that made the
original investigation so slow: it was never really about suite sequencing.
A standalone script that happened to interact *after* the tree had rendered
read the state correctly; the in-suite path raced it.

**The fix** (`pages/tpa/tpa_beps_questionnaire_page.py` +
`tests/tpa/beps/test_tpa_beps_questionnaire.py`):

- `goto()` now waits for the question tree to genuinely render before
  returning control, so every subsequent state read is taken against a
  real, settled DOM.
- `topic_child_list()` exposes the child `<ul>` — the real state source.
  Because Tailwind's `hidden` is `display: none`, Playwright's own
  visibility check on that element *is* the expansion state (no
  `page.evaluate`, no class-string parsing), and it is a real locator, so
  it can be waited on to **confirm** an expansion took effect.
- `is_topic_expanded()` reads that state; `ensure_topic_expanded()` toggles
  **at most once and only when genuinely collapsed**, then verifies the
  result via an observable DOM change. Deliberately *not* a retry loop: if
  one honest toggle does not expand the topic, that is a real finding to
  surface, not something to paper over.
- `topic_toggle()` matches on the `icon-` class *prefix*, so the locator no
  longer implies that the match carries state information.
- The post-insert fixed `wait_for_timeout` calls were replaced with
  `wait_for_question_in_editor()`, which waits for the editor to actually
  contain the inserted question (6 fixed waits removed).

**Real, live-confirmed environment difference that makes the state-based
approach mandatory rather than cosmetic**: the tree's *initial* expansion
state genuinely differs per environment. On **RC** the fixture sub-topic
("Hybrid mismatch arrangements") loads already **expanded**; on **Live**
every topic loads **collapsed** (both confirmed via a strictly read-only DOM
probe). Any implementation that hardcodes "expand first", or assumes "it
starts expanded", is therefore wrong on one of the two environments by
construction — the same "read the real state first" lesson as TPA Case
Law's per-environment empty-country data.

Separately re-confirmed real app behavior (not a test bug): re-inserting a
question that is already present is a **no-op**, not a duplicate insert —
which is why `_02` resets via Start Over first.

## BEPS Mapper

| Field | Value |
|---|---|
| Route | `/tpa/beps` |
| Exploration status | **Explored, Automated, Tested** — 7/7 on RC, Staging **and** Live (entirely read-only, so safe to run against production) |
| Business purpose | For a selected jurisdiction, map each BEPS Action (BEPS 1.0, 15 actions) or Pillar (BEPS 2.0, 2 pillars) to where that topic is actually covered across the application's own modules (Transfer Pricing Analyzer / World Tax Analyzer). |

**Real, live-confirmed finding - this is NOT a data-field/ETL mapper**: the
feature name could suggest import/export field mapping; live exploration
confirmed it is instead a navigational/informational tool answering "where
in this app is BEPS Action N actually handled?" for a chosen country.
Confirmed for Australia + "Action 1: Tax Challenges Arising from
Digitalisation": expanding it reveals a "Transfer Pricing Analyzer"
sub-section with 3 checkable leaf items ("Digital economy
transactions-General/-Services covered/-Profit allocation") and a "World
Tax Analyzer" sub-section reading "Not Covered in World Tax Analyzer
(WTA)" - i.e. a legitimate, real "not covered in this other module" result,
not missing data.

**Left panel, confirmed live**:
- Heading: "Jurisdictions, Pillars and Categories" (page-specific wording).
- Country list: byte-identical to `pages/wta/wta_common.py`'s `JurisdictionPanel` (region tabs, "Search countries", same `<label>` shape) - reused unmodified, confirmed not assumed.
- Selecting a country renders a removable "chip" (flag + name + a "Remove" `x` button) next to the "BEPS Mapper" page heading - a distinct UI from every other WTA/TPA jurisdiction page, which just leaves the checkbox checked.
- Placeholder before any Action is picked: "Use the left panel to choose actions." (page-specific wording, distinct from every other page's "...choose jurisdiction.").
- Pillars/Categories panel: an ACCORDION, not a flat `CategoryTree` checklist - top-level rows ("BEPS 2.0"/"BEPS 1.0" groups, each Action/Pillar label) are plain text with a "+" icon and NO underlying `<input>` (confirmed via a direct "preceding-sibling checkbox" probe returning 0 matches) - clicking a label EXPANDS it rather than toggling a selection. Only the nested, 2-levels-deep leaf items (e.g. "Digital economy transactions-General") are real checkboxes, and the checkbox is the `<p>` label's PRECEDING SIBLING `<input>`, not a `<label for>` wrapper (same family of gotcha as WHT Router's Intermediaries modal / `pages/landing_page.py::category_checkbox`, confirmed independently here).
- A top-level "Check All" control is present with the same `#checkAll` id/shape as every other category tree in the project - reused directly since it IS a real top-of-tree action (unlike the per-Action labels).
- `Ask AI` is present (confirmed live, presence-only this round).

**Business rules / validations confirmed live**: none found beyond "an Action with no coverage in a given module legitimately shows 'Not Covered'" - there is no save/submit/create/delete flow on this page (it's a live, read-only-per-selection mapping view), so no CRUD test coverage was invented for it (per the master prompt's own instruction not to manufacture artificial CRUD cases for read-only functionality).

**Dependencies between BEPS Questionnaire and BEPS Mapper**: none found. Live exploration found no shared data, no cross-navigation link, and no API evidence connecting the two - they are two independent sub-features sharing only the same "BEPS" nav grouping. Documented as a genuine finding, not assumed from either module's name.

## Environment validation

All three environments were executed on 2026-11-12 (switching environments
via the project's standard `.env` block toggle + `.auth/state.json`
deletion ritual; `.env` was backed up first and restored byte-identically
afterward). No hardcoded URLs, credentials or environment-specific selectors
are used anywhere in this module - it resolves everything through
`APP_ORIGIN`/`.env` like every other TPA page.

- **RC** — **14/14 pass** (92s). Run via `--feature tpabeps`, or
  independently via `--feature bepsquestionnaire` / `--feature bepsmapper`.
  Confirmed twice: once immediately after the fix, and again as a final
  regression after `.env` was restored to RC.
- **Staging** — **14/14 pass** (82s). No Staging-specific differences
  encountered.
- **Live (production)** — **9 of 14 executed, 9/9 pass; the remaining 5 are
  deliberately EXCLUDED, not failing or unverified.**
  - **Executed and passing (9)**: all 7 BEPS Mapper tests, plus
    `BepsQuestionnaire_01` and `_07`. These are read-only — Mapper only
    selects jurisdictions, expands accordions, toggles a leaf checkbox back
    off again and searches; `_01`/`_07` only assert page load and the deep
    link. Nothing is created, saved, submitted or deleted.
  - **Excluded on Live (5)**: `BepsQuestionnaire_02`, `_03`, `_04`, `_05`,
    `_06`. The reason is specific and not a convenience: the questionnaire
    editor's content is **account-level persisted state** (confirmed live —
    it survives page loads and is shared by anyone using this account), and
    these five either confirm `Start Over` (`_02`, `_05`, `_06`), which
    **wipes that real draft**, or insert questions into it (`_03`, `_04`).
    Running them against production would destroy live user data on a real
    shared account, so they were withheld under the project's standing
    production-safety rule.
  - To keep this honest rather than merely asserted, the *premise* of the
    fix was still verified against Live directly, with a strictly read-only
    DOM probe (no clicks, no writes): the tree renders with the same
    structure (44 rows / 15 topic rows, identical to RC), the toggle icon
    is the same `icon-plus` constant, and the child-`<ul>`
    `hidden`/`flex` state contract holds — the one genuine difference being
    that **every topic loads collapsed on Live**, where RC loads the
    fixture sub-topic expanded. That difference is precisely what the
    state-based fix handles and what the old visibility-probe approach
    could not.
  - Re-enabling the 5 excluded tests on Live would require an approved,
    dedicated production test account whose questionnaire draft is
    expendable. Until such an account exists, running them there should
    stay excluded by choice rather than attempted.
