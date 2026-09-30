"""Pillar 2 > Regulation (/wta/PillarTwoRegulation).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: jurisdiction list only (no categories), plus its own plain
    'Search' text box.
  - Selecting a jurisdiction alone renders a 'Showing regulations of
    <Country>' table (Title / Description / Entry into Force / Download /
    Project) with an 'Add to Project' button per row. For Australia there
    is 1 known row (Section 102.15 of the ITAA 1997)."""
import os

import pytest

from pages.pillar2_regulation_page import PillarTwoRegulationPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 Regulation"


def _login_and_open(case, page):
    perform_login(case, page)
    reg = PillarTwoRegulationPage(page)
    case.action("Navigating to /wta/PillarTwoRegulation", kind="navigate")
    reg.goto()
    return reg


@pytest.mark.smoke
def test_p2reg_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "P2Reg_01", FEATURE, "Pillar 2 > Regulation loads with the jurisdiction placeholder",
        description="The page must load showing the left-panel instruction text and a 'Search' box.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Regulation\n2. Verify the placeholder text and Search box are visible",
    )
    reg = _login_and_open(case, page)
    case.step(2, "Verify placeholder and search box")
    placeholder_ok = case.verify_visible(reg.placeholder_text, "left-panel instruction text")
    search_ok = case.verify_visible(reg.search_regulations, "'Search' box")
    ok = placeholder_ok and search_ok
    case.check("Placeholder and Search box are visible", ok, expected="both visible",
               actual=f"placeholder={placeholder_ok}, search={search_ok}")

    actual = ("Pillar 2 > Regulation loaded with the placeholder and Search box visible." if ok else
              "Pillar 2 > Regulation did not show the expected placeholder/search box.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2reg_02_selecting_jurisdiction_renders_regulations_table(page, result):
    case = Case(
        page, "P2Reg_02", FEATURE, "Selecting a jurisdiction renders the regulations table",
        description="Checking 'Australia' must render a 'Showing regulations of Australia' table with an "
                     "'Entry into Force' column.",
        precondition="User is logged in and on Pillar 2 > Regulation.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > Regulation\n2. Check 'Australia'\n"
              "3. Verify the regulations table and its 'Entry into Force' column are visible",
    )
    reg = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(reg.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(reg.showing_text)

    case.step(3, "Verify table content")
    showing_ok = case.verify_visible(reg.showing_text, "'Showing regulations of' text")
    col_ok = case.verify_visible(reg.col_entry_into_force, "'Entry into Force' column header")
    ok = showing_ok and col_ok
    case.check("Regulations table with 'Entry into Force' column is visible", ok, expected="both visible",
               actual=f"showing={showing_ok}, column={col_ok}")

    actual = ("Selecting Australia rendered the regulations table with the expected columns." if ok else
              "The regulations table did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2reg_03_add_to_project_button_present(page, result):
    case = Case(
        page, "P2Reg_03", FEATURE, "Each regulation row has an Add to Project button",
        description="For Australia, at least one regulation row must show an 'Add to Project' button.",
        precondition="User is logged in, Australia selected on Pillar 2 > Regulation.",
        test_data="Country: Australia",
        steps="1. Log in, open Pillar 2 > Regulation, select Australia\n"
              "2. Verify an 'Add to Project' button is visible",
    )
    reg = _login_and_open(case, page)
    reg.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(reg.showing_text)

    case.step(2, "Verify Add to Project button")
    ok = case.verify_visible(reg.add_to_project_buttons.first, "'Add to Project' button")
    case.check("An 'Add to Project' button is present on a regulation row", ok, expected="visible", actual=ok,
               locator=reg.add_to_project_buttons.first)

    actual = ("Each regulation row exposed an 'Add to Project' action." if ok else
              "A regulation row was missing its 'Add to Project' action.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2reg_04_search_box_accepts_input(page, result):
    case = Case(
        page, "P2Reg_04", FEATURE, "The regulations Search box accepts free-text input",
        description="Typing into the page's 'Search' box (distinct from 'Search countries') must accept "
                     "the text without error.",
        precondition="User is logged in and on Pillar 2 > Regulation.",
        test_data="Search term: capital",
        steps="1. Log in and open Pillar 2 > Regulation\n2. Type 'capital' into the Search box\n"
              "3. Verify the box holds the typed value",
    )
    reg = _login_and_open(case, page)
    case.step(2, "Type into the Search box")
    case.fill(reg.search_regulations, "capital", "'Search' box")
    page.wait_for_timeout(400)

    case.step(3, "Verify the typed value is present")
    value = reg.search_regulations.input_value()
    ok = value == "capital"
    case.check("Search box holds the typed value", ok, expected="capital", actual=value,
               locator=reg.search_regulations)

    actual = (f"The Search box accepted and retained the typed value '{value}'." if ok else
              f"The Search box did not retain the typed value (got '{value}').")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2reg_05_download_link_triggers_real_file_download(page, result):
    case = Case(
        page, "P2Reg_05", FEATURE, "The 'Download' column's link triggers a real, non-empty file download",
        description="With Australia selected, clicking the regulation row's 'English' download link must "
                     "trigger a real download with no failure and a non-zero size - this module previously had "
                     "no download coverage at all, only the 'Download' column heading was referenced in a docstring.",
        precondition="User is logged in, Australia selected on Pillar 2 > Regulation.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > Regulation\n2. Select Australia\n"
              "3. Click the 'English' download link\n"
              "4. Verify a real, non-empty file download completed",
    )
    reg = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(reg.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(reg.showing_text)

    case.step(3, "Click the 'English' download link")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(reg.download_links.first, "'English' download link")
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
