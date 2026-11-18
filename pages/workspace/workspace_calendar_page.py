"""Workspace > Calendar (`/companydata/calendar/`), default "Agenda" view.

Confirmed live via scratchpad discovery (full HTML dump + a rendered
screenshot, not part of the suite): a real compliance-deadline calendar,
not a generic event calendar.

**Agenda/Calendar toggle** - a real `<div class="reg-toggle-container">`
holding two `<span class="reg-toggle-text">` labels ("Agenda"/"Calendar")
plus a sliding `<div class="reg-toggle-button">` indicator (its own text
content mirrors whichever side is active). **Real gotcha confirmed live**:
an unscoped `get_by_text("Calendar", exact=True)` matches the LEFT SIDEBAR
nav link first (same ambiguous-text family as every other rsuite-ish
control in this project) - the toggle's own labels must be scoped inside
`.reg-toggle-container`. Switching to "Calendar" renders a genuine
month-grid (confirmed live via screenshot: Sun-Sat weekday headers, a
"<Month> <Year>" heading with prev/next chevrons, and real compliance-
deadline markers on their due-date cells) - not a fake/disabled toggle.

**Filters panel** - "Date Range" (defaults live to a ~4-month forward
window, e.g. "18-Oct-2026 to 18-Feb-2027" - a rolling window relative to
today, not a fixed literal date, same "don't hardcode a date" lesson as
WTA/TPA's own rolling-window news pages), "Filter By" Entity/Jurisdiction
(radio pair, Entity selected by default), and "Event Types" - the same
`reg-chip-button-choice`-style chips-with-live-counts pattern as
Dashboard's risk chips ("All(N)", "CbC Report (N)", "Custom Event (N)",
"CIT Return (N)").

**"Create New Event"** opens a real modal (Single Event/Multiple Events
tabs) with Select Country* (an rsuite combobox), Nature of Compliance*
(`name="Title"`), Description (`name="Description"`), Due Date*
(`name="StartDateTime"`, a masked date picker - same "never type into a
masked date field, it can crash the app" gotcha already documented for
WTA's Interest and Penalties calculator, so automation never types into
this field), External Link (`name="ApplicableForm"`). **Real, live-
confirmed validation**: `Save` is NOT disabled for an empty form -
submitting empty instead shows 3 real inline errors ("Country name is
required", "Title is required", "Due date is required") and keeps the
modal open, the same "validate on submit, not via a disabled button"
pattern as TPA Analyzer's "Create Analysis" modal. Automation only opens/
validates/cancels this modal - it never actually creates a new compliance
event in this shared, real account (same production-safety judgment as
the Entities "Add Entity" wizard)."""
import re

from playwright.sync_api import Page

from pages.workspace.workspace_common import WORKSPACE_CALENDAR_URL, workspace_goto
from utils.wait import wait_for_content


class WorkspaceCalendarPage:
    def __init__(self, page: Page):
        self.page = page
        # Real gotcha confirmed live (caught by a real test run, not just
        # discovery): the page's own title area is a plain `<p
        # class="...text-18-semibold...">` reading "Agenda" or "Calendar"
        # depending on the CURRENTLY ACTIVE view - it is NOT a static
        # `role=heading` element, so `get_by_role("heading", name=
        # "Calendar")` never matches and silently burns the full
        # ASSERTION_TIMEOUT_MS. `view_title` is the real, always-present
        # signal; `heading` is kept as an alias so callers that just want
        # "the page genuinely loaded" (regardless of which view) have one.
        self.view_title = page.locator(".tax-top-bar p.text-18-semibold")
        self.heading = self.view_title
        self.create_event_button = page.get_by_role("button", name="Create New Event", exact=True)

        self.toggle_container = page.locator(".reg-toggle-container")
        self.toggle_agenda = self.toggle_container.get_by_text("Agenda", exact=True)
        self.toggle_calendar = self.toggle_container.get_by_text("Calendar", exact=True)

        self.filters_heading = page.get_by_text("Filters", exact=True)
        self.date_range_label = page.get_by_text("Date Range", exact=True)
        self.filter_by_entity_radio = page.get_by_text("Entity", exact=True).first
        self.filter_by_jurisdiction_radio = page.get_by_text("Jurisdiction", exact=True).first

        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.column_header = lambda name: page.locator("th").filter(has_text=name)

        # Create New Event modal
        self.modal_heading = page.get_by_role("heading", name="Create New Event", exact=True)
        self.modal_single_event_tab = page.get_by_text("Single Event", exact=True)
        self.modal_multiple_events_tab = page.get_by_text("Multiple Events", exact=True)
        self.modal_title_input = page.locator('input[name="Title"]')
        self.modal_description_input = page.locator('input[name="Description"]')
        self.modal_external_link_input = page.locator('input[name="ApplicableForm"]')
        self.modal_save_button = page.get_by_role("button", name="Save", exact=True)
        self.modal_cancel_button = page.get_by_role("button", name="Cancel", exact=True)
        self.modal_country_required_error = page.get_by_text("Country name is required", exact=True)
        self.modal_title_required_error = page.get_by_text("Title is required", exact=True)
        self.modal_due_date_required_error = page.get_by_text("Due date is required", exact=True)

    def goto(self):
        """Confirmed live (a real test run, not just discovery): a bare
        `page.goto()` with no ready-wait races this SPA's render -
        `create_event_button`/the Agenda table can both still be absent
        moments after `domcontentloaded` fires, leading to a 60s
        actionability timeout on the very next click/assert. Waits for the
        real "Create New Event" button (present in both Agenda and
        Calendar view) before returning control, the same
        `goto_and_wait_ready` discipline every other page object in this
        project follows."""
        workspace_goto(self.page, WORKSPACE_CALENDAR_URL)
        wait_for_content(self.create_event_button, timeout=30000)

    def switch_to_calendar_view(self):
        self.toggle_calendar.click()

    def switch_to_agenda_view(self):
        self.toggle_agenda.click()

    def event_type_chip(self, label: str):
        """`label` e.g. "All"/"CbC Report"/"Custom Event"/"CIT Return" -
        matches regardless of the live count suffix, same pattern as
        WorkspaceDashboardPage.risk_chip(). **Real gotcha confirmed live**:
        the required `\\(\\d+\\)` suffix must NOT be optional - an earlier,
        looser version of this regex (every group optional) matched the
        unrelated "All Entity's Jurisdiction" filter-chip text, since both
        start with "All". The chip's spacing is also inconsistent live
        ("All(7)" has no space, "CbC Report (3)" does), so `\\s*` stays
        optional while the parenthesized count stays mandatory."""
        return self.page.get_by_text(re.compile(rf"^{re.escape(label)}\s*\(\d+\)"))

    def agenda_row_count(self) -> int:
        return self.table_rows.count()

    def close_create_event_modal(self):
        try:
            if self.modal_cancel_button.count():
                self.modal_cancel_button.first.click()
                return
        except Exception:
            pass
        self.page.keyboard.press("Escape")
