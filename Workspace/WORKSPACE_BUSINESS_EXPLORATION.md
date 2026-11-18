# Workspace — Business Exploration (Dashboard, Entities, Calendar)

Exploration performed live against RC (`regplusrc.reganalytics.com`), logged in as the
project's standard RC test account (`Handy Home AG`), via throwaway Playwright discovery
scripts (not part of the suite — standard practice for this project, see CLAUDE.md).
Screenshots and raw HTML/innerText dumps were captured during discovery and are not
checked in (scratchpad artifacts only); the findings below are transcribed from those
live captures.

## Scope

**Workspace** is one of the 4 top-level product tabs (Workspace / World Tax Analyzer /
Transfer Pricing Analyzer / RegBriefings — see `pages/landing_page.py`). Clicking it (or
navigating directly) lands on `/companydata/dashboard/`. The left sidebar offers 4 real
items, confirmed via real `<a href="...">` elements (not the no-href `<span>` pattern
RegBriefings' sidebar uses): **Dashboard**, **Entities**, **Calendar**, and **TP
Documenter**. Per this build's explicit scope, only Dashboard/Entities/Calendar are
explored and automated — TP Documenter is confirmed to exist but is intentionally **out
of scope** (not requested, so not invented).

Every one of the 3 in-scope pages supports a direct full-page deep link (confirmed live
for all 3 routes), the same pattern as TPA/RegBriefings/Treaties, not WTA's Tools/
Calculator menu-only restriction.

## Dashboard (`/companydata/dashboard/`)

**Business purpose**: a single-screen risk overview across the account's entities, plus a
feed of upcoming compliance deadlines and relevant tax news, scoped to the risk profile
of the entities' jurisdictions.

Two real sections:

1. **Risk Heatmap** — "A visual overview of risk across your entities". Rendered via a
   yFiles-licensed SVG tree chart (confirmed: the page's own footer text reads "yFiles
   HTML Development License" twice) mapping each entity to its home jurisdiction, color-
   coded by a real High/Medium/No Risk legend (3 real DOM `<span>` + label pairs). The
   chart canvas itself is a third-party widget with no assertable business content beyond
   its legend and heading — automation verifies the legend and heading, not the chart's
   visual render.
2. **News, Alerts & Updates** — a real, filterable feed combining compliance deadlines
   (e.g. "Corporate Income Tax Return (Form C-S/ Form C-S (Lite)/ Form C)", due "30
   November 2026", tagged to "Handy Home Singapore") and tax-news articles (e.g. "UK
   introduces new transfer pricing reporting requirements...", tagged to "Handy Home UK").
   Confirmed live:
   - 4 real chip buttons — "All (N)", "High (N)", "Medium (N)", "No Risk (N)" — the counts
     are genuine, live entity-risk counts for this account (on RC: All=14, High=9,
     Medium=0, No Risk=5). A chip with a real 0 count (`Medium (0)` on this account)
     renders `disabled`, not simply unclickable-but-enabled — confirmed via the real
     `disabled` HTML attribute.
   - Selecting a non-"All" chip (e.g. "High") narrows the feed AND adds a "Filtered" label
     next to the heading — confirmed via a real before/after innerText diff (UK/Canada/
     Brazil news items, which only applied to non-High-risk entities, disappeared).
   - A `placeholder="Search"` text input inside the panel further narrows the same feed.
   - Each feed card is a real `<div id="event-card-<N>">` — a stable id prefix used as the
     "how many items are showing" count proxy.

## Entities (`/companydata/entities/information/data/`)

**Business purpose**: the account's entity master data — every legal entity the account
tracks, its jurisdiction, ownership chain, business type and tax characterization, with
tools to add new entities and view them from 3 different angles.

Confirmed live:

- **3 panels** (`<button class="rs-panel-btn">`), each with its own Data/Chart link(s),
  all mounted in the DOM at once with distinct real hrefs (not an ambiguous-text
  situation):
  - **Entity Information** → Data (`/information/data/`, the default view), Chart
    (`/information/chart/`)
  - **TP View** → Data (`/transferpricing/data/`), Chart (`/transferpricing/chart/`)
  - **Tax Risk** → Chart only (`/taxrisk/chart/`, confirmed no Data view exists for this
    one panel — a real, asymmetric design, not an oversight)
  - A separate "Entity Chart" link also exists; not explored further (out of this build's
    requested surface — the Data grid was the primary ask).
- **The Data grid** is a real `<table>` with a single `<tbody>`, one `<tr>` per entity (22
  real entities on the RC account at time of exploration: "Handy Home AG", "Handy Home
  Singapore", "3rd Party 1", several visibly test/placeholder-named rows like "ownrer"/
  "ffdffd", etc. — real, messy shared-account data, not synthetic fixture data). 9 columns:
  ID, Entity Name, Incorporation Jurisdiction, Sub-National, Tax Residence, Ownership,
  Ownership %, Type, Tax Characterization. Several columns are sortable (`aria-sort`
  attribute, real `th.reg-table-th--sortable`), defaulting to `entityName:asc` (confirmed
  in the URL query string: `?sort=entityName:asc`). No pagination controls were found
  anywhere in the DOM — all entities render on one page at this account's current size;
  this may not hold on an account with many more entities, which is documented here
  rather than assumed to generalize.
- A `placeholder="Search"` input narrows the grid.
- **"Add Entity"** opens a real multi-step wizard modal (3 tabs: Legal/Ownership/Tax).
  Step 1 ("Legal Information") has 5 fields: ID\* (`name="entityCode"`), Name\*
  (`name="entityName"`), Incorporation Jurisdiction\* (an rsuite Select), Sub-National (an
  rsuite Select), Business Type\* (defaults to "Company"), Business SIC Code\* (an rsuite
  Select). **Confirmed live**: the "Next" button's `disabled` attribute renders as
  `disabled=""` (present with an empty value, not absent) while the required fields are
  empty — a real, assertable gate, not merely a visual/CSS-only disabled look.
- **"Import Entities"** button exists (confirmed present) but was not explored further —
  a bulk-import flow is inherently higher-risk to exercise against a shared real account
  and was out of this build's requested scope.

Per this project's production-safety rule, automation only opens/validates/cancels the
Add Entity wizard — it never actually submits a new entity into this shared, real
account.

## Calendar (`/companydata/calendar/`)

**Business purpose**: a compliance-deadline calendar — one real deadline/event per row,
each tied to a specific entity and jurisdiction, with both a list ("Agenda") and a visual
month-grid ("Calendar") view, plus the ability to add new custom compliance events.

Confirmed live:

- **Agenda/Calendar toggle** — a real `reg-toggle-container` with two text labels
  ("Agenda"/"Calendar") and a sliding active-state indicator. Default view is "Agenda" (a
  real `<table>`, 7 rows at time of exploration, columns: Tax Residence, Nature of
  Compliance, Description, Due Date, Applicable Form; sortable, default
  `?sort=dueDate:asc`). Switching to "Calendar" renders a genuine month-grid (confirmed
  via a full-page screenshot: Sun–Sat weekday headers, a "<Month> <Year>" heading with
  prev/next chevrons, and real due-date markers placed on their calendar cells — e.g. a
  "fsddsf" compliance item correctly placed on its 6 Oct 2026 due date).
  - **Real gotcha confirmed live**: an unscoped `get_by_text("Calendar", exact=True)`
    matches the LEFT SIDEBAR nav link before the toggle's own "Calendar" label — the
    toggle's labels must be scoped inside `.reg-toggle-container`.
- **Filters panel** — "Date Range" (defaults to a rolling ~4-month forward window from
  today, e.g. "18-Oct-2026 to 18-Feb-2027" on the day of exploration — a relative window,
  not a fixed literal date), "Filter By" Entity/Jurisdiction (a radio pair, "Entity"
  selected by default), and "Event Types" — the same chip-with-live-count pattern as
  Dashboard's risk chips ("All(7)", "CbC Report (3)", "Custom Event (2)", "CIT Return
  (2)" on the RC account at time of exploration).
- **"Create New Event"** opens a real modal (Single Event/Multiple Events tabs) with:
  Select Country\* (an rsuite combobox, `name="CountryName"`), Nature of Compliance\*
  (`name="Title"`), Description (`name="Description"`), Due Date\* (`name=
  "StartDateTime"`, a masked date picker), External Link (`name="ApplicableForm"`).
  **Confirmed live, a real and important validation gotcha**: `Save` is NOT disabled for
  an empty form (no disabled-button gate the way Entities' "Next" has one) — submitting
  an empty form instead shows 3 real inline errors: "Country name is required", "Title is
  required", "Due date is required", and keeps the modal open. This is the same
  "validate-on-submit, not via a disabled button" shape as TPA Tools Analyzer's "Create
  Analysis" modal.
  **Date-field safety note**: the Due Date field's placeholder format ("Due Date") is a
  masked-input hint. This project has an already-documented, confirmed-live application
  crash elsewhere (WTA's Interest and Penalties calculator) from typing a comma-
  containing literal string into a visually similar masked date field — automation for
  this field never types into it, matching that established safety precedent.

Per this project's production-safety rule, automation only opens/validates/cancels the
Create New Event modal — it never actually creates a new compliance event in this shared,
real account.

## Test coverage (17 tests)

| ID | Module | Category | What it proves |
|---|---|---|---|
| WorkspaceDashboard_01 | Dashboard | Smoke / UI | Risk Heatmap heading + full High/Medium/No Risk legend render |
| WorkspaceDashboard_02 | Dashboard | Smoke / Data | News feed loads with >0 real cards |
| WorkspaceDashboard_03 | Dashboard | Regression / State | Feed starts unfiltered (no "Filtered" badge) |
| WorkspaceDashboard_04 | Dashboard | Functional / Positive | "High" chip adds the "Filtered" badge and narrows the feed (skips, not fails, if the account's real High count is 0 and the chip is disabled) |
| WorkspaceDashboard_05 | Dashboard | Functional / Data | Searching a live-read entity name leaves >=1 card and every card matches |
| WorkspaceDashboard_06 | Dashboard | Navigation | Dashboard/Entities/Calendar sidebar links present |
| WorkspaceEntities_01 | Entities | Smoke / Data | Data grid loads with >0 real rows |
| WorkspaceEntities_02 | Entities | Smoke / UI | Add Entity wizard opens with ID/Name fields; closed without saving |
| WorkspaceEntities_03 | Entities | Negative / Validation | Wizard "Next" is genuinely `disabled` with required fields empty |
| WorkspaceEntities_04 | Entities | Functional / Data | Searching a live-read entity name leaves >=1 row and every row matches |
| WorkspaceEntities_05 | Entities | Regression / Sorting | "Entity Name" defaults to `aria-sort="ascending"` |
| WorkspaceEntities_06 | Entities | Navigation | TP View > Data routes to `/transferpricing/data/` and renders a table |
| WorkspaceCalendar_01 | Calendar | Smoke / Data | Agenda view loads with >0 real rows |
| WorkspaceCalendar_02 | Calendar | Smoke / UI | Calendar toggle renders a real month grid |
| WorkspaceCalendar_03 | Calendar | Smoke / UI | Create New Event modal opens with its fields; cancelled without saving |
| WorkspaceCalendar_04 | Calendar | Negative / Validation | Empty-form Save shows all 3 required-field errors |
| WorkspaceCalendar_05 | Calendar | Data integrity | Event Types "All(N)" count equals the Agenda row count |

Per-test steps, preconditions, test data and actual results are written automatically to
`test_data/Workspace/<Feature>/*.xlsx` on every run (the project's standard format — not
hand-authored).

### Execution results (2026-11-18, final code)

| Environment | Dashboard | Entities | Calendar | Total | Failed / Blocked / Skipped |
|---|---|---|---|---|---|
| RC | 6/6 | 6/6 | 5/5 | **17/17** | 0 / 0 / 0 |
| Staging | 6/6 | 6/6 | 5/5 | **17/17** | 0 / 0 / 0 |
| Live | 6/6 | 6/6 | 5/5 | **17/17** | 0 / 0 / 0 |

All 17 tests are read-only, so Live ran the full suite with no production-safety exclusions.

Defects found during the build were all **automation** defects, each fixed at the root
rather than by loosening an assertion: a bare `goto()` racing the SPA render; two
`role=heading` locators for elements that are not headings; a too-loose Event Types chip
regex that matched "All Entity's Jurisdiction"; and two search tests that used `fill()`
(which never triggers this app's keystroke-driven filter) behind a `<=` check that hid it.
No application defects were found in the in-scope surface.

An earlier RC attempt was also invalidated by a stale cached session (`.auth/state.json`
from two days earlier — the documented stale-session gotcha in CLAUDE.md); it was
discarded, the cache cleared, and every reported result comes from a fresh-session run.

## Known limitations / explicitly out of scope

- **TP Documenter** (the 4th real Workspace sidebar item) — confirmed to exist, not
  automated; not requested for this build.
- **Entities > Import Entities** — confirmed to exist as a button, the underlying bulk-
  import flow was not explored or automated (out of requested scope; higher risk to
  exercise against shared real data).
- **Entities > Chart views / Tax Risk / TP View / Entity Chart** — their own Data/Chart
  routes are confirmed real and reachable, and one navigation test (`WorkspaceEntities_06`)
  confirms TP View's own route switch works, but their full business content was not
  independently explored/automated beyond that — the Entity Information Data grid is the
  primary, requested surface.
- **Role/permission testing** — only the single standard RC/Staging/Live test accounts
  already used throughout this project were available; no second role/permission level
  was observed or could be tested. Documented as unverified rather than assumed absent.
- **Entities' Ownership/Tax wizard steps**, and the "Multiple Events" tab of Create New
  Event, were observed to exist but their own field sets were not independently explored
  beyond what the Legal/Single Event steps already cover — same reasoning as above.
