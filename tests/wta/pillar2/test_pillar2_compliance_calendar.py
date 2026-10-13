"""Pillar 2 > Compliance Calendar (/wta/ComplianceCalendar).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: jurisdiction list only (no categories).
  - Selecting a single jurisdiction alone (no category needed) renders a
    'Showing compliance calendar of <Country>' table with 5 fixed deadline
    rows: GIR Filing Deadline, Notification Deadline, Registration
    Deadline, Top-Up Tax Payment Deadline, Top-Up Tax Return Filing
    Deadline."""
import pytest

from pages.pillar2_compliance_calendar_page import ComplianceCalendarPage, DEADLINE_TYPES
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 ComplianceCalendar"


def _login_and_open(case, page):
    perform_login(case, page)
    cal = ComplianceCalendarPage(page)
    case.action("Navigating to /wta/ComplianceCalendar", kind="navigate")
    cal.goto()
    return cal


@pytest.mark.smoke
def test_p2cal_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "P2Cal_01", FEATURE, "Compliance Calendar loads with the jurisdiction placeholder",
        description="The page must load showing 'Select Jurisdiction' and the left panel instruction text.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Compliance Calendar\n2. Verify the placeholder text is visible",
    )
    cal = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(cal.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok,
               locator=cal.placeholder_text)

    actual = ("Compliance Calendar loaded with the jurisdiction placeholder visible." if ok else
              "Compliance Calendar did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2cal_02_selecting_jurisdiction_renders_table(page, result):
    case = Case(
        page, "P2Cal_02", FEATURE, "Selecting a jurisdiction alone renders the deadline table",
        description="Checking 'Australia' (no category needed here) must render a "
                     "'Showing compliance calendar of Australia' table.",
        precondition="User is logged in and on Compliance Calendar.",
        test_data="Country: Australia",
        steps="1. Log in and open Compliance Calendar\n2. Check 'Australia'\n"
              "3. Verify the 'Showing compliance calendar of' text and a table are visible",
    )
    cal = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(cal.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(cal.showing_text)

    case.step(3, "Verify the calendar table rendered")
    showing_ok = case.verify_visible(cal.showing_text, "'Showing compliance calendar of' text")
    table_ok = cal.table.count() >= 1
    ok = showing_ok and table_ok
    case.check("Compliance calendar content and table are visible for Australia", ok,
               expected="text + table visible", actual=f"text={showing_ok}, table_count={cal.table.count()}",
               locator=cal.showing_text)

    actual = ("Selecting Australia rendered the compliance calendar table." if ok else
              f"Selecting a jurisdiction did not render the expected table (text={showing_ok}, "
              f"table_count={cal.table.count()}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2cal_03_table_has_expected_deadline_rows(page, result):
    case = Case(
        page, "P2Cal_03", FEATURE, "The deadline table lists all 5 known deadline types",
        description="For Australia the table must include GIR Filing Deadline, Notification Deadline, "
                     "Registration Deadline, Top-Up Tax Payment Deadline and Top-Up Tax Return Filing "
                     "Deadline.",
        precondition="User is logged in, Australia selected on Compliance Calendar.",
        test_data="Country: Australia",
        steps="1. Log in, open Compliance Calendar, select Australia\n"
              "2. Verify each of the 5 deadline type rows is present",
    )
    cal = _login_and_open(case, page)
    cal.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(cal.showing_text)

    case.step(2, "Verify each deadline type row")
    missing = [d for d in DEADLINE_TYPES if not case.verify_visible(page.get_by_text(d, exact=True), f"'{d}' row")]
    ok = not missing
    case.check("All 5 deadline type rows are present", ok, expected="all 5 present",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("The compliance calendar table for Australia listed all 5 expected deadline types." if ok else
              f"Missing deadline rows: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2cal_04_switching_jurisdiction_updates_table(page, result):
    case = Case(
        page, "P2Cal_04", FEATURE, "Switching the selected jurisdiction updates the calendar",
        description="Unchecking Australia and checking Japan instead must update the 'Showing compliance "
                     "calendar of' text to reference Japan.",
        precondition="User is logged in, Australia selected on Compliance Calendar.",
        test_data="Countries: Australia -> Japan",
        steps="1. Log in, open Compliance Calendar, select Australia\n2. Uncheck Australia, check Japan\n"
              "3. Verify the heading now references Japan",
    )
    cal = _login_and_open(case, page)
    cal.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(cal.showing_text)

    case.step(2, "Switch selection from Australia to Japan")
    case.click(cal.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox (uncheck)")
    page.wait_for_timeout(300)
    case.click(cal.jurisdiction.country_checkbox("Japan"), "'Japan' checkbox")
    wait_for_content(cal.showing_text)
    page.wait_for_timeout(500)

    case.step(3, "Verify the calendar now shows Japan")
    ok = case.verify_visible(page.get_by_text("Japan", exact=True).first, "'Japan' in the content header")
    case.check("Calendar content updates to reference Japan after switching jurisdiction", ok,
               expected="Japan referenced", actual=ok)

    actual = ("Switching from Australia to Japan updated the compliance calendar to reference Japan." if ok
              else "Switching jurisdictions did not update the calendar content as expected.")
    result(case, actual, ok)
    assert ok, actual
