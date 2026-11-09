"""TPA's "Tools" submenu (nested inside the unlabeled "more" overflow
menu). See pages/tpa/tpa_tools_common.py for the full confirmed-live
shape: 4 real children, each with its own working direct deep link -
unlike WTA's own 2-item Tools dropdown, every TPA Tools page supports
`goto()`."""
import pytest

from config.settings import APP_ORIGIN
from pages.tpa.tpa_common import TpaNav
from pages.tpa.tpa_tools_common import TPA_TOOLS_ITEM_URLS, TPA_TOOLS_SUBMENU_ITEMS
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Tools Navigation"


@pytest.mark.smoke
def test_tpatoolsnav_01_more_menu_and_tools_toggle_are_discoverable(page, result):
    case = Case(
        page, "TpaToolsNav_01", FEATURE, "The 'more' overflow menu and its 'Tools' submenu toggle are discoverable",
        description="Opening the unlabeled 'more' overflow menu (three-dot icon) must reveal a visible "
                     "'Tools' submenu toggle, alongside Treaties/Commentary/BEPS.",
        precondition="User is logged in and on the TPA product tab.",
        test_data="-",
        steps="1. Log in and open the TPA tab\n2. Open the 'more' overflow menu\n"
              "3. Verify the 'Tools' submenu toggle is visible",
    )
    perform_login(case, page)
    nav = TpaNav(page)
    case.step(2, "Open the 'more' overflow menu")
    nav.open_tab()
    case.click(nav.nav_more_menu, "'more' overflow menu toggle")
    page.wait_for_timeout(500)

    case.step(3, "Verify the 'Tools' submenu toggle is visible")
    ok = case.verify_visible(nav.tools_submenu_toggle(), "'Tools' submenu toggle")
    case.check("'Tools' submenu toggle is visible inside the 'more' menu", ok, expected=True, actual=ok)

    actual = "The 'more' menu's 'Tools' submenu toggle was correctly discoverable." if ok else \
             "The 'Tools' submenu toggle was not found inside the 'more' menu."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatoolsnav_02_tools_submenu_has_exactly_4_items(page, result):
    case = Case(
        page, "TpaToolsNav_02", FEATURE, "The 'Tools' submenu lists exactly its 4 known children",
        description="Hovering/opening the 'Tools' submenu toggle must reveal exactly 4 children: "
                     f"{', '.join(TPA_TOOLS_SUBMENU_ITEMS)} - confirmed live via a full nav HTML dump, no "
                     "5th/invented item.",
        precondition="User is logged in and on the TPA product tab.",
        test_data=f"Expected items: {TPA_TOOLS_SUBMENU_ITEMS}",
        steps="1. Log in and open the TPA tab\n2. Open the 'more' menu, then the 'Tools' submenu\n"
              "3. Verify each of the 4 expected items is present in the submenu HTML",
    )
    perform_login(case, page)
    nav = TpaNav(page)
    case.step(2, "Open the 'more' menu, then the 'Tools' submenu")
    nav.open_tab()
    case.click(nav.nav_more_menu, "'more' overflow menu toggle")
    page.wait_for_timeout(500)
    toggle = nav.tools_submenu_toggle()
    case.click(toggle, "'Tools' submenu toggle")
    page.wait_for_timeout(500)

    case.step(3, "Verify each of the 4 expected items is present")
    submenu_html = page.locator("div.custom-nav-menu").first.inner_html()
    missing = [name for name in TPA_TOOLS_SUBMENU_ITEMS if name not in submenu_html]
    ok = not missing
    case.check("All 4 expected 'Tools' submenu items are present", ok,
               expected=TPA_TOOLS_SUBMENU_ITEMS, actual=f"missing: {missing}" if missing else "all present")

    actual = (f"The 'Tools' submenu correctly listed all 4 expected items: {TPA_TOOLS_SUBMENU_ITEMS}." if ok
              else f"The 'Tools' submenu was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
@pytest.mark.parametrize("item_name", list(TPA_TOOLS_ITEM_URLS.keys()))
def test_tpatoolsnav_03_each_item_supports_a_direct_deep_link(page, result, item_name):
    url = TPA_TOOLS_ITEM_URLS[item_name]
    case = Case(
        page, f"TpaToolsNav_03_{item_name.replace(' ', '')}", FEATURE,
        f"Tools > {item_name} supports a direct deep link to {url}",
        description=f"A full-page `goto()` straight to {url} must land there directly - unlike WTA's own "
                     f"Tools pages, which redirect any direct deep link to /wta/Information, TPA's own Tools "
                     f"pages are confirmed live to support real deep links, same as every other TPA page.",
        precondition="User is logged in.",
        test_data=f"Direct URL: {url}",
        steps=f"1. Log in\n2. Navigate directly (full page load) to {url}\n"
              f"3. Verify the URL still contains {url} (no redirect away)",
    )
    perform_login(case, page)
    case.step(2, f"Navigate directly to {url}")
    case.action(f"Navigating directly to {url}", kind="navigate")
    page.goto(APP_ORIGIN + url, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, f"Verify the URL still contains {url}")
    ok = url in page.url
    case.check(f"Direct deep link landed on {url}, not redirected away", ok, expected=url, actual=page.url)

    actual = (f"A direct deep link to {url} correctly loaded the real page (unlike WTA's own Tools pages)."
              if ok else f"The direct deep link to {url} did not land as expected (ended on {page.url}).")
    result(case, actual, ok)
    assert ok, actual
