"""Workspace > Entities (`/companydata/entities/information/data/`), the
default "Entity Information > Data" view.

Confirmed live via scratchpad discovery (full HTML dump, not part of the
suite): this is a real entity-management workspace, structurally closer to
a data grid than any WTA/TPA/RegBriefings page built so far.

**Panel/tab shape** - 3 panels (`<button class="rs-panel-btn">`), each with
its own Data/Chart link(s), all mounted in the DOM at once with distinct
real `href`s (confirmed: NOT the "ambiguous text match" rsuite-dropdown
gotcha documented elsewhere in this project - every link here has its own
unique href, so they're targeted by href, never by ambiguous link text):
  - "Entity Information" -> Data (`/information/data/`, the default view),
    Chart (`/information/chart/`)
  - "TP View" -> Data (`/transferpricing/data/`), Chart
    (`/transferpricing/chart/`)
  - "Tax Risk" -> Chart only (`/taxrisk/chart/`, no Data view - confirmed
    live, not an oversight)
  - A separate top-level "Entity Chart" link also exists but was not
    explored further (out of this build's scope - the Data grid is the
    primary, requested surface).

**The Data grid** is a real `<table>` (confirmed via HTML dump: a single
`<tbody>` with one `<tr>` per entity, NOT a div-based layout) with 9
sortable-or-plain columns (ID, Entity Name, Incorporation Jurisdiction,
Sub-National, Tax Residence, Ownership, Ownership %, Type, Tax
Characterization). Sortable columns render `aria-sort` and default to
`entityName:asc` (confirmed in the URL query string on load: `?sort=
entityName:asc`). No pagination controls were found in the DOM (confirmed
by searching the whole page for any pagination/rows-per-page marker) - the
account's ~22 entities all render on one page; this may not hold on an
account with far more entities, documented here rather than assumed.

**"Add Entity"** opens a real multi-step wizard modal (3 tabs: Legal/
Ownership/Tax). Its first ("Legal Information") step has 5 fields - ID*,
Name*, Incorporation Jurisdiction* (a Select), Sub-National (a Select),
Business Type* (defaults to "Company"), Business SIC Code* (a Select) -
and a "Next" button, confirmed live NOT clickable through to creation
without filling the required fields. Per this project's production-safety
rule, automation only opens/validates/cancels this modal - it never
actually submits a new entity into this shared, real account (same
judgment as Repatriation Calculator's "Add to Project" dialog discovery,
scaled up for a modal this project has not been asked to fully exercise
end-to-end)."""
from playwright.sync_api import Page

from pages.workspace.workspace_common import WORKSPACE_ENTITIES_URL, workspace_goto
from utils.wait import wait_for_content


class WorkspaceEntitiesPage:
    def __init__(self, page: Page):
        self.page = page
        self.panel_entity_information = page.get_by_role("button", name="Entity Information", exact=True)
        self.panel_tp_view = page.get_by_role("button", name="TP View", exact=True)
        self.panel_tax_risk = page.get_by_role("button", name="Tax Risk", exact=True)

        self.link_information_data = page.locator('a[href="/companydata/entities/information/data/"]')
        self.link_information_chart = page.locator('a[href="/companydata/entities/information/chart/"]')
        self.link_tp_view_data = page.locator('a[href="/companydata/entities/transferpricing/data/"]')
        self.link_tp_view_chart = page.locator('a[href="/companydata/entities/transferpricing/chart/"]')
        self.link_tax_risk_chart = page.locator('a[href="/companydata/entities/taxrisk/chart/"]')

        self.search_input = page.locator('input[placeholder="Search"]').first
        self.add_entity_button = page.get_by_role("button", name="Add Entity", exact=True)
        self.import_entities_button = page.get_by_role("button", name="Import Entities", exact=True)

        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.column_header = lambda name: page.locator("th").filter(has_text=name)

        # Add Entity modal
        # The wizard's "Add Entity" title is a plain `<div class="text-18-medium">`
        # in the modal's left side-nav, NOT a role=heading (confirmed live via
        # a modal-scoped HTML dump after a real run failed on a heading
        # locator). Scoped to the modal wrapper so it can't match the page's
        # own "Add Entity" button outside it.
        self.modal_wrapper = page.locator(".rs-modal-wrapper")
        self.modal_heading = self.modal_wrapper.get_by_text("Add Entity", exact=True)
        self.modal_tab_legal = page.get_by_text("Legal", exact=True)
        self.modal_tab_ownership = page.get_by_text("Ownership", exact=True)
        self.modal_tab_tax = page.get_by_text("Tax", exact=True)
        # Real `name` attributes confirmed via a modal-scoped HTML dump
        # (`entityCode`/`entityName`) - not guessed label-proximity xpath.
        self.modal_id_input = page.locator('input[name="entityCode"]')
        self.modal_name_input = page.locator('input[name="entityName"]')
        self.modal_next_button = page.get_by_role("button", name="Next", exact=True)
        self.modal_cancel_button = page.get_by_role("button", name="Cancel", exact=True)

    def goto(self):
        """Waits for the real 'Add Entity' button (present regardless of
        grid-loading timing) before returning control - the same
        `goto_and_wait_ready` discipline every other page object in this
        project follows, to avoid racing this SPA's render (confirmed live
        via a real test run: a bare `page.goto()` with no ready-wait can
        leave the next click/assert hitting a still-rendering page)."""
        workspace_goto(self.page, WORKSPACE_ENTITIES_URL)
        wait_for_content(self.add_entity_button, timeout=30000)

    def is_next_button_disabled(self) -> bool:
        """The real `disabled` attribute renders as `disabled=""` (empty
        string, not absent) when the wizard's required fields aren't all
        filled - confirmed live via `get_attribute()`, so the check must be
        `is not None`, not a truthiness check on the empty string itself."""
        return self.modal_next_button.get_attribute("disabled") is not None

    def entity_row_count(self) -> int:
        return self.table_rows.count()

    def type_search(self, term: str):
        """Real gotcha confirmed live: the grid search filters on keystroke
        events, so Playwright's `fill()` (sets the value with no key events)
        leaves the grid unfiltered - 22 rows stayed 22. Typing key-by-key
        filters immediately (22 -> 1 for "Singapore")."""
        self.search_input.press_sequentially(term, delay=40)

    def entity_names(self) -> list:
        """Every visible row's 'Entity Name' cell, located by the header's
        own column index rather than a hardcoded position."""
        return self.page.evaluate("""() => {
            const ths = [...document.querySelectorAll('table thead th')];
            const idx = ths.findIndex(th => th.innerText.trim() === 'Entity Name');
            if (idx < 0) return [];
            return [...document.querySelectorAll('table tbody tr')]
                .map(tr => (tr.children[idx]?.innerText || '').trim());
        }""")

    def column_sort_state(self, column_name: str) -> str:
        """Returns the real `aria-sort` attribute ("ascending"/"descending"
        /"none") of a sortable column header, confirmed live to be the
        genuine sort-state signal (not a CSS class guess)."""
        header = self.column_header(column_name).first
        return header.get_attribute("aria-sort") or ""

    def close_add_entity_modal(self):
        """Closes the Add Entity wizard without creating anything - via its
        own Cancel button, falling back to Escape if Cancel is somehow
        absent (never leaves a stray creation in progress)."""
        try:
            if self.modal_cancel_button.count():
                self.modal_cancel_button.first.click()
                return
        except Exception:
            pass
        self.page.keyboard.press("Escape")
