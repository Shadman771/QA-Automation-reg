"""Workspace > Entities (`/companydata/entities/information/data/`), the
default "Entity Information > Data" view.

Confirmed live via scratchpad discovery (full HTML dumps plus a real
create/edit/delete of a throwaway entity on RC, not part of the suite):
this is a real entity-management workspace with complete CRUD.

**Panel/tab shape** - 3 panels (`<button class="rs-panel-btn">`), each with
its own Data/Chart link(s), all mounted in the DOM at once with distinct
real `href`s (so they are targeted by href, never by ambiguous link text):
  - "Entity Information" -> Data (`/information/data/`, default), Chart
  - "TP View" -> Data (`/transferpricing/data/`), Chart
  - "Tax Risk" -> Chart only (`/taxrisk/chart/`, no Data view)

**The Data grid** is a real `<table>` (one `<tr>` per entity) with columns
ID, Entity Name, Incorporation Jurisdiction, Sub-National, Tax Residence,
Ownership, Ownership %, Type, Tax Characterization. Entity Name,
Incorporation Jurisdiction, Tax Residence and Type are sortable
(`aria-sort` + a `?sort=<field>:asc|desc` URL param; default
`entityName:asc`). No pagination controls exist at the test accounts'
entity counts (22-32). The search box filters on KEYSTROKES (`fill()` does
nothing); a no-match search replaces the table with a "No Entities Yet"
empty state.

**Full CRUD** (all confirmed live):
  - "Add Entity" opens a 3-step wizard (Legal -> Ownership -> Tax) that
    POSTs `api/CompanyData/AddOrEditEntity`.
  - Each row's kebab (icon button in the first cell) offers Edit (the same
    wizard titled "Edit Entity", with `Save` available on every step) and
    Delete (a "Delete Entity / Are you sure you want to delete <name>?"
    Cancel/Delete confirm).

Wizard facts:
  - Step 1: ID* (`entityCode`), Name* (`entityName`), Incorporation
    Jurisdiction*, Sub-National (disabled until a jurisdiction is picked),
    Business Type* (default "Company"), Business SIC Code*. `Next` carries
    a real `disabled=""` attribute (present with an empty value) until
    every required field is filled; whitespace-only ID/Name count as empty.
  - Step 2: "Owned by entities in this chart" (default; owner + % rows that
    must total exactly 100.00%, each % limited to 0.01-100, an already
    chosen owner is removed from the next row's options) or "Owner unknown
    / not assigned yet" (the grid then shows "— Unassigned").
  - Step 3: Tax Resident Jurisdiction* (defaults to the incorporation
    jurisdiction), Financial Year End*, a Tax Characterization list, Save.
  - A duplicate ID is rejected only by the server on Save: HTTP 400,
    "Unable to Complete Action / Entity ID already exists", the wizard
    stays open and nothing is created.
  - Special characters and very long names (278 chars) are stored intact.
  - **Escape closes the whole wizard and discards everything**, even while
    a picker is open - never press Escape to dismiss a picker here. The
    wizard has no Cancel button; Escape is its cancel path.

Other real controls: "Import Entities" (an .xlsx upload dialog -
automation only opens/validates/cancels it, because a bulk import cannot
be cleanly undone), "Export as Excel" (downloads a real .xlsx), TP View >
Data (row kebab has Edit only - a related-party picker - and no Delete),
and three canvas chart views with Filters/Properties buttons.

Automation only ever creates, edits and deletes entities it named
`WorkspaceQA_<tag>_<timestamp>` itself."""
import re

from playwright.sync_api import Page

from pages.workspace.workspace_common import WORKSPACE_ENTITIES_URL, workspace_goto
from utils.wait import wait_for_content

