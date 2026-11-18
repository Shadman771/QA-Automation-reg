# Workspace — Business Exploration (Dashboard, Entities, Calendar)

Explored live on RC (`regplusrc.reganalytics.com`, account chart "Handy Home AG") with
throwaway Playwright discovery scripts (not part of the suite — the project's standard
practice, see CLAUDE.md). The first pass (2026-11-18) was read-only; the second pass the
same day exercised every create / edit / delete operation with throwaway records named
`WorkspaceQA_...`, all of which were deleted again. Findings below are transcribed from those
live sessions and were then re-confirmed by the automated suite on RC, Staging and Live.

## Scope

**Workspace** is one of the 4 top-level product tabs (Workspace / World Tax Analyzer /
Transfer Pricing Analyzer / RegBriefings). It lands on `/companydata/dashboard/`. The sidebar
has 4 real links: **Dashboard**, **Entities**, **Calendar** and **TP Documenter**. Only the
first three are in scope; TP Documenter exists but was not requested and is not automated.
Every in-scope page supports a direct deep link.

A chart selector (top-left, "Handy Home AG") lists the account's entity charts and offers
"Add Entity Chart". Chart-level management is outside the three requested modules and is not
automated; all tests work inside whichever chart the account opens by default.

## What can be created, changed and deleted

| Operation | Exists? | Where / how | Automated |
|---|---|---|---|
| Create entity | Yes | Entities > Add Entity (3-step wizard) | Yes |
| Edit entity | Yes | Entity row menu > Edit (same wizard, "Edit Entity") | Yes |
| Delete entity | Yes | Entity row menu > Delete > confirm | Yes |
| Bulk-import entities | Yes | Entities > Import Entities (.xlsx upload, column mapping) | Dialog only — never uploads (cannot be cleanly undone) |
| Export entities | Yes | Entities > Export as Excel | Yes (download verified) |
| Edit an entity's related parties | Yes | TP View > Data > row menu > Edit | Dialog opened and cancelled only (saving would alter pre-existing entities' relationships) |
| Delete from TP View | **No** | TP View's row menu has Edit only | Asserted absent |
| Create custom event | Yes | Calendar > Create New Event > Single Event | Yes |
| Edit custom event | Yes | Event row menu > Edit ("Edit Event") | Yes |
| Delete custom event | Yes | Event row menu > Delete > confirm | Yes |
| Edit / delete a system deadline | **No** | CbC Report, CIT Return etc. rows have no row menu | Asserted absent |
| Bulk-upload events | Yes | Create New Event > Multiple Events (.xlsx, optional "Replace the existing events") | Tab inspected only — never uploads |
| Event detail view | **No** | Clicking an Agenda row or a month-grid event opens nothing; the row's chevron only expands the row inline | Not applicable |
| Dashboard create / edit / delete | **No** | The Dashboard only displays Entities and Calendar data | Covered through cross-module tests |
| Dashboard chart drill-down | **No** | The heatmap is a canvas with a 4-button view toolbar; nodes do not navigate | Chart + toolbar presence asserted |

## Dashboard (`/companydata/dashboard/`)

**Business purpose**: one screen showing risk across the account's entities plus upcoming
compliance deadlines and tax news for the entities' jurisdictions.

- **Risk Heatmap** — a canvas chart (yFiles) with one node per entity, a High / Medium / No
  Risk legend and a 4-button view toolbar. A newly created entity appears as a node and
  disappears when deleted.
