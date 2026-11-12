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
| Exploration status | **Explored, Automated; Tested PARTIALLY on RC — 2/7 pass, 5 BLOCKED** (see "Blocked: post-Start-Over tree expansion" below) |
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

### Blocked: post-Start-Over tree expansion (status **Blocked**, honestly reported)

`BepsQuestionnaire_01` and `_07` pass reliably on RC. `_02` through `_06`
are currently **BLOCKED**, all on the same single unresolved interaction:
re-inserting a question *after* a Start Over, within a sequential suite run.
They are left in place, with their assertions fully intact - deliberately
NOT deleted, skipped, or weakened to manufacture a green run.

What was established live, across five full suite runs plus four standalone
diagnostics (each finding is reproducible, and each is already documented in
`pages/tpa/tpa_beps_questionnaire_page.py`):

- On a normal load the question leaf is already visible and a plain click
  inserts it correctly. This is why `_01`/`_07` pass.
- A Start Over collapses the leaf's sub-topic. Playwright's `force=True`
  does **not** help (force still requires visibility - forced clicks failed
  fast with "Element is not visible").
- Clicking the topic row's **text** does not re-expand a collapsed topic.
- Clicking the row's own `span.icon-plus` **does** re-expand it in a
  standalone script (verified: leaf became visible, insert grew the editor
  11 -> 357 chars) - but the identical call inside the suite still leaves
  the leaf hidden past a 10s `wait_for_content`, so some state difference
  between the standalone and in-suite sequences is still unaccounted for.
- Separately confirmed real app behavior (not a test bug): re-inserting a
  question that is already present is a **no-op**, not a duplicate insert
  (editor stayed at exactly 357 chars) - which is why `_02` resets via
  Start Over first.

Next step for whoever picks this up: instrument the in-suite failure
directly (dump the sub-topic `<li>`'s outer HTML and the leaf's computed
style at the moment the expand icon click lands) to find what differs from
the standalone case. The remaining unknown is narrow and well-bounded; it is
an automation-side interaction problem, with no evidence so far of an
application defect.

## BEPS Mapper

| Field | Value |
|---|---|
| Route | `/tpa/beps` |
| Exploration status | **Explored, Automated, Tested** (RC) |
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

- **RC**: both sub-features explored and automated against. Final RC run: **9/14 pass** - **BEPS Mapper 7/7** (fully green), **BEPS Questionnaire 2/7** with `_02`-`_06` Blocked on the single tree-expansion interaction described above. Run via `--feature tpabeps`, or independently via `--feature bepsquestionnaire` / `--feature bepsmapper`.
- **Staging / Live**: not run this round within the available time budget - the automation itself is environment-agnostic (no hardcoded URLs/credentials/country, uses `APP_ORIGIN`/`.env`/live-confirmed country names the same way every other TPA page does), so running it against Staging/Live only requires the project's standard `.env` switch + `.auth/state.json` deletion ritual. Flagged honestly as **Unverified** on those two environments rather than claimed without execution.
