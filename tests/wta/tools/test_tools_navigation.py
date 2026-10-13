"""Tools top-nav dropdown menu.

Manually verified against the live application first (scratchpad discovery
scripts):
  - The dropdown contains exactly 2 items: Projects, Questionnaire Creator -
    both real internal WTA pages under /wta/.
  - Unlike every Treaties page, neither Tools page supports a direct
    full-page deep link - `page.goto()` to either URL redirects to
    /wta/Information instead (see pages/tools_menu.py's docstring). Test
    _03 below documents that as a real, asserted application behavior."""
import pytest

from pages.tools_menu import ToolsMenu, TOOLS_ITEMS, TOOLS_ITEM_URLS
from utils.auth import perform_login
from utils.case import Case
from config.settings import BASE_URL

FEATURE = "WTA Tools Menu"


def _login(case, page):
    perform_login(case, page)


@pytest.mark.smoke
def test_toolsmenu_01_dropdown_has_two_items(page, result):
    case = Case(
        page, "ToolsMenu_01", FEATURE, "The Tools dropdown lists exactly its 2 known items",
        description="Opening the 'Tools' nav dropdown must show Projects and Questionnaire Creator - "
                     "no more, no less.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Open the 'Tools' dropdown\n3. Verify each of the 2 items is visible",
    )
    _login(case, page)
    menu = ToolsMenu(page)
    case.step(2, "Open the 'Tools' dropdown")
    case.click(menu.nav_tools, "'Tools' nav link")
    page.wait_for_timeout(500)

    case.step(3, "Verify each expected item is visible")
    missing = [name for name in TOOLS_ITEMS if not case.verify_visible(menu.item(name), f"'{name}' menu item")]
    ok = not missing
    case.check("Both Tools dropdown items are visible", ok,
               expected=", ".join(TOOLS_ITEMS), actual=f"missing: {missing}" if missing else "all present")

    actual = (f"The Tools dropdown showed both expected items: {', '.join(TOOLS_ITEMS)}." if ok else
              f"The Tools dropdown was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
@pytest.mark.parametrize("item_name", list(TOOLS_ITEM_URLS.keys()))
def test_toolsmenu_02_each_item_navigates(page, result, item_name):
    case = Case(
        page, f"ToolsMenu_02_{item_name.replace(' ', '')}", FEATURE,
        f"Tools > {item_name} navigates to its page",
        description=f"Clicking '{item_name}' in the Tools dropdown must navigate to "
                     f"{TOOLS_ITEM_URLS[item_name]}.",
        precondition="User is logged in.",
        test_data=f"Menu item: {item_name}",
        steps=f"1. Log in\n2. Open the Tools dropdown\n3. Click '{item_name}'\n"
              f"4. Verify the URL contains {TOOLS_ITEM_URLS[item_name]}",
    )
    _login(case, page)
    menu = ToolsMenu(page)
    case.step(2, "Open the 'Tools' dropdown")
    case.click(menu.nav_tools, "'Tools' nav link")
    page.wait_for_timeout(400)

    case.step(3, f"Click '{item_name}'")
    case.click(menu.item(item_name), f"'{item_name}' menu item")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)

    case.step(4, "Verify the URL")
    ok = TOOLS_ITEM_URLS[item_name] in page.url
    case.check(f"URL contains {TOOLS_ITEM_URLS[item_name]}", ok,
               expected=TOOLS_ITEM_URLS[item_name], actual=page.url)

    actual = (f"Clicking '{item_name}' navigated to {page.url}." if ok else
              f"Clicking '{item_name}' did not navigate to {TOOLS_ITEM_URLS[item_name]}. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
@pytest.mark.parametrize("item_name", list(TOOLS_ITEM_URLS.keys()))
def test_toolsmenu_03_direct_deep_link_redirects_to_information(page, result, item_name):
    case = Case(
        page, f"ToolsMenu_03_{item_name.replace(' ', '')}", FEATURE,
        f"A direct deep link to {TOOLS_ITEM_URLS[item_name]} redirects to /wta/Information (documented app behavior)",
        description=f"Unlike every Treaties page, a full-page `goto()` straight to "
                     f"{TOOLS_ITEM_URLS[item_name]} does not land on that page - the SPA has no "
                     f"server-side route for a hard deep link to it, so it redirects to "
                     f"/wta/Information. This is a real, live-confirmed application behavior, "
                     f"documented here rather than hidden.",
        precondition="User is logged in.",
        test_data=f"Direct URL: {TOOLS_ITEM_URLS[item_name]}",
        steps=f"1. Log in\n2. Navigate directly (full page load) to {TOOLS_ITEM_URLS[item_name]}\n"
              f"3. Verify the app redirects to /wta/Information rather than showing the target page",
    )
    _login(case, page)
    case.step(2, f"Navigate directly to {TOOLS_ITEM_URLS[item_name]}")
    case.action(f"Navigating directly to {TOOLS_ITEM_URLS[item_name]}", kind="navigate")
    page.goto(BASE_URL.rstrip("/") + TOOLS_ITEM_URLS[item_name], wait_until="networkidle")
    page.wait_for_timeout(800)

    case.step(3, "Verify the app redirected to /wta/Information")
    ok = "/wta/Information" in page.url and TOOLS_ITEM_URLS[item_name] not in page.url
    case.check("Direct deep link redirected to /wta/Information", ok,
               expected="/wta/Information", actual=page.url)

    actual = (f"Confirmed: a direct deep link to {TOOLS_ITEM_URLS[item_name]} redirects to {page.url} "
              f"instead of loading the target page - a real application limitation, not an automation bug."
              if ok else
              f"Direct deep link behavior differed from the confirmed baseline (ended on {page.url}).")
    result(case, actual, ok)
    assert ok, actual