ENTITIES_BASE = WORKSPACE_ENTITIES_URL.split("/information/data/")[0]


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
        self.add_entity_button = page.get_by_role("button", name="Add Entity", exact=True).first
        self.import_entities_button = page.get_by_role("button", name="Import Entities", exact=True).first

        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.column_header = lambda name: page.locator("th").filter(has_text=name)

        # ---- Add/Edit Entity wizard ----
        # The wizard's title is a plain `<div class="text-18-medium">` in
        # the modal's left side-nav, NOT a role=heading (confirmed live).
        self.modal_wrapper = page.locator(".rs-modal-wrapper")
        self.modal_heading = self.modal_wrapper.get_by_text("Add Entity", exact=True)
        self.modal_edit_heading = self.modal_wrapper.get_by_text("Edit Entity", exact=True)
        self.modal_tab_legal = page.get_by_text("Legal", exact=True)
        self.modal_tab_ownership = page.get_by_text("Ownership", exact=True)
        self.modal_tab_tax = page.get_by_text("Tax", exact=True)
        self.modal_id_input = page.locator('input[name="entityCode"]')
        self.modal_name_input = page.locator('input[name="entityName"]')
        self.modal_next_button = page.get_by_role("button", name="Next", exact=True)
        self.modal_cancel_button = page.get_by_role("button", name="Cancel", exact=True)
        self.modal_back_button = self.modal_wrapper.get_by_role("button", name="Back", exact=True)
        self.modal_save_button = self.modal_wrapper.get_by_role("button", name="Save", exact=True)
        self.step_legal_heading = self.modal_wrapper.get_by_text("Legal Information", exact=True)
        self.step_ownership_heading = self.modal_wrapper.get_by_text("Ownership Information", exact=True)
        self.step_tax_heading = self.modal_wrapper.get_by_text("Tax Information", exact=True)

        combos = self.modal_wrapper.locator("[role='combobox']")
        self.jurisdiction_combo = combos.filter(has=page.locator('input[name="incorporationJurisdiction"]'))
        self.sub_national_combo = combos.filter(has=page.locator('input[name="subNational"]'))
        self.business_type_combo = combos.filter(has=page.locator('input[name="businessType"]'))
        self.tax_residence_combo = combos.filter(has=page.locator('input[name="taxResidenceJurisdiction"]'))
        # The SIC picker's hidden input has no `name` (confirmed via HTML
        # dump), so it is the one wizard combobox reachable only by
        # position: 4th of the 5 mounted comboboxes.
        self.sic_combo = combos.nth(3)
        self.options = page.locator("[role='option']")

        self.owner_unassigned_radio = self.modal_wrapper.get_by_text("Owner unknown / not assigned yet", exact=True)
        self.owner_owned_radio = self.modal_wrapper.get_by_text("Owned by entities in this chart", exact=True)
        self.owner_combos = combos.filter(has=page.locator('input[name="ownerId"]'))
        self.ownership_pct_inputs = self.modal_wrapper.locator('input[name="ownershipPercentage"]')
        self.add_another_owner_button = self.modal_wrapper.get_by_role("button", name="Add Another Owner", exact=True)
        self.pct_range_error = self.modal_wrapper.get_by_text("Ownership Percentage must between 0.01 and 100", exact=True)
        self.duplicate_id_error = page.get_by_text("Entity ID already exists", exact=False)
        self.financial_year_end_input = self.modal_wrapper.locator('input[placeholder="Select Day & Month"]')

        # ---- Row actions / delete confirm ----
        self.menu_edit = page.get_by_text("Edit", exact=True)
        self.menu_delete = page.get_by_text("Delete", exact=True)
        self.delete_dialog_text = self.modal_wrapper.get_by_text(re.compile(r"Are you sure you want to delete"))
        self.delete_confirm_button = self.modal_wrapper.get_by_role("button", name="Delete", exact=True)
        self.delete_cancel_button = self.modal_wrapper.get_by_role("button", name="Cancel", exact=True)

        # ---- Import / export / empty state ----
        self.import_heading = self.modal_wrapper.get_by_role("heading", name=re.compile("^Import Entities"))
        self.import_file_input = self.modal_wrapper.locator('input[type="file"]')
        self.import_next_button = self.modal_wrapper.get_by_role("button", name="Next", exact=True)
        self.import_template_link = self.modal_wrapper.get_by_text("Download Template", exact=True)
        self.export_button = page.locator('button:has(img[alt="Export as Excel"])')
        self.empty_state = page.get_by_text("No Entities Yet", exact=True)

        # ---- TP View / charts ----
        self.tp_expand_buttons = page.get_by_role("button", name="Expand related party details")
        self.tp_related_heading = self.modal_wrapper.get_by_text("Add More Related Parties", exact=True)
        self.tp_party_checkboxes = self.modal_wrapper.locator("input.reg-checkbox")
        self.chart_canvas = page.locator("canvas")
        self.chart_filters_button = page.get_by_role("button", name="Filters", exact=True)
        self.chart_properties_button = page.get_by_role("button", name="Properties", exact=True)

    # ---- navigation -----------------------------------------------------
    def goto(self):
        """Waits for the real 'Add Entity' button before returning control
        (a bare `page.goto()` races this SPA's render - confirmed live)."""
        workspace_goto(self.page, WORKSPACE_ENTITIES_URL)
        wait_for_content(self.add_entity_button, timeout=30000)

    def goto_view(self, route: str):
        """`route` e.g. "information/chart", "transferpricing/data",
        "transferpricing/chart", "taxrisk/chart" - every one supports a
        direct deep link (confirmed live)."""
        workspace_goto(self.page, f"{ENTITIES_BASE}/{route}/")
        wait_for_content(self.panel_entity_information, timeout=30000)

    # ---- grid -----------------------------------------------------------
    def entity_row_count(self) -> int:
        return self.table_rows.count()

    def row(self, name: str):
        return self.table_rows.filter(has_text=name)

    def row_kebab(self, name: str):
        """The row's actions kebab - the icon button in its first cell."""
        return self.row(name).first.locator("td").first.locator(".reg-icon-button")

    def column_values(self, header: str) -> list:
        """Every visible row's cell under `header`, located by the header's
        own index rather than a hardcoded position."""
        return self.page.evaluate("""(h) => {
            const ths = [...document.querySelectorAll('table thead th')];
            const idx = ths.findIndex(th => th.innerText.trim() === h);
            if (idx < 0) return [];
            return [...document.querySelectorAll('table tbody tr')]
                .map(tr => (tr.children[idx]?.innerText || '').trim());
        }""", header)

    def entity_names(self) -> list:
        return self.column_values("Entity Name")

    def row_cells(self, name: str) -> dict:
        """{header: cell text} for the first row containing `name`."""
        return self.page.evaluate("""(name) => {
            const hs = [...document.querySelectorAll('table thead th')].map(th => th.innerText.trim());
            const tr = [...document.querySelectorAll('table tbody tr')].find(r => r.innerText.includes(name));
            if (!tr) return {};
            const out = {};
            hs.forEach((h, i) => { if (h) out[h] = (tr.children[i]?.innerText || '').trim(); });
            return out;
        }""", name)

    def sortable_header(self, column_name: str):
        return self.page.locator("th").filter(has_text=re.compile(r"^%s$" % re.escape(column_name)))

    def column_sort_state(self, column_name: str) -> str:
        """The real `aria-sort` attribute ("ascending"/"descending"/"none")."""
        return self.sortable_header(column_name).first.get_attribute("aria-sort") or ""

    def type_search(self, term: str):
        """The grid search filters on keystroke events, so `fill()` leaves
        the grid unfiltered (confirmed live: 22 rows stayed 22)."""
        self.search_input.press_sequentially(term, delay=40)

    # ---- wizard ---------------------------------------------------------
    def option(self, text: str):
        return self.options.filter(has_text=text).first

    def tax_characterization(self, name: str):
        return self.modal_wrapper.get_by_text(name, exact=True)

    def total_ownership(self) -> str:
        m = re.search(r"Total Ownership\s*([\d.]+%)", self.modal_wrapper.inner_text())
        return m.group(1) if m else ""

    def is_next_button_disabled(self) -> bool:
        """`disabled=""` (empty string, not absent) - so `is not None`."""
        return self.modal_next_button.get_attribute("disabled") is not None

    def wait_modal_closed(self, timeout: int = 20000) -> bool:
        try:
            self.modal_wrapper.first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        return self.modal_wrapper.count() == 0

    def wait_row(self, name: str, timeout: int = 20000) -> bool:
        return wait_for_content(self.row(name), timeout=timeout)

    def wait_row_gone(self, name: str, timeout: int = 15000) -> bool:
        try:
            self.row(name).first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        return self.row(name).count() == 0

    def wait_edit_loaded(self, timeout: int = 20000) -> bool:
        """The Edit wizard opens empty and is filled asynchronously
        (confirmed on Live, where fields were still blank right after the
        title appeared). Waits until the Name field actually has a value."""
        waited = 0
        while waited < timeout:
            if self.modal_name_input.count() and self.modal_name_input.input_value().strip():
                return True
            self.page.wait_for_timeout(250)
            waited += 250
        return False

    def wait_rows_settled(self, timeout: int = 20000) -> int:
        """After a create/delete the grid re-renders (briefly 0 rows on a
        slow environment). Returns the row count once it is non-zero and
        unchanged across two consecutive reads."""
        last, waited = -1, 0
        while waited < timeout:
            n = self.table_rows.count()
            if n > 0 and n == last:
                return n
            last = n
            self.page.wait_for_timeout(500)
            waited += 500
        return self.table_rows.count()

    def close_add_entity_modal(self):
        """Closes the wizard without creating anything. It has no Cancel
        button; Escape discards its data (confirmed live)."""
        try:
            if self.modal_cancel_button.count():
                self.modal_cancel_button.first.click()
                return
        except Exception:
            pass
        self.page.keyboard.press("Escape")

    def dismiss_any_modal(self):
        if self.modal_wrapper.count():
            self.page.keyboard.press("Escape")
            self.wait_modal_closed(5000)

    # ---- cleanup (teardown only - never part of a test's own steps) ------
    def delete_all_matching(self, prefix: str) -> int:
        """Deletes every entity whose row contains `prefix` (always a
        `WorkspaceQA_...` name this run created). Returns how many were
        deleted; never raises, so a `finally` block can rely on it."""
        deleted = 0
        try:
            self.dismiss_any_modal()
            self.goto()
            wait_for_content(self.table_rows, timeout=20000)
            for _ in range(6):
                if self.row(prefix).count() == 0:
                    break
                self.row_kebab(prefix).click()
                self.menu_delete.first.click()
                self.delete_confirm_button.click()
                self.wait_modal_closed(15000)
                self.wait_row_gone(prefix, 5000) if self.row(prefix).count() == 1 else self.page.wait_for_timeout(800)
                deleted += 1
        except Exception:
            pass
        return deleted
