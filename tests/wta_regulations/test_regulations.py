"""World Tax Analyzer > Regulations (/wta/Regulations) - top-level module
(distinct from Pillar 2 > Regulation).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: jurisdiction list only (no categories), plus its own plain
    'Search' text box.
  - Selecting a jurisdiction alone renders a 'Showing regulations of
    <Country>' table (Title / Description / Entry into Force / Download /
    Project) with one or more 'English' download links and an 'Add to
    Project' button per row. For Australia there are multiple known rows
    (e.g. 'Section 102.15 of the ITAA 1997', 'Subdivision 815-C of ITAA
    1997', plus test data like 'TESTT')."""
import os

import pytest

from pages.regulations_page import RegulationsPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Regulations"


def _login_and_open(case, page):
    perform_login(case, page)
    regs = RegulationsPage(page)
    case.action("Navigating to /wta/Regulations", kind="navigate")
    regs.goto()
    return regs


@pytest.mark.smoke
def test_regs_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "Regs_01", FEATURE, "Regulations module loads with the jurisdiction placeholder",
        description="The page must load showing the left-panel instruction text and a 'Search' box.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Regulations\n2. Verify the placeholder text and Search box are visible",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Verify placeholder and search box")
    placeholder_ok = case.verify_visible(regs.placeholder_text, "left-panel instruction text")
    search_ok = case.verify_visible(regs.search_regulations, "'Search' box")
    ok = placeholder_ok and search_ok
    case.check("Placeholder and Search box are visible", ok, expected="both visible",
               actual=f"placeholder={placeholder_ok}, search={search_ok}")

    actual = ("Regulations loaded with the placeholder and Search box visible." if ok else
              "Regulations did not show the expected placeholder/search box.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_regs_02_selecting_jurisdiction_renders_table(page, result):
    case = Case(
        page, "Regs_02", FEATURE, "Selecting a jurisdiction renders the regulations table",
        description="Checking 'Australia' must render a 'Showing regulations of Australia' table with "
                     "multiple rows and an 'Entry into Force' column.",
        precondition="User is logged in and on Regulations.",
        test_data="Country: Australia",
        steps="1. Log in and open Regulations\n2. Check 'Australia'\n"
              "3. Verify the table, its column and at least one row are visible",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(regs.showing_text)

    case.step(3, "Verify table content")
    showing_ok = case.verify_visible(regs.showing_text, "'Showing regulations of' text")
    col_ok = case.verify_visible(regs.col_entry_into_force, "'Entry into Force' column header")
    row_count = regs.table.locator("tbody tr").count() if regs.table.count() else 0
    ok = showing_ok and col_ok and row_count >= 1
    case.check("Regulations table with rows and 'Entry into Force' column is visible", ok,
               expected="table with >=1 row",
               actual=f"showing={showing_ok}, column={col_ok}, row_count={row_count}")

    actual = (f"Selecting Australia rendered a regulations table with {row_count} row(s)." if ok else
              "The regulations table did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_regs_03_add_to_project_and_download_present(page, result):
    case = Case(
        page, "Regs_03", FEATURE, "Each regulation row has a Download link and an Add to Project button",
        description="For Australia, at least one row must show an 'English' download link and an "
                     "'Add to Project' button.",
        precondition="User is logged in, Australia selected on Regulations.",
        test_data="Country: Australia",
        steps="1. Log in, open Regulations, select Australia\n"
              "2. Verify an 'English' download link and an 'Add to Project' button are visible",
    )
    regs = _login_and_open(case, page)
    regs.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(regs.showing_text)

    case.step(2, "Verify download link and Add to Project button")
    download_ok = case.verify_visible(page.get_by_text("English", exact=True).first, "'English' download link")
    add_ok = case.verify_visible(regs.add_to_project_buttons.first, "'Add to Project' button")
    ok = download_ok and add_ok
    case.check("A download link and an 'Add to Project' button are present", ok,
               expected="both visible", actual=f"download={download_ok}, add_to_project={add_ok}")

    actual = ("Each regulation row exposed a download link and an 'Add to Project' action." if ok else
              "A regulation row was missing its download link or 'Add to Project' action.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_regs_04_search_box_accepts_input(page, result):
    case = Case(
        page, "Regs_04", FEATURE, "The Regulations Search box accepts free-text input",
        description="Typing into the page's own 'Search' box (distinct from 'Search countries') must "
                     "accept the text without error.",
        precondition="User is logged in and on Regulations.",
        test_data="Search term: capital gains",
        steps="1. Log in and open Regulations\n2. Type 'capital gains' into the Search box\n"
              "3. Verify the box holds the typed value",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Type into the Search box")
    case.fill(regs.search_regulations, "capital gains", "'Search' box")
    page.wait_for_timeout(400)

    case.step(3, "Verify the typed value is present")
    value = regs.search_regulations.input_value()
    ok = value == "capital gains"
    case.check("Search box holds the typed value", ok, expected="capital gains", actual=value,
               locator=regs.search_regulations)

    actual = (f"The Search box accepted and retained the typed value '{value}'." if ok else
              f"The Search box did not retain the typed value (got '{value}').")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_regs_05_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "Regs_05", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Clicking 'MEA' must hide 'Australia' (Asia Pacific) from the jurisdiction list.",
        precondition="User is logged in and on Regulations.",
        test_data="-",
        steps="1. Log in and open Regulations\n2. Click the 'MEA' region tab\n"
              "3. Verify 'Australia' is no longer listed",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Click the 'MEA' region tab")
    case.click(regs.jurisdiction.region_tab("MEA"), "'MEA' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify Australia is hidden")
    ok = not regs.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("'Australia' is not listed under 'MEA'", ok, expected="hidden", actual=not ok)

    actual = ("Switching to 'MEA' hid 'Australia' from the jurisdiction list." if ok else
              "Switching region tabs did not hide the out-of-region country as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_regs_06_download_link_triggers_real_file_download(page, result):
    case = Case(
        page, "Regs_06", FEATURE, "The 'English' download link triggers a real, non-empty file download",
        description="With Australia selected, clicking the first 'English' download link must trigger a real "
                     "download with no failure and a non-zero size - Regs_03 only proved the link is visible, "
                     "not that it actually downloads anything.",
        precondition="User is logged in, Australia selected on Regulations.",
        test_data="Country: Australia",
        steps="1. Log in and open Regulations\n2. Select Australia\n"
              "3. Click the first 'English' download link\n"
              "4. Verify a real, non-empty file download completed",
    )
    regs = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(regs.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(regs.showing_text)

    case.step(3, "Click the first 'English' download link")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(regs.download_links.first, "'English' download link")
    download = dl_info.value

    case.step(4, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and size > 0
    case.check("The 'English' download link produces a real, non-empty file with no failure", ok,
               expected="failure=None, size>0", actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The download link correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"The download link did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual
