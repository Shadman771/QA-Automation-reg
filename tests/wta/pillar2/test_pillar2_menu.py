"""Pillar 2 top-nav dropdown menu.

Manually verified against the live application first (scripts/discover_wta.py):
  - The dropdown contains exactly 7 items: Information, Compliance
    Calendar, Forms, Simulator, Country Commentary, Regulation, News.
  - Six of the seven are internal WTA pages (/wta/PillarTwoInformation,
    /wta/ComplianceCalendar, /wta/PillarTwoForms, /wta/CountryCommentary,
    /wta/PillarTwoRegulation, /wta/PillarTwoNews).
  - 'Simulator' has no href on its menu item and instead navigates OUT of
    the WTA module entirely, to /companydata/P2Simulator/ (the Transfer
    Pricing Analyzer's "Master Entity Chart" workspace) - a different
    product area, out of this suite's WTA scope, so it is covered here
    only as a navigation smoke check."""
import pytest

from pages.pillar2_menu import Pillar2Menu, PILLAR2_ITEMS
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 Menu"

ITEM_URLS = {
    "Information": "/wta/PillarTwoInformation",
    "Compliance Calendar": "/wta/ComplianceCalendar",
    "Forms": "/wta/PillarTwoForms",
    "Country Commentary": "/wta/CountryCommentary",
    "Regulation": "/wta/PillarTwoRegulation",
    "News": "/wta/PillarTwoNews",
}


def _login(case, page):
    perform_login(case, page)


@pytest.mark.smoke
def test_p2menu_01_dropdown_has_seven_items(page, result):
    case = Case(
        page, "P2Menu_01", FEATURE, "The Pillar 2 dropdown lists exactly its 7 known items",
        description="Opening the 'Pillar 2' nav dropdown must show Information, Compliance Calendar, "
                     "Forms, Simulator, Country Commentary, Regulation and News - no more, no less.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Open the 'Pillar 2' dropdown\n3. Verify each of the 7 items is visible",
    )
    _login(case, page)
    menu = Pillar2Menu(page)
    case.step(2, "Open the 'Pillar 2' dropdown")
    case.click(menu.nav_pillar2, "'Pillar 2' nav link")
    page.wait_for_timeout(500)

    case.step(3, "Verify each expected item is visible")
    missing = [name for name in PILLAR2_ITEMS if not case.verify_visible(menu.item(name), f"'{name}' menu item")]
    ok = not missing
    case.check("All 7 Pillar 2 dropdown items are visible", ok,
               expected=", ".join(PILLAR2_ITEMS), actual=f"missing: {missing}" if missing else "all present")

    actual = (f"The Pillar 2 dropdown showed all 7 expected items: {', '.join(PILLAR2_ITEMS)}." if ok else
              f"The Pillar 2 dropdown was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
@pytest.mark.parametrize("item_name", list(ITEM_URLS.keys()))
def test_p2menu_02_each_internal_item_navigates(page, result, item_name):
    case = Case(
        page, f"P2Menu_02_{item_name.replace(' ', '')}", FEATURE,
        f"Pillar 2 > {item_name} navigates to its page",
        description=f"Clicking '{item_name}' in the Pillar 2 dropdown must navigate to "
                     f"{ITEM_URLS[item_name]}.",
        precondition="User is logged in.",
        test_data=f"Menu item: {item_name}",
        steps=f"1. Log in\n2. Open the Pillar 2 dropdown\n3. Click '{item_name}'\n"
              f"4. Verify the URL contains {ITEM_URLS[item_name]}",
    )
    _login(case, page)
    menu = Pillar2Menu(page)
    case.step(2, "Open the 'Pillar 2' dropdown")
    case.click(menu.nav_pillar2, "'Pillar 2' nav link")
    page.wait_for_timeout(400)

    case.step(3, f"Click '{item_name}'")
    case.click(menu.item(item_name), f"'{item_name}' menu item")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)

    case.step(4, "Verify the URL")
    ok = ITEM_URLS[item_name] in page.url
    case.check(f"URL contains {ITEM_URLS[item_name]}", ok, expected=ITEM_URLS[item_name], actual=page.url)

    actual = (f"Clicking '{item_name}' navigated to {page.url}." if ok else
              f"Clicking '{item_name}' did not navigate to {ITEM_URLS[item_name]}. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2menu_03_simulator_navigates_outside_wta(page, result):
    case = Case(
        page, "P2Menu_03", FEATURE, "'Simulator' navigates out of the WTA module to the P2 Simulator workspace",
        description="Clicking 'Simulator' in the Pillar 2 dropdown must navigate to /companydata/P2Simulator/, "
                     "a different product area (Transfer Pricing Analyzer's 'Master Entity Chart'), not a "
                     "page under /wta/.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Open the Pillar 2 dropdown\n3. Click 'Simulator'\n"
              "4. Verify the URL is /companydata/P2Simulator/",
    )
    _login(case, page)
    menu = Pillar2Menu(page)
    case.step(2, "Open the 'Pillar 2' dropdown")
    case.click(menu.nav_pillar2, "'Pillar 2' nav link")
    page.wait_for_timeout(400)

    case.step(3, "Click 'Simulator'")
    case.click(menu.item("Simulator"), "'Simulator' menu item")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    case.step(4, "Verify the URL")
    ok = "/companydata/P2Simulator" in page.url
    case.check("URL contains /companydata/P2Simulator", ok,
               expected="/companydata/P2Simulator/", actual=page.url)

    actual = (f"Clicking 'Simulator' navigated to {page.url}, outside the /wta/ module as expected." if ok else
              f"Clicking 'Simulator' did not navigate to the expected P2 Simulator workspace. "
              f"Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual
