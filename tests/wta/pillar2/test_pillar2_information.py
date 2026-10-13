"""Pillar 2 > Information (/wta/PillarTwoInformation).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: jurisdiction list plus a FLAT list of 9 GMT categories
    (Scope of GMT, IIR, UTPR, QDMTT, Safe Harbours under GloBE Rule,
    Filing obligations of GMT, Penalties under GMT, Payment obligations of
    GMT, Qualified Refundable Tax Credits under GMT) - no nested tree,
    unlike the main Information page.
  - The right panel shows the 'Select Jurisdictions and Categories'
    placeholder until BOTH a jurisdiction and a category are selected;
    once both are picked it renders a 'Showing information of <Country>'
    content header."""
import pytest

from pages.pillar2_information_page import PillarTwoInformationPage, GMT_CATEGORIES
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 Information"


def _login_and_open(case, page):
    perform_login(case, page)
    p2info = PillarTwoInformationPage(page)
    case.action("Navigating to /wta/PillarTwoInformation", kind="navigate")
    p2info.goto()
    return p2info


@pytest.mark.smoke
def test_p2info_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "P2Info_01", FEATURE, "Pillar 2 > Information loads with the jurisdiction/category placeholder",
        description="The page must load with the 'Select Jurisdictions and Categories' placeholder shown.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Information\n2. Verify the placeholder text is visible",
    )
    p2info = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(p2info.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok,
               locator=p2info.placeholder_text)

    actual = ("Pillar 2 > Information loaded with the jurisdiction/category placeholder visible." if ok else
              "Pillar 2 > Information did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2info_02_all_nine_gmt_categories_listed(page, result):
    case = Case(
        page, "P2Info_02", FEATURE, "All 9 GMT categories are listed in the left panel",
        description="The category checklist must show all 9 known Pillar Two GMT topics.",
        precondition="User is logged in and on Pillar 2 > Information.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Information\n2. Verify each of the 9 GMT categories is visible",
    )
    p2info = _login_and_open(case, page)
    case.step(2, "Verify each GMT category label is visible")
    missing = [c for c in GMT_CATEGORIES if not case.verify_visible(p2info.category.category_label(c), f"'{c}' category")]
    ok = not missing
    case.check("All 9 GMT categories are visible", ok, expected="all 9 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 9 GMT categories were visible in the left panel." if ok else
              f"Missing GMT categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2info_03_jurisdiction_only_keeps_placeholder(page, result):
    case = Case(
        page, "P2Info_03", FEATURE, "Selecting only a jurisdiction keeps the placeholder",
        description="Checking a country without also checking a GMT category must NOT render content.",
        precondition="User is logged in and on Pillar 2 > Information.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > Information\n2. Check 'Australia' only\n"
              "3. Verify the placeholder is still shown",
    )
    p2info = _login_and_open(case, page)
    case.step(2, "Select Australia's jurisdiction checkbox only")
    case.click(p2info.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(800)

    case.step(3, "Verify the placeholder is still visible")
    ok = case.verify_visible(p2info.placeholder_text, "left-panel instruction text")
    case.check("Placeholder remains visible after selecting a jurisdiction with no category", ok,
               expected="placeholder still visible", actual=ok, locator=p2info.placeholder_text)

    actual = ("Selecting Australia alone left the placeholder in place, confirming a GMT category is "
              "also required." if ok else
              "Selecting a jurisdiction alone unexpectedly rendered content without a category.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2info_04_jurisdiction_and_category_renders_content(page, result):
    case = Case(
        page, "P2Info_04", FEATURE, "Selecting a jurisdiction and a category renders content",
        description="Checking 'Australia' AND the 'Scope of GMT' category must replace the placeholder "
                     "with a 'Showing information of Australia' content header.",
        precondition="User is logged in and on Pillar 2 > Information.",
        test_data="Country: Australia / Category: Scope of GMT",
        steps="1. Log in and open Pillar 2 > Information\n2. Check 'Australia'\n"
              "3. Check 'Scope of GMT'\n4. Verify 'Showing information of' content header appears",
    )
    p2info = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(p2info.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)

    case.step(3, "Select the 'Scope of GMT' category")
    case.click(p2info.category.category_checkbox("Scope of GMT"), "'Scope of GMT' category checkbox")
    wait_for_content(p2info.showing_heading("Australia"))

    case.step(4, "Verify content rendered")
    ok = case.verify_visible(p2info.showing_heading("Australia"), "'Showing information of ...' header")
    case.check("Content header 'Showing information of ...' is visible", ok, expected="visible", actual=ok,
               locator=p2info.showing_heading("Australia"))

    actual = ("Selecting Australia and 'Scope of GMT' rendered the 'Showing information of Australia' "
              "content header, replacing the placeholder." if ok else
              "Selecting a jurisdiction and a category did not render the expected content header.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2info_05_region_tab_switch(page, result):
    case = Case(
        page, "P2Info_05", FEATURE, "Switching region tabs changes the visible country list",
        description="Clicking 'Europe' must hide Asia Pacific-only countries like 'Australia'.",
        precondition="User is logged in and on Pillar 2 > Information.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Information\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer listed",
    )
    p2info = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(p2info.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Australia' is hidden")
    ok = not p2info.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("'Australia' is not listed under 'Europe'", ok, expected="hidden", actual=not ok)

    actual = ("Switching to the 'Europe' region tab hid 'Australia' from the list." if ok else
              "Switching region tabs did not hide the expected out-of-region country.")
    result(case, actual, ok)
    assert ok, actual
