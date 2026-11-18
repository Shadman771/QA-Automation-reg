"""Workspace > Calendar (`/companydata/calendar/`), default "Agenda" view.

Confirmed live via scratchpad discovery (HTML dumps, screenshots and a real
create/edit/delete of throwaway events on RC, not part of the suite): a
compliance-deadline calendar mixing system deadlines (CbC Report, CIT
Return, ...) with user-created "Custom Event"s.

**Views** - a `.reg-toggle-container` with "Agenda"/"Calendar" labels (an
unscoped `get_by_text("Calendar")` hits the sidebar link first). The page
title is a plain `<p>` that reads "Agenda" or "Calendar" with the active
view - not a `role=heading`. "Calendar" renders a toast-ui month grid whose
heading ("<Month> <Year>") sits between two unlabeled chevron `<svg>`s
(previous / next) and starts on the Date Range's first month.

**Agenda table** - columns: (expand), (kebab), Tax Residence, Nature of
Compliance, Description, Due Date, Applicable Form. Tax Residence, Nature
of Compliance and Due Date are sortable (`aria-sort` + `?sort=countryName|
title|dueDate:asc|desc`, default `dueDate:asc`). The search box filters on
keystrokes; a no-match search replaces the table with a "Stay on Top of
Compliance Deadlines" empty state.

**Filters** - Date Range (a rolling window, today-1 month .. today+3
months, with presets such as "This Year"), Filter By Entity (default, "All
Entity's Jurisdiction") or Jurisdiction, and Event Types chips whose names
carry live counts ("All(7)", "CbC Report (3)" - spacing is inconsistent).
Real behaviour worth knowing: under the default Entity filter only events
in jurisdictions where the account HAS AN ENTITY are listed, so a custom
event created for any other country is saved but invisible until Filter By
is switched to Jurisdiction. Tests therefore always create events in a
jurisdiction read from the live Agenda.

**Custom event CRUD** (all confirmed live):
  - "Create New Event" > Single Event: Select Country* (rsuite combobox),
    Nature of Compliance* (`name="Title"`), Description, Due Date* (a date
    picker - pick a `role="gridcell"` by its zero-padded `aria-label`
    "DD Mon YYYY", then OK; never type into it), External Link
    (`name="ApplicableForm"`, shown in the grid as an "E-File" link).
    Saving POSTs `api/EventCalendar/AddOrPopulateCustomEventCalendarData`.
  - `Save` is never disabled: an empty form shows "Country name is
    required", "Title is required", "Due date is required".
  - Only custom events have a row kebab (Edit / Delete); system deadlines
    have no row actions at all.
  - Edit opens "Edit Event" (same fields, pre-filled); Delete asks "Do you
    want to delete the event '<title>'? This action is irreversible."
    (Cancel / Delete).
  - Accepted without validation (documented behaviour): past due dates, a
    non-URL External Link, duplicate titles, long/special-character text.
  - **Application defect**: a whitespace-only Nature of Compliance passes
    the required check and is saved as an event with a blank title.
  - "Multiple Events" is an Excel upload with a "Replace the existing
    events with new events" option - automation only inspects it and
    never uploads (a bulk replace cannot be undone).

Automation only ever creates, edits and deletes events it named
`WorkspaceQA_<tag>_<timestamp>` itself."""
import datetime
import re

from playwright.sync_api import Page

from pages.workspace.workspace_common import WORKSPACE_CALENDAR_URL, workspace_goto
from utils.wait import wait_for_content

MONTH_RE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$")


def agenda_date(d: datetime.date) -> str:
    """The Agenda's Due Date format, e.g. "8 December 2026"."""
    return f"{d.day} {d.strftime('%B %Y')}"


