"""Workspace > Calendar (`/companydata/calendar/`). See
pages/workspace/workspace_calendar_page.py for the full confirmed-live
layout: the Agenda/Calendar toggle, Filters panel, Event Types chips, and
the Create New Event modal (opened/validated, never submitted, per this
project's production-safety rule)."""
import re

import pytest

from pages.workspace.workspace_calendar_page import WorkspaceCalendarPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "Workspace Calendar"


def _login_and_open(case, page):
    perform_login(case, page)
    calendar = WorkspaceCalendarPage(page)
    case.action("Navigating to Workspace > Calendar", kind="navigate")
    calendar.goto()
    return calendar


@pytest.mark.smoke
def test_workspacecalendar_01_page_loads_with_agenda_table(page, result):
    case = Case(
        page, "WorkspaceCalendar_01", FEATURE, "Calendar loads with the Agenda table",
        description="The Calendar page must load in its default 'Agenda' view with at least one real "
                     "compliance-deadline row.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Calendar\n2. Verify the Agenda table is visible with >0 rows",
    )
    calendar = _login_and_open(case, page)
    case.step(2, "Verify the Agenda table is visible with at least one row")
    heading_ok = case.verify_visible(calendar.view_title, "page view-title ('Agenda'/'Calendar')")
    table_ok = wait_for_content(calendar.table, timeout=20000)
    row_count = calendar.agenda_row_count() if table_ok else 0
    ok = heading_ok and table_ok and row_count > 0
    case.check("Agenda table loads with at least one real row", ok, expected="> 0 rows", actual=str(row_count))

    actual = f"Agenda table loaded with {row_count} row(s)." if ok else "Agenda table did not load with any rows."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_workspacecalendar_02_switching_to_calendar_view_renders_month_grid(page, result):
    case = Case(
        page, "WorkspaceCalendar_02", FEATURE, "Switching to 'Calendar' view renders a real month grid",
        description="Clicking the 'Calendar' side of the Agenda/Calendar toggle must render a month-grid "
                     "view (confirmed live via Sun-Sat weekday headers).",
        precondition="User is logged in and on Workspace > Calendar (Agenda view).",
        test_data="-",
        steps="1. Log in and open Workspace > Calendar\n2. Click the 'Calendar' toggle\n"
              "3. Verify a weekday header ('Sun') is visible",
    )
    calendar = _login_and_open(case, page)
    case.step(2, "Click the 'Calendar' side of the toggle")
    case.click(calendar.toggle_calendar, "'Calendar' view toggle")
    page.wait_for_timeout(500)

    case.step(3, "Verify a month-grid weekday header is visible")
    weekday_header = page.get_by_text("Sun", exact=True)
    ok = wait_for_content(weekday_header, timeout=10000)
    case.check("Month-grid view renders with weekday headers", ok, expected="'Sun' header visible", actual=ok)

    actual = "Switched to Calendar view and the month grid rendered." if ok else \
        "Calendar view did not render a month grid as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_workspacecalendar_03_create_new_event_opens_modal(page, result):
    case = Case(
        page, "WorkspaceCalendar_03", FEATURE, "'Create New Event' opens the event-creation modal",
        description="Clicking 'Create New Event' must open a modal with Select Country, Nature of "
                     "Compliance, Description and Due Date fields.",
        precondition="User is logged in and on Workspace > Calendar.",
        test_data="-",
        steps="1. Log in and open Workspace > Calendar\n2. Click 'Create New Event'\n"
              "3. Verify the modal and its fields are visible\n4. Close the modal via Cancel",
    )
    calendar = _login_and_open(case, page)
    case.step(2, "Click 'Create New Event'")
    case.click(calendar.create_event_button, "'Create New Event' button")

    case.step(3, "Verify the modal's fields are visible")
    heading_ok = wait_for_content(calendar.modal_heading, timeout=10000)
    title_ok = calendar.modal_title_input.is_visible()
    description_ok = calendar.modal_description_input.is_visible()
    ok = heading_ok and title_ok and description_ok
    case.check("Create New Event modal shows its required fields", ok,
               expected="modal + Title + Description fields visible",
               actual=f"heading={heading_ok}, title={title_ok}, description={description_ok}")

    case.step(4, "Close the modal without creating an event")
    calendar.close_create_event_modal()

    actual = "Create New Event modal opened with its fields, then closed without creating anything." if ok else \
        "Create New Event modal did not open as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacecalendar_04_save_with_empty_form_shows_validation_errors(page, result):
    case = Case(
        page, "WorkspaceCalendar_04", FEATURE, "Saving the event form empty shows real inline validation",
        description="Confirmed live: 'Save' is not disabled for an empty form - submitting empty instead "
                     "shows 'Country name is required', 'Title is required' and 'Due date is required'.",
        precondition="User is logged in and the Create New Event modal is open.",
        test_data="-",
        steps="1. Log in and open Workspace > Calendar\n2. Open 'Create New Event'\n"
              "3. Click 'Save' with the form empty\n4. Verify the 3 inline validation errors appear\n"
              "5. Close the modal via Cancel",
    )
    calendar = _login_and_open(case, page)
    case.step(2, "Open 'Create New Event'")
    case.click(calendar.create_event_button, "'Create New Event' button")
    wait_for_content(calendar.modal_heading, timeout=10000)

    case.step(3, "Click 'Save' with the form empty")
    case.click(calendar.modal_save_button, "'Save' button (empty form)")
    page.wait_for_timeout(500)

    case.step(4, "Verify the 3 inline validation errors appear")
    country_err = wait_for_content(calendar.modal_country_required_error, timeout=5000)
    title_err = calendar.modal_title_required_error.is_visible()
    date_err = calendar.modal_due_date_required_error.is_visible()
    ok = country_err and title_err and date_err
    case.check("Empty-form Save shows all 3 required-field validation errors", ok,
               expected="country + title + due-date errors all visible",
               actual=f"country={country_err}, title={title_err}, due_date={date_err}")

    case.step(5, "Close the modal without creating an event")
    calendar.close_create_event_modal()

    actual = "Empty-form Save correctly showed all 3 inline validation errors." if ok else \
        "Empty-form Save did not show the expected validation errors."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacecalendar_05_event_types_all_chip_shows_total_count(page, result):
    case = Case(
        page, "WorkspaceCalendar_05", FEATURE, "Event Types 'All' chip count matches the Agenda row count",
        description="The 'Event Types' filter's 'All(N)' chip count must match the number of real rows "
                     "shown in the unfiltered Agenda table.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Calendar\n2. Read the Agenda row count\n"
              "3. Read the 'All' chip's live count\n4. Verify they match",
    )
    calendar = _login_and_open(case, page)
    wait_for_content(calendar.table, timeout=20000)
    case.step(2, "Read the Agenda row count")
    row_count = calendar.agenda_row_count()

    case.step(3, "Read the 'Event Types' > 'All' chip's live count")
    all_chip = calendar.event_type_chip("All")
    chip_text = all_chip.first.inner_text() if all_chip.count() else ""
    m = re.search(r"\((\d+)\)", chip_text)
    chip_count = int(m.group(1)) if m else -1

    case.step(4, "Verify the Agenda row count matches the 'All' chip count")
    ok = chip_count == row_count
    case.check("'All' Event Types chip count matches the real Agenda row count", ok,
               expected=f"{row_count}", actual=f"{chip_count}")

    actual = f"'All' chip count ({chip_count}) matches the Agenda row count ({row_count})." if ok else \
        f"'All' chip count ({chip_count}) did not match the Agenda row count ({row_count})."
    result(case, actual, ok)
    assert ok, actual
