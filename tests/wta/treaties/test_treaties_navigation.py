"""Treaties top-nav dropdown menu.

Manually verified against the live application first (scripts/discover_treaties*.py):
  - The dropdown contains exactly 5 items: Full DTA, PE Clause, Other
    Articles, WHT Rates, MLI Data - all real internal WTA pages under
    /wta/. Unlike Pillar 2's dropdown, there is no external/out-of-module
    item here."""
import pytest

from pages.treaties_menu import TreatiesMenu, TREATIES_ITEMS, TREATIES_ITEM_URLS
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Treaties Menu"


def _login(case, page):
    perform_login(case, page)


@pytest.mark.smoke
def test_treatiesmenu_01_dropdown_has_five_items(page, result):
    case = Case(
        page, "TreatiesMenu_01", FEATURE, "The Treaties dropdown lists exactly its 5 known items",
        description="Opening the 'Treaties' nav dropdown must show Full DTA, PE Clause, Other Articles, "
                     "WHT Rates and MLI Data - no more, no less.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Open the 'Treaties' dropdown\n3. Verify each of the 5 items is visible",
    )
    _login(case, page)
    menu = TreatiesMenu(page)
    case.step(2, "Open the 'Treaties' dropdown")
    case.click(menu.nav_treaties, "'Treaties' nav link")
    page.wait_for_timeout(500)

    case.step(3, "Verify each expected item is visible")
    missing = [name for name in TREATIES_ITEMS if not case.verify_visible(menu.item(name), f"'{name}' menu item")]
    ok = not missing
    case.check("All 5 Treaties dropdown items are visible", ok,
               expected=", ".join(TREATIES_ITEMS), actual=f"missing: {missing}" if missing else "all present")

    actual = (f"The Treaties dropdown showed all 5 expected items: {', '.join(TREATIES_ITEMS)}." if ok else
              f"The Treaties dropdown was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
@pytest.mark.parametrize("item_name", list(TREATIES_ITEM_URLS.keys()))
def test_treatiesmenu_02_each_item_navigates(page, result, item_name):
    case = Case(
        page, f"TreatiesMenu_02_{item_name.replace(' ', '')}", FEATURE,
        f"Treaties > {item_name} navigates to its page",
        description=f"Clicking '{item_name}' in the Treaties dropdown must navigate to "
                     f"{TREATIES_ITEM_URLS[item_name]}.",
        precondition="User is logged in.",
        test_data=f"Menu item: {item_name}",
        steps=f"1. Log in\n2. Open the Treaties dropdown\n3. Click '{item_name}'\n"
              f"4. Verify the URL contains {TREATIES_ITEM_URLS[item_name]}",
    )
    _login(case, page)
    menu = TreatiesMenu(page)
    case.step(2, "Open the 'Treaties' dropdown")
    case.click(menu.nav_treaties, "'Treaties' nav link")
    page.wait_for_timeout(400)

    case.step(3, f"Click '{item_name}'")
    case.click(menu.item(item_name), f"'{item_name}' menu item")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)

    case.step(4, "Verify the URL")
    ok = TREATIES_ITEM_URLS[item_name] in page.url
    case.check(f"URL contains {TREATIES_ITEM_URLS[item_name]}", ok,
               expected=TREATIES_ITEM_URLS[item_name], actual=page.url)

    actual = (f"Clicking '{item_name}' navigated to {page.url}." if ok else
              f"Clicking '{item_name}' did not navigate to {TREATIES_ITEM_URLS[item_name]}. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual
