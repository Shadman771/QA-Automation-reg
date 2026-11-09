# TPA (Transfer Pricing Analyzer) — Business Exploration

Explored live against RC (`https://regplusrc.reganalytics.com`), logged in as the
same shared account used throughout this project. All findings below are
confirmed live via throwaway discovery scripts, not assumed from WTA's shape.

## Entry point

Clicking the **"Transfer Pricing Analyzer"** top tab (one of the 4 product tabs
alongside Workspace / World Tax Analyzer / RegBriefings — see
`pages/landing_page.py`) navigates to `/tpa/Home`. The TPA top nav is:

`Home | Information (dropdown: National Rules, International Guidelines) | News | Forms | Regulations | Case Law | Treaties | Commentary`

**Treaties** and **Commentary** also exist as real top-nav items but are
**out of scope for this initial build** (not part of the 7 features requested).
Documented here for a future round, not automated now.

No viewport-width defect was observed for any TPA top-nav item at the
project's default 1440x900 viewport (unlike WTA's Treaties/Calculators/Tools/
BEPS dropdowns) — confirmed all items visible/clickable at 1440x900, so no
per-directory `browser_context_args` override is needed for TPA tests.

## Feature inventory

| Parent | Sub-feature | Route | Left panel type | Status |
|---|---|---|---|---|
| TPA | Home | `/tpa/Home` | none | Explored |
| TPA | Information > National Rules | `/tpa/NationalRules` | Jurisdiction (country) + Category tree | Explored |
| TPA | Information > International Guidelines | `/tpa/InternationalGuideline` | Guideline body (EU/OECD/UN, category-tree-shaped) + Category tree | Explored |
| TPA | News | `/tpa/News` | Jurisdiction (country) only | Explored |
| TPA | Forms | `/tpa/Forms` | Jurisdiction (country) + flat category list | Explored |
| TPA | Regulations | `/tpa/Regulations` | Jurisdiction (country) only | Explored |
| TPA | Case Law | `/tpa/CaseLaw` | Jurisdiction (country) + Category tree | Explored |
| TPA | Treaties | `/tpa/...` (unconfirmed) | unknown | Out of scope — not explored |
| TPA | Commentary | `/tpa/Commentary` | Jurisdiction (country) only | Explored, built (7 tests) |
| TPA | Tools > Templates | `/tpa/Templates` | none (document table) | Explored, built (7 tests) |
| TPA | Tools > Analyzer | `/tpa/DecisionFlows` | none (analysis list) | Explored, built (7 tests) |
| TPA | Tools > Projects | `/tpa/Project` | none (project list) | Explored, built (7 tests) |
| TPA | Tools > FAR Questionnaire | `/tpa/FARQuestionnaireCreator` | none (questionnaire table) | Explored, built (6 tests) |

## Reusable components (confirmed, no changes needed)

- **`pages/wta/wta_common.py::JurisdictionPanel`** — fully reusable as-is for
  National Rules, News, Forms, Regulations, Case Law. The "Search countries"
  placeholder, region tabs (Asia Pacific/Americas/Europe/MEA), and the
  `<label><span>CountryName</span></label>` country-row shape are byte-for-byte
  identical to WTA's own pages — confirmed live, no TPA-specific override
  needed.
- **`pages/wta/wta_common.py::CategoryTree`** — reusable for National Rules'
  and Case Law's 14-item category list, and (confirmed live, same DOM shape:
  `<input type="checkbox" id="G12"><label for="G12">OECD</label>`) for
  International Guidelines' own "Guideline" selector (EU/OECD/UN) **and**
  its 17-item category list — so International Guidelines needs no new
  panel class, just two `CategoryTree` instances.

Only Forms' flat 4-item category list (TP specific form / Main corporate tax
return / APA forms / Other forms) needs confirming whether it reuses
`CategoryTree` unmodified or needs a simpler variant — not yet selection-
tested for a filtering effect (see Forms section below).

## Per-feature findings

### Home (`/tpa/Home`)
No jurisdiction/category panel — a dashboard-style landing page.
- `h1`: "Recent News" — a feed of real news articles (title, date, excerpt),
  each a real link.
- `h3` cards: "My Projects", "My TPA Research", "Use a Virtual Coach".
- `h4` sections: "Monthly Briefs" (Transfer Pricing Brief: <Month Year>
  entries — real, same monthly-brief shape as RegBriefings' Archive),
  "Quick Access".
- A snippet of recent Forms/Regulations entries with real titles
  (e.g. "Australia_Form_Form: NAT 73345-06.2020").
- "View full tutorial gallery" link.
- Top nav: Home, Information, News, Forms, Regulations, Case Law (plus the
  4 product tabs, Search, Ask AI).

### National Rules (`/tpa/NationalRules`)
Identical shape to WTA's Information/Pillar2 Information pages:
- Left panel: `JurisdictionPanel` (single-select country) + `CategoryTree`
  (14 categories: Requirements, Special areas, Financial transactions,
  Digital economy transactions, Safe harbour, Application, Comparability,
  Documentation, Compliance, Information exchange, Audits, Adjustments,
  APAs, Dispute resolution), "Check All", Depth 1-4.
- Placeholder before selection: "Select Jurisdictions and Categories" /
  "Use the left panel to choose jurisdictions and categories."
- Confirmed live: selecting Australia + "Requirements" renders real content
  — a "Category" selector, sub-topic headings ("Scope of transfer pricing
  rules", "OECD Guidelines", "Related party definition"), each with a real
  paragraph of legal text, an "Export:" control, a "Compare with other
  years" button, and a "BEPS"/"Commentary" toggle area.
- **Calculation-validation anchor candidate**: Australia's "Scope of
  transfer pricing rules" answer references Subdivisions 815-B/C/D of
  ITAA97 — real, verifiable legal text (confirmed live, matches WTA's own
  Australia regulation text seen elsewhere in this project).

### International Guidelines (`/tpa/InternationalGuideline`)
- Left panel: "Guideline" selector (EU/OECD/UN — 3 real options, same
  `CategoryTree`-shaped checkbox list, own "Check All" with id
  `checkAllGuideline` distinct from the category tree's own `#checkAll`)
  + a separate 17-item category `CategoryTree` (Basic rule, Legislative
  design principles, Transfer pricing methods, Measuring and monitoring
  BEPS, Mandatory disclosure rules, Documentation, Comparability, Dispute
  resolution, Intangibles, Intragroup services, Cost contribution
  arrangements, Business restructurings, Financial transactions, Digital
  economy transactions, Interaction with customs valuation, Information
  exchange, Audits and risk assessment).
- Placeholder: "Select Guidelines and Categories" / "Use the left panel to
  choose guideline and categories."
- **Real gotcha**: unlike the country `JurisdictionPanel`'s
  `<label><span>Name</span></label>` wrapping shape, "EU"/"OECD"/"UN" use
  the `CategoryTree` shape (`<input id="G12"><label for="G12">OECD</label>`)
  — a `JurisdictionPanel.country_checkbox()`-style lookup will NOT match
  this panel; use `CategoryTree.category_checkbox()`'s xpath pattern
  instead (confirmed live: the WTA-style country xpath returned 0 matches).
- Content-after-selection not yet captured in this pass (ran out of time
  mid-exploration at this page) — confirm during build before writing the
  calculation-validation anchor for this feature.

### News (`/tpa/News`)
Near-identical to WTA's own News module:
- Left panel: `JurisdictionPanel` only (no categories) — "Jurisdictions"
  heading (plural, no "and Categories").
- 3 tabs: "Treaty Related News", "News Timeline", "Saved Search" (this
  shared RC account already has one real saved search, "dessfff" — a sign
  of real prior manual/automation use, same caution as WTA Tools Projects).
- Confirmed live: selecting Australia renders "News of Australia between
  <DateRange>" (a real, account-local rolling date window — NOT a fixed
  literal date, confirmed by the dates shown: "September 30, 2026 and
  October 30, 2026", i.e. "today minus ~1 month" to "today" — tests must
  compute this dynamically, never hardcode a window), a real article list
  (confirmed: "Australia: ATO extends 2025 public CbC reporting deadline"),
  "Save Searches"/"Start Over" buttons, "Add to Project" per article.

### Forms (`/tpa/Forms`)
Near-identical to WTA's own Forms module:
- Left panel: `JurisdictionPanel` + a flat 4-item category list (TP
  specific form, Main corporate tax return, APA forms, Other forms) — not
  yet confirmed whether selecting one category actually FILTERS the table
  (the exploration run selected "TP specific form" and the table shown
  still displayed what looks like Australia's full form set, including a
  clearly non-TP-specific "Non cillum non quia" seed/placeholder-looking
  row) — **needs explicit before/after row-count confirmation during
  build**, don't assume filtering works until directly verified.
- Table columns: Title, Description, "Applies to tax year ending on",
  Download, Project — same shape as WTA Forms' own table. Real rows
  confirmed (e.g. "Form: NAT 0656-06.2020", "Company tax return 2020",
  "30 June 2020", "English" download link, "Add to Project" button).
- One row ("Non cillum non quia" / "Excepteur laboriosam") is obviously
  Lorem-Picsum-style seed/test data, not real content — confirmed live,
  worth noting as account-specific seed noise, not a defect.

### Regulations (`/tpa/Regulations`)
Simplest of the 7 — `JurisdictionPanel` only, no categories, no table
columns captured yet (ran out of time in this pass selecting a country and
confirming the table shape) — **needs a follow-up pass during build** to
confirm columns/download/add-to-project shape before writing tests (same
"Showing regulations of X" pattern as WTA Regulations is likely, but not
yet confirmed for TPA specifically).

### Case Law (`/tpa/CaseLaw`)
- Left panel: `JurisdictionPanel` + the SAME 14-item `CategoryTree` as
  National Rules (Requirements, Special areas, ... Dispute resolution) —
  confirmed identical category list text, "Check All", Depth 1-4.
- Content-after-selection not yet captured in this pass — needs a
  follow-up during build to confirm the actual table/content shape,
  download links, and any calculation-validation anchor.

## Treaties (full exploration, 2026-11-05)

A later request asked for TPA's own "Treaties" (5 sub-features: Full DTA, PE
Clause, Other Articles, WHT Rates, MLI Data) and "Calculator" (6
sub-features) parent features, mirroring WTA's own shape. **Live
exploration found neither assumption holds for TPA** - documented here in
full rather than inventing the assumed shape:

- **"Treaties" is a single real page, not five.** It is not a direct
  top-nav item at all (unlike WTA) - it lives inside an unlabeled "more"
  overflow menu (a three-dot icon, confirmed via a full nav HTML dump)
  alongside Commentary/Tools/BEPS submenus, all out of scope. Opening
  "Treaties" there reveals exactly ONE child link, labelled **"TP
  Articles"**, routed at `/tpa/Treaties`. There is no Full DTA / PE Clause
  / Other Articles / WHT Rates / MLI Data equivalent anywhere under TPA -
  confirmed by a full nav dump showing only this one child. **Status:
  Explored, Automated, Tested** (`pages/tpa/tpa_treaties_page.py`,
  `tests/tpa/treaties/test_tpa_treaties.py`, 7 tests).

  TP Articles is a single-select `JurisdictionPanel`-only page (no
  categories). Selecting a country renders "Showing treaties of
  `<Country>`" and a real `<table>` with 6 columns: Jurisdiction,
  Competent Authority, Transfer Pricing adjustments, Corresponding
  adjustments, Relief from Double Taxation, Exchange of Information - one
  row per partner country with a real treaty (confirmed on Staging/Live,
  e.g. Bangladesh x Bahrain: Art. 3(1)(h) / Art. 9(1) / Art. 9(2) / Art. 24
  / Art. 27).

  **Real, live-confirmed RC-only application defect**: selecting ANY
  jurisdiction on RC (confirmed across Bangladesh/Singapore/India/China/
  Australia, 5 different countries) shows a blocking "Unable to Complete
  Action - Failed to load Treaties. Please try again later." error instead
  of ever rendering the table. The identical action succeeds immediately
  on both Staging and Live with real data. This is a genuine RC backend
  defect, not a test/locator issue - `test_tpatreaties_02` correctly and
  intentionally FAILS on RC until the real issue is fixed (6/7 pass on RC,
  7/7 on Staging and Live) - the assertion was never weakened to hide it.

  **Navigation gotcha**: the "more" menu's "Treaties" submenu toggle did
  not reliably reveal its nested "TP Articles" link via a plain
  Playwright `.click()` in discovery (the nested `<ul>` stayed `hidden` -
  likely a hover-driven reveal, unlike every other rsuite dropdown in this
  project). Automation uses the confirmed-reliable direct deep link
  instead and only asserts the submenu toggle is discoverable, not that
  clicking through it completes - documented, not silently worked around.

- **"Calculator" / "Calculators" does not exist under TPA at all - Not
  Applicable.** A full nav HTML dump (confirmed on RC, Staging, AND Live)
  shows the complete TPA top nav is: Home, Information (National Rules /
  International Guidelines), News, Forms, Regulations, Case Law, plus the
  "more" overflow menu's Treaties (TP Articles) / Commentary / Tools
  (Templates, Analyzer, Projects, FAR Questionnaire) / BEPS (BEPS
  Questionnaire, BEPS Mapper) submenus. There is no "Calculator" or
  "Calculators" link, button, or submenu entry anywhere, on any of the 3
  environments, and no `/tpa/Calculator`-style route was found. This is a
  **confirmed, documented absence of functionality**, not a blocker to
  work around - per this project's standing rule against inventing
  functionality for features that don't exist, no Calculator automation
  was built for TPA. (WTA's own, pre-existing 6-sub-feature Calculator
  module at `pages/wta/calculator_*.py` / `tests/wta/calculator/` is
  untouched and remains the only Calculator automation in this project.)

## Commentary and Tools — exploration and build (later round, Commentary + Tools only)

A later, separately-scoped request asked for exactly two more TPA parent features: **Commentary** and
**Tools**, with every other existing TPA/WTA module explicitly protected from any change. Explored live
against RC first, per the same standing rule as every other round in this project (never assume business
rules or that a feature mirrors another module's shape).

**Commentary** (`/tpa/Commentary`): a direct `<a href="/tpa/Commentary">` link inside the "more" overflow
menu - NOT a submenu toggle like Treaties/Tools/BEPS, confirmed via the same full nav HTML dump used for
Treaties' own exploration. `JurisdictionPanel`-only; selecting a country renders a "Commentary on
`<Country>`" heading, a "last updated `<date>`" line, an asynchronously-rendered "`<N>` news since the
update" button (opens a "Related News" modal closed via its own "OK" button - confirmed live Escape does
NOT close it), an "Export" control, and a long lettered-section article body. See
`pages/tpa/tpa_commentary_page.py` and `CLAUDE.md` > "TPA" for the full gotcha writeup (sibling-text-node
heading split, async news-button race, embedded-table false positive).

**Tools**: confirmed, via the same nav dump, to be a submenu toggle (same shape as Treaties/BEPS) inside
the "more" menu, holding exactly 4 real children - Templates (`/tpa/Templates`), Analyzer
(`/tpa/DecisionFlows` - the submenu label and the route intentionally differ), Projects (`/tpa/Project`),
FAR Questionnaire (`/tpa/FARQuestionnaireCreator`) - a materially larger menu than WTA's own 2-item Tools
dropdown. **Real, confirmed difference from WTA's own Tools pages**: all 4 of these support a direct
full-page deep link (unlike WTA's Projects/Questionnaire Creator, which redirect to `/wta/Information`).

Each of the 4 Tools sub-pages has its own real shape, not a shared template:
- **Templates**: a sortable document table with a 6-action per-row kebab menu (Preview/Clone
  Document/Edit Document/Delete Document/Export to Word/Export to PDF) and a 5-template picker modal for
  "Create Document".
- **Analyzer**: an analysis list with hover-only Edit/Delete links, a "Create Analysis" modal with a By
  Jurisdiction/By Entity mode pair and 2 required rsuite "Tax Residence" country pickers. Confirmed live:
  `Save` is not disabled for an empty form - it shows real inline required-field errors instead; the
  "Analysis name" field's placeholder is cased differently between "Create Analysis" (`"Analysis name"`)
  and "Edit Analysis" (`"Analysis Name"`).
- **Projects**: a different, richer DOM shape from WTA's own `/wta/Project` - hover-only Export/Edit/Delete
  links (confirmed via a full row HTML dump, correcting an initial mis-read based on `is_visible()` not
  accounting for CSS `opacity`), and a 3-tab (Regulatory Reports/Research/Documents) detail pane per
  project.
- **FAR Questionnaire**: an AI-driven "Add FAR Questionnaire" flow (Title + SIC Code required, optional
  file attachments, "Create & Generate" starts disabled and enables once both required fields are filled),
  with the same 5-action kebab-menu shape as Templates' own rows.

Full per-page gotcha writeups (async table-load races on Templates/Projects/FAR Questionnaire, the
Analyzer placeholder-casing bug, the Commentary news-button/modal races) live in `CLAUDE.md` > "TPA" rather
than being duplicated here. Built: `pages/tpa/tpa_commentary_page.py`, `pages/tpa/tpa_tools_common.py`,
`pages/tpa/tpa_tools_templates_page.py`, `pages/tpa/tpa_tools_analyzer_page.py`,
`pages/tpa/tpa_tools_projects_page.py`, `pages/tpa/tpa_tools_far_questionnaire_page.py`, plus
`tests/tpa/commentary/` (7 tests) and `tests/tpa/tools/` (33 tests: 6 navigation + 7 Templates + 7
Analyzer + 7 Projects + 6 FAR Questionnaire) - 40 new tests, all passing on RC as of this round. Every
existing TPA/WTA module (Home, National Rules, International Guidelines, News, Forms, Regulations, Case
Law, Treaties, and all of WTA) was left untouched, per this round's explicit scope restriction.

## Outstanding exploration gaps (to close during build, not before)

Per the user's explicit pacing choice ("explore first, then build all
sub-features, reviewed as I go"), the high-level shape of all 7 features is
now confirmed enough to start building page objects feature-by-feature.
Three features (International Guidelines' content render, Regulations'
table shape, Case Law's content/table shape) need one more targeted
discovery pass each — done immediately before writing that feature's page
object and tests, not deferred to the end, so nothing is built from a
guess.

## Environments

Explored only against RC so far (the environment the suite's `.env` was
already pointed at before this task started). Staging/Live structural
parity not yet confirmed — per the user's env-validation choice ("full run
against all 3 environments for every sub-feature"), each sub-feature's
tests will be run against RC, Staging, and Live before being considered
done, which will also surface any structural differences between
environments for TPA, the same way it did for WTA/RegBriefings.
