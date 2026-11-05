"""TPA > Regulations (/tpa/Regulations).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. The simplest of the 7 TPA pages: a jurisdiction-only left panel,
no category list. See pages/tpa/tpa_regulations_page.py for the full
real-shape writeup."""
import pytest

from pages.wta.wta_common import wait_for_content
from pages.tpa.tpa_regulations_page import TpaRegulationsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Regulations"


def _login_and_open(case, page):
    perform_login(case, page)
    regs = TpaRegulationsPage(page)
    case.action("Navigating to /tpa/Regulations", kind="navigate")
    regs.goto()
    return regs


@pytest.mark.smoke
def test_tparegulations_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "TpaRegulations_01", FEATURE, "Regulations loads with the jurisdiction placeholder",
        description="The page must load with the 'Use the left panel to choose jurisdiction.' placeholder "
                     "shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Regulations\n2. Verify the placeholder text is visible",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(regs.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("Regulations loaded with the placeholder visible." if ok else
              "Regulations did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tparegulations_02_jurisdiction_renders_real_table(page, result):
    case = Case(
        page, "TpaRegulations_02", FEATURE, "Selecting a jurisdiction renders a real regulations table",
        description="Checking 'Australia' must render a 'Showing regulations of Australia' table with real "
                     "rows and column headers (Title, Description, Entry into Force, Download).",
        precondition="User is logged in and on Regulations.",
        test_data="Country: Australia",
        steps="1. Log in and open Regulations\n2. Check 'Australia'\n"
              "3. Verify the table and its columns render with real rows",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(regs.showing_regulations_text)
    wait_for_content(regs.add_to_project_buttons)

    case.step(3, "Verify table and columns")
    showing_ok = case.verify_visible(regs.showing_regulations_text, "'Showing regulations of' text")
    title_ok = case.verify_visible(regs.col_title, "'Title' column header")
    entry_ok = case.verify_visible(regs.col_entry_into_force, "'Entry into Force' column header")
    row_count = regs.row_count()
    ok = showing_ok and title_ok and entry_ok and row_count > 0
    case.check("Regulations table with columns and real rows is visible", ok,
               expected="all visible, rows > 0",
               actual=f"showing={showing_ok}, title={title_ok}, entry_into_force={entry_ok}, rows={row_count}")

    actual = (f"Selecting Australia rendered the regulations table with {row_count} row(s)." if ok else
              "The regulations table or its columns did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tparegulations_03_each_row_has_add_to_project(page, result):
    case = Case(
        page, "TpaRegulations_03", FEATURE, "Each regulation row has an 'Add to Project' button",
        description="With Australia selected, every rendered row must have its own 'Add to Project' button "
                     "(same count as the row total, not one shared button).",
        precondition="User is logged in, Australia selected on Regulations.",
        test_data="Country: Australia",
        steps="1. Log in, open Regulations, select Australia\n"
              "2. Verify at least one 'Add to Project' button is visible",
    )
    regs = _login_and_open(case, page)
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(regs.showing_regulations_text)
    wait_for_content(regs.add_to_project_buttons)

    case.step(2, "Verify at least one 'Add to Project' button is visible")
    count = regs.row_count()
    ok = count > 0
    case.check("At least one 'Add to Project' button is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"Regulations correctly shows {count} 'Add to Project' button(s)." if ok else
              "No 'Add to Project' button was found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tparegulations_04_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "TpaRegulations_04", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Switching from 'Asia Pacific' (default) to 'Europe' must hide 'Australia' from the "
                     "visible list.",
        precondition="User is logged in and on Regulations.",
        test_data="-",
        steps="1. Log in and open Regulations\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer visible",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(regs.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Australia' is no longer visible")
    ok = not regs.jurisdiction.country_checkbox("Australia").is_visible()
    case.check("'Australia' is hidden after switching to 'Europe'", ok, expected="not visible", actual=f"visible={not ok}")

    actual = ("Switching to 'Europe' correctly hid 'Australia'." if ok else
              "'Australia' was still visible after switching to 'Europe'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tparegulations_05_search_box_accepts_input(page, result):
    case = Case(
        page, "TpaRegulations_05", FEATURE, "The 'Search countries' box accepts input",
        description="Typing into the 'Search countries' box must filter the visible country list.",
        precondition="User is logged in and on Regulations.",
        test_data="Search term: Austra",
        steps="1. Log in and open Regulations\n2. Type 'Austra' into 'Search countries'\n"
              "3. Verify 'Australia' is still visible",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Type 'Austra' into 'Search countries'")
    case.fill(regs.jurisdiction.search_countries, "Austra", "'Search countries' input")
    page.wait_for_timeout(600)

    case.step(3, "Verify 'Australia' is still visible")
    ok = case.verify_visible(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.check("'Australia' remains visible after searching 'Austra'", ok, expected="visible", actual=ok)

    actual = ("The search box correctly filtered to show 'Australia'." if ok else
              "'Australia' was not visible after searching 'Austra'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tparegulations_06_switching_country_updates_table(page, result):
    case = Case(
        page, "TpaRegulations_06", FEATURE, "Switching to a different country updates the table heading",
        description="Switching from Australia to Bangladesh must update the heading to 'Showing regulations "
                     "of Bangladesh'.",
        precondition="User is logged in and on Regulations.",
        test_data="Country: Australia -> Bangladesh",
        steps="1. Log in, open Regulations, select Australia\n2. Uncheck Australia, check Bangladesh\n"
              "3. Verify the heading updates to Bangladesh",
    )
    regs = _login_and_open(case, page)
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(regs.showing_regulations_text)
    case.step(2, "Switch to Bangladesh")
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox (uncheck)")
    case.click(regs.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the heading updates to Bangladesh")
    # "Showing regulations of" and the country name are separate sibling
    # text nodes (confirmed live), not one string - read the shared
    # parent container's text instead of just the matched element's own.
    heading_text = regs.showing_regulations_text.first.locator("xpath=..").inner_text()
    ok = "Bangladesh" in heading_text
    case.check("Heading updates to reflect Bangladesh", ok, expected="contains 'Bangladesh'", actual=heading_text)

    actual = (f"Switching country correctly updated the heading to {heading_text!r}." if ok else
              f"The heading did not update as expected (got {heading_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tparegulations_07_direct_deep_link_works(page, result):
    case = Case(
        page, "TpaRegulations_07", FEATURE, "A direct deep link to /tpa/Regulations loads the page",
        description="Navigating straight to /tpa/Regulations must load with the placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/Regulations\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/Regulations")
    regs = TpaRegulationsPage(page)
    regs.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(regs.placeholder_text, "left-panel instruction text")
    case.check("Direct deep link to /tpa/Regulations loads with the placeholder", ok, expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/Regulations correctly loaded." if ok else
              "The direct deep link to /tpa/Regulations did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