- **News, Alerts & Updates** — one card per entity (`<div id="event-card-N">`: entity name,
  jurisdiction flag, then that jurisdiction's deadlines and news). Custom calendar events
  appear here too.
  - Risk chips "All (N)", "High (N)", "Medium (N)", "No Risk (N)" — counts are in the
    accessible name; High + Medium + No Risk = All. A chip with count 0 carries a real
    `disabled` attribute. Chips are single-select; the active one gets a colour-suffixed
    class. Selecting a risk chip adds a "Filtered" label and leaves only items whose
    coloured bar matches (red for High, green for No Risk).
  - Search filters on keystrokes, is case-insensitive, and a no-match search shows "No news
    or updates match your current search or filter."
  - "Collapse panel" hides the feed and leaves the heatmap.

## Entities (`/companydata/entities/information/data/`)

**Business purpose**: the account's legal-entity master data — jurisdiction, ownership chain,
business type and tax characterization — viewed as data grids or charts.

- **Views**: Entity Information (Data, Chart), TP View (Data, Chart), Tax Risk (Chart only).
  All five routes deep-link. The three chart views render a canvas with Filters and
  Properties buttons; TP View's chart draws only entities that have related parties.
- **Entity Information grid**: ID, Entity Name, Incorporation Jurisdiction, Sub-National, Tax
  Residence, Ownership, Ownership %, Type, Tax Characterization. Entity Name, Incorporation
  Jurisdiction, Tax Residence and Type sort both ways (`aria-sort` + `?sort=field:dir`); the
  Ultimate Parent Entity stays pinned first. No pagination at 22–32 entities. Search filters
  on keystrokes, is case-insensitive, and a no-match search shows
  "No Entities Yet".
- **Add Entity wizard**
  - *Legal*: ID\*, Name\*, Incorporation Jurisdiction\*, Sub-National (disabled until a
    jurisdiction is chosen), Business Type\* (default Company; UPE is disabled once the chart
    has one), Business SIC Code\*. Next is disabled until all required fields are filled;
    whitespace-only ID / Name count as empty.
  - *Ownership*: "Owned by entities in this chart" (owner + % rows; must total exactly
    100.00%; each % must be 0.01–100, an out-of-range value is refused and the field keeps
    its previous value; an owner already chosen is not offered again) or "Owner unknown / not
    assigned yet". Next is disabled until one of the two is satisfied. Back keeps the Legal
    data.
  - *Tax*: Tax Resident Jurisdiction\* (defaults to the incorporation jurisdiction),
    Financial Year End\* (pre-filled), Tax Characterization list, custom TCT, Save.
  - A duplicate ID is rejected only on Save: "Entity ID already exists", wizard stays open,
    nothing is created. (Whether duplicate names are allowed was not tested.)
  - Special characters and a 250+ character name are stored exactly as typed.
  - Escape closes the wizard at any step and discards everything (there is no Cancel button).
- **Edit**: same wizard titled "Edit Entity", pre-filled, with Save available on every step.
- **Delete**: "Delete Entity — Are you sure you want to delete <name>?" with Cancel / Delete.
- **Cross-module**: a created entity is offered in the Calendar's entity filter and drawn on
  the Dashboard heatmap; both stop showing it once it is deleted.

## Calendar (`/companydata/calendar/`)

**Business purpose**: compliance deadlines per jurisdiction — system deadlines generated for
the jurisdictions the account has entities in, plus user-created custom events — as a list
(Agenda) or a month grid (Calendar).

- **Agenda**: Tax Residence, Nature of Compliance, Description, Due Date, Applicable Form.
  The first three of those that are sortable (Tax Residence, Nature of Compliance, Due Date)
  sort both ways. Search filters on keystrokes and the Event Type counts follow the search;
  a no-match search shows "Stay on Top of Compliance Deadlines".
- **Calendar view**: a month grid starting on the Date Range's first month; the chevrons
  move one month per click. The page title reads "Agenda" or "Calendar" with the view.
- **Filters**
  - Date Range: a rolling window (about one month back to three months ahead), with presets
    such as "This Year".
  - Filter By Entity (default "All Entity's Jurisdiction") or Jurisdiction. Under the Entity
    filter only jurisdictions where the account has an entity are listed; Jurisdiction with
    nothing selected lists every jurisdiction. **Consequence**: a custom event created for a
    country with no entity is saved but invisible in the default view.
  - Event Types chips with live counts; multi-select; the type counts sum to "All", which
    equals the number of rows.
  - The Filters panel can be collapsed.
- **Create New Event > Single Event**: Select Country\*, Nature of Compliance\*, Description,
  Due Date\* (date picker), External Link. Save is never disabled; each missing required
  field produces its own message ("Country name is required", "Title is required", "Due date
  is required"). Cancel discards the form.
- **Edit** (custom events only): "Edit Event", pre-filled with every saved value.
- **Delete** (custom events only): "Do you want to delete the event '<title>'? This action
  is irreversible." with Cancel / Delete.
- **Accepted without validation** (documented behaviour, each asserted as it really works):
  past due dates, duplicate titles, long and special-character text. A non-URL External Link
  is also accepted (observed during exploration; not automated).
- **Cross-module**: a created event appears in the month grid and in the Dashboard feed, and
  raises the "All" and "Custom Event" counts by one; all revert on delete.

## Application defect found

**Calendar — a whitespace-only "Nature of Compliance" is accepted.** The field is required,
but a value consisting only of spaces passes validation and is saved as an event with a
blank title (the delete dialog then reads "delete the event ''"). Reproduced on RC,
Staging and Live by `WorkspaceCalendar_24`, which is kept as a failing test until the application is
fixed; the blank event the test creates is deleted every time. By contrast the Entities
wizard handles the same input correctly (whitespace-only ID / Name keep Next disabled).

## Test coverage (122 tests)

| Module | Before | Now | What the new tests add |
|---|---|---|---|
| Dashboard | 6 | 20 | Risk-count integrity, chip enablement, single-select and reset, per-risk filtering by bar colour, no-match and case-insensitive search, clearing the search, panel collapse, heatmap chart and toolbar, card completeness, feed-vs-Entities integrity, sidebar navigation |
| Entities | 6 | 56 | Create / persist / count, edit name, edit pre-fill, edit tax characterization, delete cancel / confirm, owned entity, special and long names, search, business type, Calendar and Dashboard linkage; each required field, whitespace, step gating, Sub-National dependency, ownership total and range rules, duplicate owner, Back, cancel at each of the 3 steps, duplicate ID, Tax defaults; sort on all 4 sortable columns, no-match / case-insensitive / partial search, import dialog, Excel export, row menus, TP View grid / menu / related-party dialog, 3 chart views; leftover sweep |
| Calendar | 5 | 46 | Create / persist, count changes, external link, month grid, edit, edit pre-fill, re-date, delete cancel / confirm, system rows have no actions, Dashboard linkage, search, duplicate titles, past date; each required field, whitespace title (defect), special / long text, Cancel, recovery after errors, Multiple Events tab, tab switching; sort on all 3 sortable columns, single and combined type chips, count integrity, search, empty state, Jurisdiction filter, single jurisdiction, single entity, default date range, "This Year", filter collapse, month navigation, view round trip; leftover sweep |

Test IDs: `WorkspaceDashboard_01–20`, `WorkspaceEntities_01–55` and `_99`,
`WorkspaceCalendar_01–45` and `_99`. Steps, test data, expected and actual results for every
case are written to `test_data/Workspace/<Feature>/*.xlsx` on each run (the project's
standard, generated format).

### Test-data safety

- Every record a test creates is named `WorkspaceQA_<tag>_<timestamp>` and deleted in a
  `finally` block, including when the test fails.
- `WorkspaceEntities_99` and `WorkspaceCalendar_99` run last, search every jurisdiction for
  the `WorkspaceQA_` prefix, delete anything found, and fail if anything was there.
- Pre-existing entities and events are never edited or deleted. Two tests reference an
  existing entity as an owner / read its ID; neither changes it.
- Nothing is uploaded through Import Entities or Multiple Events on any environment.

### Execution results (2026-11-18, final code)

Each module was run on its own and then all three together, on each environment.

| Environment | Dashboard | Entities | Calendar | Combined | Failed | Blocked | Skipped | Excluded |
|---|---|---|---|---|---|---|---|---|
| RC | 20/20 | 56/56 | 45/46 | **121/122** | 1 | 0 | 0 | 0 |
| Staging | 20/20 | 56/56 | 45/46 | **121/122** | 1 | 0 | 0 | 0 |
| Live | 20/20 | 56/56 | 45/46 | **121/122** | 1 | 0 | 0 | 0 |

The one failure on each environment is `WorkspaceCalendar_24` (the application defect
above). No test data was left behind on any environment (both sweeps passed on every run).

A first Live run scored 118/122: three Entities tests read the grid count, the Edit wizard and
the related-party list before Live (noticeably slower) had finished loading them. They were
fixed with waits on the real content, and Entities alone plus the combined suite were then
re-run on all three environments to give the figures above.

## Not automated, and why

- **TP Documenter** and **entity-chart management** — outside the three requested modules.
- **Import Entities upload** and **Multiple Events upload** — bulk writes that cannot be
  cleanly reversed through the UI ("Replace the existing events" would overwrite real data).
- **Saving related parties in TP View** — would change relationships of pre-existing entities.
- **Custom Tax Characterization ("Apply Custom TCT")** — appears to add an account-level
  option; no way to remove one was found, so it was not exercised.
- **Sub-National values** — the list is empty for the jurisdiction used by the tests; only
  its enable/disable dependency is asserted.
- **External Link format** — the app accepts any text; observed, not asserted.
- **Roles and permissions** — one account per environment was available; no second role
  could be tested.
- **Chart contents** — the charts are canvases; presence, controls and entity labels are
  asserted, not the drawing itself.