class WorkspaceCalendarPage:
    def __init__(self, page: Page):
        self.page = page
        self.view_title = page.locator(".tax-top-bar p.text-18-semibold")
        self.heading = self.view_title
        self.create_event_button = page.get_by_role("button", name="Create New Event", exact=True).first
        self.search_input = page.locator('input[placeholder="Search"]').first
        self.empty_state = page.get_by_text("Stay on Top of Compliance Deadlines", exact=True)

        self.toggle_container = page.locator(".reg-toggle-container")
        self.toggle_agenda = self.toggle_container.get_by_text("Agenda", exact=True)
        self.toggle_calendar = self.toggle_container.get_by_text("Calendar", exact=True)

        # ---- filters ----
        self.filters_heading = page.get_by_text("Filters", exact=True)
        self.filters_collapse_button = page.locator("p:text-is('Filters') + button")
        self.date_range_label = page.get_by_text("Date Range", exact=True)
        self.date_range_input = page.locator("input[placeholder='From date - To date']")
        self.picker_popup = page.locator(".rs-picker-popup")
        self.filter_selector = page.locator(".filter-selector")
        self.filter_by_entity_radio = self.filter_selector.get_by_text("Entity", exact=True)
        self.filter_by_jurisdiction_radio = self.filter_selector.get_by_text("Jurisdiction", exact=True)
        self.filter_picker = self.filter_selector.locator("[role='combobox']")
        self.filter_selected_chips = self.filter_selector.locator(".reg-chip-button-filter")
        self.event_type_chips = page.locator("label:has-text('Event Types') + div button")

        # ---- agenda table ----
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.column_header = lambda name: page.locator("th").filter(has_text=name)

        # ---- month grid ----
        self.month_heading = page.locator("div.text-18-semibold").filter(has_text=MONTH_RE)
        # The chevrons are bare sibling <svg>s with no role/label (confirmed
        # via HTML dump), so they can only be reached relative to the heading.
        self.month_next = self.month_heading.locator("xpath=following-sibling::*[1]")
        self.month_prev = self.month_heading.locator("xpath=preceding-sibling::*[1]")
        self.weekday_sun = page.get_by_text("Sun", exact=True)
        self.grid_events = page.locator(".toastui-calendar-weekday-event-title")

        # ---- create / edit modal ----
        self.modal_wrapper = page.locator(".rs-modal-wrapper")
        self.modal_heading = page.get_by_role("heading", name="Create New Event", exact=True)
        self.modal_edit_heading = self.modal_wrapper.get_by_text("Edit Event", exact=True)
        self.modal_single_event_tab = page.get_by_text("Single Event", exact=True)
        self.modal_multiple_events_tab = page.get_by_text("Multiple Events", exact=True)
        self.modal_country_combo = self.modal_wrapper.locator("[role='combobox']").first
        self.options = page.locator("[role='option']")
        self.modal_title_input = page.locator('input[name="Title"]')
        self.modal_description_input = page.locator('input[name="Description"]')
        self.modal_due_date_input = self.modal_wrapper.locator('input[placeholder="Due Date"]')
        self.modal_external_link_input = page.locator('input[name="ApplicableForm"]')
        self.modal_save_button = page.get_by_role("button", name="Save", exact=True)
        self.modal_cancel_button = page.get_by_role("button", name="Cancel", exact=True)
        self.modal_country_required_error = page.get_by_text("Country name is required", exact=True)
        self.modal_title_required_error = page.get_by_text("Title is required", exact=True)
        self.modal_due_date_required_error = page.get_by_text("Due date is required", exact=True)
        self.date_ok_button = self.picker_popup.get_by_role("button", name="OK", exact=True)
        self.date_next_month = page.get_by_role("button", name="Next month")
        self.date_prev_month = page.get_by_role("button", name="Previous month")

        # ---- multiple events tab ----
        self.multi_upload_label = self.modal_wrapper.get_by_text("Upload Excel File", exact=True)
        self.multi_replace_label = self.modal_wrapper.get_by_text("Replace the existing events with new events", exact=True)
        self.multi_replace_checkbox = self.modal_wrapper.locator('input[type="checkbox"]')
        self.multi_template_link = self.modal_wrapper.get_by_text("Download Template", exact=True)
        self.multi_add_button = self.modal_wrapper.get_by_role("button", name="Add", exact=True)

        # ---- row actions / delete confirm ----
        self.menu_edit = page.get_by_text("Edit", exact=True)
        self.menu_delete = page.get_by_text("Delete", exact=True)
        self.delete_dialog_text = self.modal_wrapper.get_by_text(re.compile(r"Do you want to delete the event"))
        self.delete_confirm_button = self.modal_wrapper.get_by_role("button", name="Delete", exact=True)
        self.delete_cancel_button = self.modal_wrapper.get_by_role("button", name="Cancel", exact=True)

    # ---- navigation -----------------------------------------------------
    def goto(self):
        """Waits for the real "Create New Event" button (a bare
        `page.goto()` races this SPA's render - confirmed live)."""
        workspace_goto(self.page, WORKSPACE_CALENDAR_URL)
        wait_for_content(self.create_event_button, timeout=30000)

    def switch_to_calendar_view(self):
        self.toggle_calendar.click()

    def switch_to_agenda_view(self):
        self.toggle_agenda.click()

    # ---- agenda ---------------------------------------------------------
    def agenda_row_count(self) -> int:
        return self.table_rows.count()

    def row(self, text: str):
        return self.table_rows.filter(has_text=text)

    def row_kebab(self, text: str):
        """Custom events only: the icon button in the row's 2nd cell (the
        1st is the expand chevron). System deadlines have an empty 2nd cell."""
        return self.row(text).first.locator("td").nth(1).locator(".reg-icon-button")

    def column_values(self, header: str) -> list:
        return self.page.evaluate("""(h) => {
            const ths = [...document.querySelectorAll('table thead th')];
            const idx = ths.findIndex(th => th.innerText.trim() === h);
            if (idx < 0) return [];
            return [...document.querySelectorAll('table tbody tr')]
                .map(tr => (tr.children[idx]?.innerText || '').trim());
        }""", header)

    def row_cells(self, text: str) -> dict:
        return self.page.evaluate("""(text) => {
            const hs = [...document.querySelectorAll('table thead th')].map(th => th.innerText.trim());
            const tr = [...document.querySelectorAll('table tbody tr')].find(r => r.innerText.includes(text));
            if (!tr) return {};
            const out = {};
            hs.forEach((h, i) => { if (h) out[h] = (tr.children[i]?.innerText || '').trim(); });
            return out;
        }""", text)

    def rows_with_kebab(self) -> int:
        return self.page.locator("table tbody tr td:nth-child(2) .reg-icon-button").count()

    def sortable_header(self, column_name: str):
        return self.page.locator("th").filter(has_text=re.compile(r"^%s$" % re.escape(column_name)))

    def column_sort_state(self, column_name: str) -> str:
        return self.sortable_header(column_name).first.get_attribute("aria-sort") or ""

    def type_search(self, term: str):
        self.search_input.press_sequentially(term, delay=40)

    def wait_row(self, text: str, timeout: int = 20000) -> bool:
        return wait_for_content(self.row(text), timeout=timeout)

    def wait_row_gone(self, text: str, timeout: int = 15000) -> bool:
        try:
            self.row(text).first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        return self.row(text).count() == 0

    # ---- chips / filters --------------------------------------------------
    def event_type_chip(self, label: str):
        """Matches regardless of the live count suffix. The parenthesized
        count is mandatory in the regex - a looser version matched the
        unrelated "All Entity's Jurisdiction" chip."""
        return self.page.get_by_text(re.compile(rf"^{re.escape(label)}\s*\(\d+\)"))

    def chip_counts(self) -> dict:
        """{"All": 7, "CbC Report": 3, ...} parsed from the live chips."""
        out = {}
        for t in self.event_type_chips.all_inner_texts():
            m = re.match(r"^(.*?)\s*\((\d+)\)\s*$", t.strip().replace("\n", ""))
            if m:
                out[m.group(1).strip()] = int(m.group(2))
        return out

    def chip_button(self, label: str):
        return self.event_type_chips.filter(has_text=re.compile(rf"^{re.escape(label)}\s*\(\d+\)"))

    def picker_option(self, text: str):
        return self.picker_popup.get_by_text(text, exact=True)

    def date_preset(self, name: str):
        return self.picker_popup.get_by_role("button", name=name, exact=True)

    # ---- modal helpers ----------------------------------------------------
    def option(self, text: str):
        return self.options.filter(has_text=text).first

    def date_cell(self, d: datetime.date):
        """Calendar day cell by its zero-padded aria-label "DD Mon YYYY"."""
        return self.page.locator("[role='gridcell'][aria-label='%s']" % d.strftime("%d %b %Y"))

    def date_cell_in_month(self, d: datetime.date) -> bool:
        cell = self.date_cell(d)
        return cell.count() > 0 and "un-same-month" not in (cell.first.get_attribute("class") or "")

    def wait_modal_closed(self, timeout: int = 20000) -> bool:
        try:
            self.modal_wrapper.first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        return self.modal_wrapper.count() == 0

    def close_create_event_modal(self):
        try:
            if self.modal_cancel_button.count():
                self.modal_cancel_button.first.click()
                return
        except Exception:
            pass
        self.page.keyboard.press("Escape")

    def grid_event(self, title: str):
        return self.grid_events.filter(has_text=title)

    # ---- cleanup (teardown only - never part of a test's own steps) ------
    def delete_all_matching(self, tag: str) -> int:
        """Deletes every custom event whose row contains `tag` (always a
        `WorkspaceQA_...` value this run wrote into the title and/or the
        description). Switches Filter By to Jurisdiction first so events in
        ANY country are listed. Returns how many were deleted; never raises."""
        deleted = 0
        try:
            if self.modal_wrapper.count():
                self.close_create_event_modal()
                self.wait_modal_closed(5000)
            self.goto()
            self.filter_by_jurisdiction_radio.click()
            self.page.wait_for_timeout(1500)
            wait_for_content(self.table_rows, timeout=15000)
            for _ in range(8):
                if self.row(tag).count() == 0:
                    break
                self.row_kebab(tag).click()
                self.menu_delete.first.click()
                self.delete_confirm_button.click()
                self.wait_modal_closed(15000)
                self.page.wait_for_timeout(1200)
                deleted += 1
        except Exception:
            pass
        return deleted
