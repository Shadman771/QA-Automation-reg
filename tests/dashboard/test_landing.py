"""Landing page after login - the World Tax Analyzer "Information" workspace
at /wta/Information.

Elements asserted here were confirmed against the live application (main
nav: Information/Pillar 2/News/Forms/Regulations; right-hand tabs:
Workspace/World Tax Analyzer/Transfer Pricing Analyzer/RegBriefings; left
panel: "Jurisdictions and Categories" with region tabs Asia Pacific/
Americas/Europe/MEA and a country checklist).

Every click/fill/check below goes through `case.*`, which red-highlights
the exact element being interacted with or verified and pushes a live
event to the dashboard (see utils/case.py, utils/highlight.py, utils/dashboard.py).
"""
import pytest

from config.settings import LOGIN_EMAIL
from pages.landing_page import LandingPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Dashboard"


def _login(case, page, dismiss_cookies: bool = True):
    perform_login(case, page, dismiss_cookies=dismiss_cookies)


@pytest.mark.smoke
def test_landing_01_loads_after_login(page, result):
    case = Case(
        page, "LANDING_01", FEATURE, "Landing page loads after a successful login",
        description="After login the app must land on the World Tax Analyzer Information "
                     "workspace with the jurisdiction/category panel visible.",
        precondition="Valid credentials are used to log in.",
        test_data=f"Email: {LOGIN_EMAIL} / Password: <masked>",
        steps="1. Log in with valid credentials\n2. Verify the URL is /wta/Information\n"
              "3. Verify the 'Jurisdictions and Categories' panel is visible",
    )
    _login(case, page)
    landing = LandingPage(page)

    case.step(2, "Verify the landing page loaded")
    panel_visible = case.verify_visible(landing.jurisdictions_heading, "Jurisdictions and Categories heading")
    ok = "/wta/Information" in page.url and panel_visible
    case.check("URL is /wta/Information and the Jurisdictions panel is visible", ok,
               expected="/wta/Information with panel visible", actual=page.url,
               locator=landing.jurisdictions_heading)

    actual = (f"After login the app landed on {page.url} with the 'Jurisdictions and "
              f"Categories' panel visible." if ok else
              f"After login the app did not land on the expected page/panel. URL: {page.url}")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_landing_02_top_navigation_visible(page, result):
    case = Case(
        page, "LANDING_02", FEATURE, "Top navigation and product tabs are visible",
        description="The main module nav (Information/News/Forms/Regulations) and the "
                     "product tabs (Workspace/World Tax Analyzer/Transfer Pricing Analyzer/"
                     "RegBriefings) must be visible on the landing page.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify each nav link and product tab is visible",
    )
    _login(case, page)
    landing = LandingPage(page)

    case.step(2, "Verify main navigation links")
    nav_items = {
        "Information": landing.nav_information,
        "News": landing.nav_news,
        "Forms": landing.nav_forms,
        "Regulations": landing.nav_regulations,
    }
    missing = [name for name, loc in nav_items.items() if not case.verify_visible(loc, f"'{name}' nav link")]
    case.check("Information/News/Forms/Regulations links are visible", not missing,
               expected="all visible", actual=f"missing: {missing}" if missing else "all visible")

    case.step(3, "Verify product tabs")
    tabs = {
        "Workspace": landing.tab_workspace,
        "World Tax Analyzer": landing.tab_world_tax_analyzer,
        "Transfer Pricing Analyzer": landing.tab_transfer_pricing_analyzer,
        "RegBriefings": landing.tab_regbriefings,
    }
    missing_tabs = [name for name, loc in tabs.items() if not case.verify_visible(loc, f"'{name}' tab")]
    case.check("Workspace/World Tax Analyzer/Transfer Pricing Analyzer/RegBriefings tabs are visible",
               not missing_tabs, expected="all visible",
               actual=f"missing: {missing_tabs}" if missing_tabs else "all visible")

    ok = not missing and not missing_tabs
    actual = ("All main navigation links (Information, News, Forms, Regulations) and product "
              "tabs (Workspace, World Tax Analyzer, Transfer Pricing Analyzer, RegBriefings) "
              "are visible." if ok else
              f"Missing nav links: {missing}. Missing tabs: {missing_tabs}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_03_navigate_to_news(page, result):
    case = Case(
        page, "LANDING_03", FEATURE, "Clicking the News nav link navigates to the News module",
        description="Clicking 'News' in the top nav must navigate to /wta/News.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click 'News' in the top navigation\n3. Verify the URL is /wta/News",
    )
    _login(case, page)
    landing = LandingPage(page)

    case.step(2, "Click the News nav link")
    case.click(landing.nav_news, "'News' nav link")
    page.wait_for_load_state("networkidle")

    case.step(3, "Verify the URL")
    ok = "/wta/News" in page.url
    case.check("URL contains /wta/News", ok, expected="/wta/News", actual=page.url)

    actual = (f"Clicking 'News' navigated to {page.url}." if ok else
              f"Clicking 'News' did not navigate to the News module. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_04_cookie_banner_dismissible(page, result):
    case = Case(
        page, "LANDING_04", FEATURE, "The cookie consent banner can be dismissed",
        description="The 'Please review our Terms and Conditions...' banner must disappear "
                     "after clicking Accept.",
        precondition="User is logged in; the cookie banner is showing (first session load).",
        test_data="-",
        steps="1. Log in\n2. Verify the cookie banner is visible\n3. Click Accept\n"
              "4. Verify the banner is no longer visible",
    )
    _login(case, page, dismiss_cookies=False)
    landing = LandingPage(page)

    case.step(2, "Check whether the cookie banner is visible before accepting")
    was_visible = case.verify_visible(landing.cookie_accept, "Cookie 'Accept' button")

    if not was_visible:
        case.check("Cookie banner was visible to dismiss", False,
                    expected="visible on first load", actual="not visible")
        actual = ("The cookie banner was not visible on this run (likely already dismissed for "
                  "this browser profile), so the dismiss action could not be exercised.")
        result(case, actual, False, failed_step="Step 2 - cookie banner visibility")
        pytest.skip("Cookie banner was not present this run - nothing to dismiss.")

    case.step(3, "Click Accept")
    case.click(landing.cookie_accept, "Cookie 'Accept' button")
    page.wait_for_timeout(500)

    case.step(4, "Verify the banner is gone")
    now_visible = landing.cookie_accept.is_visible()
    ok = not now_visible
    case.check("Cookie banner is no longer visible after Accept", ok,
               expected="not visible", actual=now_visible)

    actual = ("Clicking Accept dismissed the cookie banner." if ok else
              "The cookie banner was still visible after clicking Accept.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_05_jurisdiction_panel_interaction(page, result):
    case = Case(
        page, "LANDING_05", FEATURE, "Selecting a jurisdiction checks its checkbox",
        description="Clicking a country in the Jurisdictions panel (e.g. Australia) must "
                     "check its checkbox, confirming the left panel is interactive.",
        precondition="User is logged in and on the landing page, Asia Pacific region selected by default.",
        test_data="Country: Australia",
        steps="1. Log in\n2. Click the 'Australia' checkbox in the Jurisdictions panel\n"
              "3. Verify the checkbox becomes checked",
    )
    _login(case, page)
    landing = LandingPage(page)

    case.step(2, "Select Australia in the Jurisdictions panel")
    case.click(landing.country_checkbox_label("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)

    case.step(3, "Verify Australia is now checked")
    is_checked = page.evaluate(
        """() => {
            const label = [...document.querySelectorAll('label,span,div')]
                .find(el => el.textContent.trim() === 'Australia');
            if (!label) return null;
            const row = label.closest('div');
            const box = row ? row.querySelector('input[type="checkbox"]') : null;
            return box ? box.checked : null;
        }"""
    )
    ok = is_checked is True
    case.check("Australia's checkbox is checked after clicking it", ok,
               expected=True, actual=is_checked)

    actual = ("Clicking 'Australia' in the Jurisdictions panel checked its checkbox, confirming "
              "the panel responds to selection." if ok else
              f"Clicking 'Australia' did not result in a checked checkbox (state: {is_checked}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_06_navigate_to_forms(page, result):
    case = Case(
        page, "LANDING_06", FEATURE, "Clicking the Forms nav link navigates to the Forms module",
        description="Clicking 'Forms' in the top nav must navigate to /wta/Forms.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click 'Forms' in the top navigation\n3. Verify the URL is /wta/Forms",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the Forms nav link")
    case.click(landing.nav_forms, "'Forms' nav link")
    page.wait_for_load_state("networkidle")
    case.step(3, "Verify the URL")
    ok = "/wta/Forms" in page.url
    case.check("URL contains /wta/Forms", ok, expected="/wta/Forms", actual=page.url)
    actual = (f"Clicking 'Forms' navigated to {page.url}." if ok else
              f"Clicking 'Forms' did not navigate to the Forms module. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_07_navigate_to_regulations(page, result):
    case = Case(
        page, "LANDING_07", FEATURE, "Clicking the Regulations nav link navigates to the Regulations module",
        description="Clicking 'Regulations' in the top nav must navigate to /wta/Regulations.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click 'Regulations' in the top navigation\n3. Verify the URL is /wta/Regulations",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the Regulations nav link")
    case.click(landing.nav_regulations, "'Regulations' nav link")
    page.wait_for_load_state("networkidle")
    case.step(3, "Verify the URL")
    ok = "/wta/Regulations" in page.url
    case.check("URL contains /wta/Regulations", ok, expected="/wta/Regulations", actual=page.url)
    actual = (f"Clicking 'Regulations' navigated to {page.url}." if ok else
              f"Clicking 'Regulations' did not navigate to the Regulations module. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_landing_08_pillar2_dropdown_button_visible(page, result):
    case = Case(
        page, "LANDING_08", FEATURE, "'Pillar 2' nav button is visible and enabled",
        description="The 'Pillar 2' dropdown trigger in the top nav must be visible and enabled. "
                     "Its dropdown contents are covered in depth by the WTA Pillar2 Menu module - "
                     "this is a light presence check only, to avoid duplicating that coverage.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify the 'Pillar 2' nav button is visible and enabled",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify the Pillar 2 nav button")
    visible = case.verify_visible(landing.nav_pillar2, "'Pillar 2' nav button")
    enabled = landing.nav_pillar2.is_enabled() if visible else False
    ok = visible and enabled
    case.check("'Pillar 2' nav button is visible and enabled", ok,
               expected="visible and enabled", actual=f"visible={visible}, enabled={enabled}",
               locator=landing.nav_pillar2)
    actual = ("The 'Pillar 2' nav button is visible and enabled." if ok else
              f"'Pillar 2' nav button was not both visible and enabled (visible={visible}, enabled={enabled}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_landing_09_asia_pacific_selected_by_default(page, result):
    case = Case(
        page, "LANDING_09", FEATURE, "'Asia Pacific' region tab is selected by default",
        description="On first load, the 'Asia Pacific' region tab must carry the active/selected "
                     "styling and 'Americas' must not.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify 'Asia Pacific' is the active region tab",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify the default active region tab")
    ap_active = landing.is_region_active("Asia Pacific")
    am_active = landing.is_region_active("Americas")
    ok = ap_active and not am_active
    case.check("'Asia Pacific' is active and 'Americas' is not, by default", ok,
               expected="Asia Pacific active, Americas inactive",
               actual=f"Asia Pacific active={ap_active}, Americas active={am_active}",
               locator=landing.region_tab("Asia Pacific"))
    actual = ("'Asia Pacific' is the default active region tab." if ok else
              f"Unexpected default region tab state: Asia Pacific active={ap_active}, "
              f"Americas active={am_active}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_10_switch_region_to_americas(page, result):
    case = Case(
        page, "LANDING_10", FEATURE, "Switching to the Americas region tab swaps the country list",
        description="Clicking 'Americas' must show Americas countries (e.g. Brazil) and hide "
                     "Asia Pacific countries (e.g. Australia).",
        precondition="User is logged in and on the landing page, Asia Pacific selected by default.",
        test_data="-",
        steps="1. Log in\n2. Click the 'Americas' region tab\n3. Verify Brazil is shown and "
              "Australia is hidden",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'Americas' region tab")
    case.click(landing.region_tab("Americas"), "'Americas' region tab")
    page.wait_for_timeout(500)
    case.step(3, "Verify the country list swapped")
    brazil_visible = landing.country_checkbox_label("Brazil").is_visible()
    australia_visible = landing.country_checkbox_label("Australia").is_visible()
    ok = brazil_visible and not australia_visible
    case.check("Brazil (Americas) is visible and Australia (Asia Pacific) is not", ok,
               expected="Brazil visible, Australia hidden",
               actual=f"Brazil visible={brazil_visible}, Australia visible={australia_visible}")
    actual = ("Switching to Americas correctly swapped the country list." if ok else
              f"Country list did not swap as expected: Brazil visible={brazil_visible}, "
              f"Australia visible={australia_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_11_switch_region_to_europe(page, result):
    case = Case(
        page, "LANDING_11", FEATURE, "Switching to the Europe region tab swaps the country list",
        description="Clicking 'Europe' must show Europe countries (e.g. France) and hide "
                     "Asia Pacific countries (e.g. Australia).",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click the 'Europe' region tab\n3. Verify France is shown and "
              "Australia is hidden",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(landing.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)
    case.step(3, "Verify the country list swapped")
    france_visible = landing.country_checkbox_label("France").is_visible()
    australia_visible = landing.country_checkbox_label("Australia").is_visible()
    ok = france_visible and not australia_visible
    case.check("France (Europe) is visible and Australia (Asia Pacific) is not", ok,
               expected="France visible, Australia hidden",
               actual=f"France visible={france_visible}, Australia visible={australia_visible}")
    actual = ("Switching to Europe correctly swapped the country list." if ok else
              f"Country list did not swap as expected: France visible={france_visible}, "
              f"Australia visible={australia_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_12_switch_region_to_mea(page, result):
    case = Case(
        page, "LANDING_12", FEATURE, "Switching to the MEA region tab swaps the country list",
        description="Clicking 'MEA' must show MEA countries (e.g. Egypt) and hide Asia Pacific "
                     "countries (e.g. Australia).",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click the 'MEA' region tab\n3. Verify Egypt is shown and Australia "
              "is hidden",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'MEA' region tab")
    case.click(landing.region_tab("MEA"), "'MEA' region tab")
    page.wait_for_timeout(500)
    case.step(3, "Verify the country list swapped")
    egypt_visible = landing.country_checkbox_label("Egypt").is_visible()
    australia_visible = landing.country_checkbox_label("Australia").is_visible()
    ok = egypt_visible and not australia_visible
    case.check("Egypt (MEA) is visible and Australia (Asia Pacific) is not", ok,
               expected="Egypt visible, Australia hidden",
               actual=f"Egypt visible={egypt_visible}, Australia visible={australia_visible}")
    actual = ("Switching to MEA correctly swapped the country list." if ok else
              f"Country list did not swap as expected: Egypt visible={egypt_visible}, "
              f"Australia visible={australia_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_13_region_tab_active_state_toggles(page, result):
    case = Case(
        page, "LANDING_13", FEATURE, "Clicking a region tab activates it and deactivates the previous one",
        description="After clicking 'Americas', it must carry the active/selected styling and "
                     "'Asia Pacific' must no longer carry it.",
        precondition="User is logged in and on the landing page, Asia Pacific active by default.",
        test_data="-",
        steps="1. Log in\n2. Click the 'Americas' region tab\n3. Verify Americas is now active "
              "and Asia Pacific is not",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'Americas' region tab")
    case.click(landing.region_tab("Americas"), "'Americas' region tab")
    page.wait_for_timeout(400)
    case.step(3, "Verify the active tab toggled")
    am_active = landing.is_region_active("Americas")
    ap_active = landing.is_region_active("Asia Pacific")
    ok = am_active and not ap_active
    case.check("'Americas' is now active and 'Asia Pacific' is not", ok,
               expected="Americas active, Asia Pacific inactive",
               actual=f"Americas active={am_active}, Asia Pacific active={ap_active}",
               locator=landing.region_tab("Americas"))
    actual = ("Clicking 'Americas' correctly toggled the active region tab." if ok else
              f"Active tab did not toggle as expected: Americas active={am_active}, "
              f"Asia Pacific active={ap_active}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_14_search_countries_filters_list(page, result):
    case = Case(
        page, "LANDING_14", FEATURE, "Searching countries filters the jurisdiction checklist",
        description="Typing 'Austra' in the country search box must show Australia and hide "
                     "non-matching countries (e.g. Bangladesh).",
        precondition="User is logged in and on the landing page, Asia Pacific region active.",
        test_data="Search term: Austra",
        steps="1. Log in\n2. Type 'Austra' into the country search box\n3. Verify Australia is "
              "shown and Bangladesh is hidden",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type 'Austra' into the country search box")
    case.fill(landing.search_countries, "Austra", "Country search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify the filtered list")
    australia_visible = landing.country_checkbox_label("Australia").is_visible()
    bangladesh_visible = landing.country_checkbox_label("Bangladesh").is_visible()
    ok = australia_visible and not bangladesh_visible
    case.check("Australia is shown and Bangladesh is hidden after searching 'Austra'", ok,
               expected="Australia visible, Bangladesh hidden",
               actual=f"Australia visible={australia_visible}, Bangladesh visible={bangladesh_visible}")
    actual = ("Searching 'Austra' correctly filtered the country list." if ok else
              f"Country search filter did not behave as expected: Australia visible="
              f"{australia_visible}, Bangladesh visible={bangladesh_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_15_search_countries_case_insensitive(page, result):
    case = Case(
        page, "LANDING_15", FEATURE, "Country search is case-insensitive",
        description="Typing a lowercase search term ('austra') must still match 'Australia'.",
        precondition="User is logged in and on the landing page.",
        test_data="Search term: austra (lowercase)",
        steps="1. Log in\n2. Type 'austra' (lowercase) into the country search box\n"
              "3. Verify Australia is still shown",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type 'austra' (lowercase) into the country search box")
    case.fill(landing.search_countries, "austra", "Country search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify Australia is still shown")
    ok = landing.country_checkbox_label("Australia").is_visible()
    case.check("Australia is shown for the lowercase search 'austra'", ok,
               expected="visible", actual=ok, locator=landing.country_checkbox_label("Australia"))
    actual = ("Country search is case-insensitive: 'austra' matched Australia." if ok else
              "Lowercase search 'austra' did not match Australia - search may be case-sensitive.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_16_search_countries_no_match(page, result):
    case = Case(
        page, "LANDING_16", FEATURE, "Searching for a non-existent country shows a 'no results' message",
        description="Typing a term that matches no country must show "
                     "'No countries found matching \"<term>\"'.",
        precondition="User is logged in and on the landing page.",
        test_data="Search term: zzzznotreal",
        steps="1. Log in\n2. Type 'zzzznotreal' into the country search box\n"
              "3. Verify the 'No countries found matching...' message appears",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type a non-matching term into the country search box")
    case.fill(landing.search_countries, "zzzznotreal", "Country search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify the no-match message")
    message = page.get_by_text('No countries found matching "zzzznotreal"')
    ok = message.is_visible()
    case.check("'No countries found matching...' message is shown", ok,
               expected="visible", actual=ok, locator=message)
    actual = ("The 'No countries found matching...' empty-state message correctly appeared." if ok
              else "The expected no-match message did not appear for a non-existent country search.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_17_clear_country_search_restores_list(page, result):
    case = Case(
        page, "LANDING_17", FEATURE, "Clearing the country search box restores the full list",
        description="After filtering to 'Austra' and then clearing the search box, the full "
                     "country list (including Bangladesh) must reappear.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Search 'Austra'\n3. Clear the search box\n"
              "4. Verify Bangladesh reappears",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Search 'Austra'")
    case.fill(landing.search_countries, "Austra", "Country search box")
    page.wait_for_timeout(400)
    case.step(3, "Clear the search box")
    case.fill(landing.search_countries, "", "Country search box (cleared)")
    page.wait_for_timeout(400)
    case.step(4, "Verify the full list is restored")
    ok = landing.country_checkbox_label("Bangladesh").is_visible()
    case.check("Bangladesh reappears after clearing the country search", ok,
               expected="visible", actual=ok, locator=landing.country_checkbox_label("Bangladesh"))
    actual = ("Clearing the country search box correctly restored the full country list." if ok
              else "Bangladesh did not reappear after clearing the country search box.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_18_search_categories_filters_tree(page, result):
    case = Case(
        page, "LANDING_18", FEATURE, "Searching categories filters the category tree",
        description="Typing 'Liability' in the category search box must show 'Liability to Tax' "
                     "and hide non-matching categories (e.g. 'Tax Compliance').",
        precondition="User is logged in and on the landing page.",
        test_data="Search term: Liability",
        steps="1. Log in\n2. Type 'Liability' into the category search box\n"
              "3. Verify 'Liability to Tax' is shown and 'Tax Compliance' is hidden",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type 'Liability' into the category search box")
    case.fill(landing.search_categories, "Liability", "Category search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify the filtered category tree")
    liability_visible = landing.category_label("Liability to Tax").is_visible()
    compliance_visible = landing.category_label("Tax Compliance").is_visible()
    ok = liability_visible and not compliance_visible
    case.check("'Liability to Tax' is shown and 'Tax Compliance' is hidden after searching "
               "'Liability'", ok, expected="Liability to Tax visible, Tax Compliance hidden",
               actual=f"Liability to Tax visible={liability_visible}, "
                      f"Tax Compliance visible={compliance_visible}")
    actual = ("Searching 'Liability' correctly filtered the category tree." if ok else
              f"Category search filter did not behave as expected: Liability to Tax visible="
              f"{liability_visible}, Tax Compliance visible={compliance_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_19_search_categories_no_match(page, result):
    case = Case(
        page, "LANDING_19", FEATURE, "Searching for a non-existent category shows 'No results found.'",
        description="Typing a term that matches no category must show 'No results found.' - "
                     "note this wording differs from the country search's empty state, which "
                     "echoes the search term.",
        precondition="User is logged in and on the landing page.",
        test_data="Search term: zzznotreal",
        steps="1. Log in\n2. Type 'zzznotreal' into the category search box\n"
              "3. Verify 'No results found.' appears",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type a non-matching term into the category search box")
    case.fill(landing.search_categories, "zzznotreal", "Category search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify the no-match message")
    message = page.get_by_text("No results found.", exact=True)
    ok = message.is_visible()
    case.check("'No results found.' message is shown", ok, expected="visible", actual=ok,
               locator=message)
    actual = ("The 'No results found.' empty-state message correctly appeared for the category "
              "search." if ok else
              "The expected 'No results found.' message did not appear for a non-existent "
              "category search.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_20_clear_category_search_restores_tree(page, result):
    case = Case(
        page, "LANDING_20", FEATURE, "Clearing the category search box restores the full tree",
        description="After filtering to 'Liability' and then clearing the search box, the full "
                     "category tree (including 'Tax Compliance') must reappear.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Search 'Liability'\n3. Clear the search box\n"
              "4. Verify 'Tax Compliance' reappears",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Search 'Liability'")
    case.fill(landing.search_categories, "Liability", "Category search box")
    page.wait_for_timeout(400)
    case.step(3, "Clear the search box")
    case.fill(landing.search_categories, "", "Category search box (cleared)")
    page.wait_for_timeout(400)
    case.step(4, "Verify the full tree is restored")
    ok = landing.category_label("Tax Compliance").is_visible()
    case.check("'Tax Compliance' reappears after clearing the category search", ok,
               expected="visible", actual=ok, locator=landing.category_label("Tax Compliance"))
    actual = ("Clearing the category search box correctly restored the full category tree." if ok
              else "'Tax Compliance' did not reappear after clearing the category search box.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_landing_21_check_all_unchecked_by_default(page, result):
    case = Case(
        page, "LANDING_21", FEATURE, "'Check All' (categories) is unchecked by default",
        description="On first load, the 'Check All' category checkbox must be unchecked.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify the 'Check All' checkbox is unchecked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify 'Check All' is unchecked")
    checked = landing.is_category_checked("Check All")
    ok = checked is False
    case.check("'Check All' checkbox is unchecked by default", ok,
               expected=False, actual=checked, locator=landing.check_all_label)
    actual = ("'Check All' is unchecked by default, as expected." if ok else
              f"'Check All' was not unchecked by default (state: {checked}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_22_check_all_checks_every_category(page, result):
    case = Case(
        page, "LANDING_22", FEATURE, "'Check All' checks every top-level category",
        description="Clicking 'Check All' must check every top-level category, e.g. "
                     "'Liability to Tax'.",
        precondition="User is logged in and on the landing page, 'Check All' unchecked.",
        test_data="-",
        steps="1. Log in\n2. Click 'Check All'\n3. Verify 'Liability to Tax' becomes checked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click 'Check All'")
    case.click(landing.check_all_label, "'Check All' checkbox")
    page.wait_for_timeout(400)
    case.step(3, "Verify a top-level category is now checked")
    check_all_state = landing.is_category_checked("Check All")
    liability_state = landing.is_category_checked("Liability to Tax")
    ok = check_all_state is True and liability_state is True
    case.check("'Check All' and 'Liability to Tax' are both checked after clicking 'Check All'",
               ok, expected="both True",
               actual=f"Check All={check_all_state}, Liability to Tax={liability_state}",
               locator=landing.category_label("Liability to Tax"))
    actual = ("Clicking 'Check All' correctly cascaded to check every top-level category." if ok
              else f"'Check All' did not correctly cascade: Check All={check_all_state}, "
                   f"Liability to Tax={liability_state}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_23_uncheck_check_all_unchecks_every_category(page, result):
    case = Case(
        page, "LANDING_23", FEATURE, "Unchecking 'Check All' unchecks every category again",
        description="After checking 'Check All', clicking it again must uncheck every category, "
                     "e.g. 'Liability to Tax'.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click 'Check All' to check it\n3. Click 'Check All' again to uncheck "
              "it\n4. Verify 'Liability to Tax' is unchecked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click 'Check All' to check it")
    case.click(landing.check_all_label, "'Check All' checkbox")
    page.wait_for_timeout(300)
    case.step(3, "Click 'Check All' again to uncheck it")
    case.click(landing.check_all_label, "'Check All' checkbox")
    page.wait_for_timeout(400)
    case.step(4, "Verify categories are unchecked")
    check_all_state = landing.is_category_checked("Check All")
    liability_state = landing.is_category_checked("Liability to Tax")
    ok = check_all_state is False and liability_state is False
    case.check("'Check All' and 'Liability to Tax' are both unchecked after toggling 'Check All' "
               "off", ok, expected="both False",
               actual=f"Check All={check_all_state}, Liability to Tax={liability_state}",
               locator=landing.category_label("Liability to Tax"))
    actual = ("Toggling 'Check All' off correctly unchecked every category." if ok else
              f"'Check All' off did not correctly uncheck categories: Check All={check_all_state}, "
              f"Liability to Tax={liability_state}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_24_depth_control_expands_category_panel(page, result):
    case = Case(
        page, "LANDING_24", FEATURE, "Depth control expands the visible category tree",
        description="Clicking Depth level '4' must reveal substantially more nested category "
                     "content than the default view (confirmed live: default/1 ~585 characters "
                     "of panel text vs. depth 4 ~3519 characters).",
        precondition="User is logged in and on the landing page.",
        test_data="Depth level: 4",
        steps="1. Log in\n2. Record the category panel's text length\n3. Click Depth '4'\n"
              "4. Verify the panel's text length increased substantially",
    )
    _login(case, page)
    landing = LandingPage(page)

    def panel_text_len():
        return page.evaluate(
            """() => {
                const input = document.querySelector('input[placeholder="Search categories"]');
                let container = input.closest('div');
                for (let i=0;i<6 && container; i++) container = container.parentElement;
                return container.innerText.length;
            }"""
        )

    case.step(2, "Record the default category panel text length")
    before_len = panel_text_len()

    case.step(3, "Click Depth '4'")
    case.click(landing.depth_button(4), "Depth level '4'")
    page.wait_for_timeout(600)

    case.step(4, "Verify the panel expanded")
    after_len = panel_text_len()
    ok = after_len > before_len * 2
    case.check("Category panel text length roughly doubles or more after selecting Depth 4", ok,
               expected=f"> {before_len * 2}", actual=after_len)
    actual = (f"Selecting Depth '4' expanded the category panel from {before_len} to {after_len} "
              f"characters of visible content." if ok else
              f"Depth '4' did not measurably expand the panel: before={before_len}, "
              f"after={after_len}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_25_multi_select_countries(page, result):
    case = Case(
        page, "LANDING_25", FEATURE, "Selecting a second country keeps the first one checked",
        description="Checking 'Australia' then 'Bangladesh' must leave both checked - the "
                     "jurisdiction panel supports multi-select.",
        precondition="User is logged in and on the landing page.",
        test_data="Countries: Australia, Bangladesh",
        steps="1. Log in\n2. Check 'Australia'\n3. Check 'Bangladesh'\n"
              "4. Verify both remain checked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Check 'Australia'")
    case.click(landing.country_checkbox_label("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(300)
    case.step(3, "Check 'Bangladesh'")
    case.click(landing.country_checkbox_label("Bangladesh"), "'Bangladesh' checkbox")
    page.wait_for_timeout(400)
    case.step(4, "Verify both are checked")
    australia_checked = landing.is_country_checked("Australia")
    bangladesh_checked = landing.is_country_checked("Bangladesh")
    ok = australia_checked is True and bangladesh_checked is True
    case.check("Both 'Australia' and 'Bangladesh' remain checked (multi-select)", ok,
               expected="both True",
               actual=f"Australia={australia_checked}, Bangladesh={bangladesh_checked}",
               locator=landing.country_checkbox_label("Bangladesh"))
    actual = ("The jurisdiction panel correctly supports multi-select: both Australia and "
              "Bangladesh remained checked." if ok else
              f"Multi-select did not behave as expected: Australia={australia_checked}, "
              f"Bangladesh={bangladesh_checked}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_26_deselect_country(page, result):
    case = Case(
        page, "LANDING_26", FEATURE, "Deselecting a checked country unchecks it",
        description="Checking then re-clicking 'Australia' must uncheck it.",
        precondition="User is logged in and on the landing page.",
        test_data="Country: Australia",
        steps="1. Log in\n2. Check 'Australia'\n3. Click 'Australia' again to uncheck it\n"
              "4. Verify it is unchecked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Check 'Australia'")
    case.click(landing.country_checkbox_label("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(300)
    case.step(3, "Click 'Australia' again to uncheck it")
    case.click(landing.country_checkbox_label("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)
    case.step(4, "Verify it is unchecked")
    checked = landing.is_country_checked("Australia")
    ok = checked is False
    case.check("'Australia' is unchecked after clicking it a second time", ok,
               expected=False, actual=checked, locator=landing.country_checkbox_label("Australia"))
    actual = ("Clicking 'Australia' a second time correctly unchecked it." if ok else
              f"'Australia' was not unchecked after a second click (state: {checked}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_27_workspace_tab_navigates_out_of_wta(page, result):
    case = Case(
        page, "LANDING_27", FEATURE, "'Workspace' product tab navigates to the Companydata dashboard",
        description="Clicking the 'Workspace' tab must navigate to /companydata/dashboard/ - a "
                     "different product area, out of this suite's WTA scope. Covered here only "
                     "as a navigation smoke check.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click the 'Workspace' tab\n3. Verify the URL is /companydata/dashboard/",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'Workspace' tab")
    case.click(landing.tab_workspace, "'Workspace' tab")
    page.wait_for_timeout(1200)
    case.step(3, "Verify the URL")
    ok = "/companydata/dashboard" in page.url
    case.check("URL contains /companydata/dashboard/", ok,
               expected="/companydata/dashboard/", actual=page.url)
    actual = (f"Clicking 'Workspace' navigated to {page.url}, the Companydata dashboard." if ok else
              f"Clicking 'Workspace' did not navigate to the expected area. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_28_transfer_pricing_analyzer_tab_navigates_out_of_wta(page, result):
    case = Case(
        page, "LANDING_28", FEATURE, "'Transfer Pricing Analyzer' tab navigates to the TPA module",
        description="Clicking the 'Transfer Pricing Analyzer' tab must navigate to /tpa/Home - a "
                     "different product area, out of this suite's WTA scope. Covered here only as "
                     "a navigation smoke check.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click the 'Transfer Pricing Analyzer' tab\n3. Verify the URL is /tpa/Home",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'Transfer Pricing Analyzer' tab")
    case.click(landing.tab_transfer_pricing_analyzer, "'Transfer Pricing Analyzer' tab")
    page.wait_for_timeout(1200)
    case.step(3, "Verify the URL")
    ok = "/tpa/Home" in page.url
    case.check("URL contains /tpa/Home", ok, expected="/tpa/Home", actual=page.url)
    actual = (f"Clicking 'Transfer Pricing Analyzer' navigated to {page.url}." if ok else
              f"Clicking 'Transfer Pricing Analyzer' did not navigate to the expected area. "
              f"Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_29_regbriefings_tab_navigates_out_of_wta(page, result):
    case = Case(
        page, "LANDING_29", FEATURE, "'RegBriefings' tab navigates to the RegBriefings module",
        description="Clicking the 'RegBriefings' tab must navigate to /regbrief/home/ - a "
                     "different product area, out of this suite's WTA scope. Covered here only as "
                     "a navigation smoke check.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click the 'RegBriefings' tab\n3. Verify the URL contains /regbrief/home/",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'RegBriefings' tab")
    case.click(landing.tab_regbriefings, "'RegBriefings' tab")
    page.wait_for_timeout(1200)
    case.step(3, "Verify the URL")
    ok = "/regbrief/home" in page.url
    case.check("URL contains /regbrief/home/", ok, expected="/regbrief/home/", actual=page.url)
    actual = (f"Clicking 'RegBriefings' navigated to {page.url}." if ok else
              f"Clicking 'RegBriefings' did not navigate to the expected area. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_30_browser_back_returns_to_information(page, result):
    case = Case(
        page, "LANDING_30", FEATURE, "Browser back navigation returns from News to Information",
        description="After navigating to News via the top nav, using the browser's back button "
                     "must return to /wta/Information.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Click 'News'\n3. Go back\n4. Verify the URL is /wta/Information",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click 'News'")
    case.click(landing.nav_news, "'News' nav link")
    page.wait_for_load_state("networkidle")
    case.step(3, "Navigate back")
    case.action("Navigating back", kind="navigate")
    page.go_back()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    case.step(4, "Verify the URL")
    ok = "/wta/Information" in page.url
    case.check("Browser back returns to /wta/Information", ok,
               expected="/wta/Information", actual=page.url)
    actual = (f"Browser back correctly returned to {page.url}." if ok else
              f"Browser back did not return to /wta/Information. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_31_page_reload_preserves_session(page, result):
    case = Case(
        page, "LANDING_31", FEATURE, "Reloading the page preserves the authenticated session",
        description="Reloading /wta/Information (F5) must keep the user authenticated and on the "
                     "same page, not bounce them to the login page.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Reload the page\n3. Verify the user is still on /wta/Information, "
              "not redirected to /auth/login",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Reload the page")
    case.action("Reloading the page", kind="navigate")
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(800)
    case.step(3, "Verify the session persisted")
    ok = "/wta/Information" in page.url and "/auth/login" not in page.url
    case.check("User remains on /wta/Information after reload (not redirected to login)", ok,
               expected="/wta/Information, not /auth/login", actual=page.url)
    actual = (f"Reloading the page correctly preserved the authenticated session; still on "
              f"{page.url}." if ok else
              f"Reloading the page did not preserve the session as expected. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_landing_32_placeholder_shown_before_selection(page, result):
    case = Case(
        page, "LANDING_32", FEATURE, "The content placeholder is shown before any selection",
        description="Before selecting a jurisdiction or category, the right panel must show "
                     "'Select Jurisdictions and Categories'.",
        precondition="User is logged in and on the landing page, nothing selected.",
        test_data="-",
        steps="1. Log in\n2. Verify the 'Select Jurisdictions and Categories' placeholder is visible",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify the placeholder")
    ok = case.verify_visible(landing.placeholder_text, "'Select Jurisdictions and Categories' placeholder")
    case.check("Placeholder text is visible before any selection", ok,
               expected="visible", actual=ok, locator=landing.placeholder_text)
    actual = ("The 'Select Jurisdictions and Categories' placeholder is correctly shown before "
              "any selection." if ok else "The expected placeholder text was not visible.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_33_exactly_four_region_tabs(page, result):
    case = Case(
        page, "LANDING_33", FEATURE, "Exactly 4 region tabs are present",
        description="The jurisdiction panel must show exactly 4 region tabs: Asia Pacific, "
                     "Americas, Europe, MEA - no more, no fewer.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify exactly 4 region tabs are present",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Count the region tabs")
    names = ["Asia Pacific", "Americas", "Europe", "MEA"]
    landing.region_tab("Asia Pacific").wait_for(state="visible")
    counts = {n: landing.region_tab(n).count() for n in names}
    ok = all(c == 1 for c in counts.values())
    case.check("Each of the 4 region tabs appears exactly once", ok,
               expected="1 each", actual=counts)
    actual = ("Exactly the 4 expected region tabs (Asia Pacific, Americas, Europe, MEA) are "
              "present." if ok else f"Unexpected region tab counts: {counts}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_34_asia_pacific_country_count(page, result):
    case = Case(
        page, "LANDING_34", FEATURE, "Asia Pacific region shows the expected number of countries",
        description="The Asia Pacific region (default) must list 25 countries, confirmed live "
                     "(Australia through Vietnam).",
        precondition="User is logged in and on the landing page, Asia Pacific active.",
        test_data="-",
        steps="1. Log in\n2. Count the visible country checkboxes in the Asia Pacific list\n"
              "3. Verify the count is 25",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Count Asia Pacific countries")
    # The country checklist isn't cleanly scoped by a shallow parent walk
    # from the search box (confirmed live) - instead, take every visible
    # checkbox that sits in DOM order between the "Search countries" input
    # and the "Search categories" input, which reliably brackets the list.
    # Both inputs must actually be present before this bracketing works.
    landing.search_countries.wait_for(state="visible")
    landing.search_categories.wait_for(state="visible")
    count = page.evaluate(
        """() => {
            const inputs = [...document.querySelectorAll('input')];
            const countriesIdx = inputs.findIndex(el => el.placeholder === 'Search countries');
            const categoriesIdx = inputs.findIndex(el => el.placeholder === 'Search categories');
            return inputs.slice(countriesIdx + 1, categoriesIdx)
                .filter(el => el.type === 'checkbox' && el.offsetParent !== null).length;
        }"""
    )
    case.step(3, "Verify the count")
    ok = count == 25
    case.check("Asia Pacific lists exactly 25 countries", ok, expected=25, actual=count)
    actual = (f"Asia Pacific correctly lists {count} countries." if ok else
              f"Expected 25 countries in Asia Pacific, found {count}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_35_exactly_five_main_nav_items(page, result):
    case = Case(
        page, "LANDING_35", FEATURE, "Exactly the 5 expected main nav items are present",
        description="The top nav must show Information, Pillar 2, News, Forms and Regulations - "
                     "no more, no fewer.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify each of the 5 main nav items appears exactly once",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Count the main nav items")
    landing.nav_information.wait_for(state="visible")
    counts = {
        "Information": landing.nav_information.count(),
        "Pillar 2": landing.nav_pillar2.count(),
        "News": landing.nav_news.count(),
        "Forms": landing.nav_forms.count(),
        "Regulations": landing.nav_regulations.count(),
    }
    ok = all(c == 1 for c in counts.values())
    case.check("Each of the 5 main nav items appears exactly once", ok, expected="1 each",
               actual=counts)
    actual = ("Exactly the 5 expected main nav items are present." if ok else
              f"Unexpected main nav item counts: {counts}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_36_expected_top_level_categories_present(page, result):
    case = Case(
        page, "LANDING_36", FEATURE, "Expected top-level categories are present in the tree",
        description="The category tree's default view must include the top-level categories "
                     "'Liability to Tax' and 'Tax Compliance'.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify 'Liability to Tax' and 'Tax Compliance' are visible",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify top-level categories")
    liability_visible = case.verify_visible(landing.category_label("Liability to Tax"), "'Liability to Tax' category")
    compliance_visible = case.verify_visible(landing.category_label("Tax Compliance"), "'Tax Compliance' category")
    ok = liability_visible and compliance_visible
    case.check("'Liability to Tax' and 'Tax Compliance' are both visible", ok,
               expected="both visible",
               actual=f"Liability to Tax={liability_visible}, Tax Compliance={compliance_visible}")
    actual = ("Both expected top-level categories are visible in the default tree view." if ok
              else f"Missing expected categories: Liability to Tax={liability_visible}, "
                   f"Tax Compliance={compliance_visible}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_37_exactly_four_product_tabs(page, result):
    case = Case(
        page, "LANDING_37", FEATURE, "Exactly 4 product tabs are present",
        description="The product-tab row must show Workspace, World Tax Analyzer, Transfer "
                     "Pricing Analyzer and RegBriefings - no more, no fewer.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify each of the 4 product tabs appears exactly once",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Count the product tabs")
    landing.tab_workspace.wait_for(state="visible")
    counts = {
        "Workspace": landing.tab_workspace.count(),
        "World Tax Analyzer": landing.tab_world_tax_analyzer.count(),
        "Transfer Pricing Analyzer": landing.tab_transfer_pricing_analyzer.count(),
        "RegBriefings": landing.tab_regbriefings.count(),
    }
    ok = all(c == 1 for c in counts.values())
    case.check("Each of the 4 product tabs appears exactly once", ok, expected="1 each",
               actual=counts)
    actual = ("Exactly the 4 expected product tabs are present." if ok else
              f"Unexpected product tab counts: {counts}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_38_select_single_category_without_check_all(page, result):
    case = Case(
        page, "LANDING_38", FEATURE, "A single category can be checked without using 'Check All'",
        description="Clicking 'Liability to Tax's checkbox directly must check it, while "
                     "'Check All' remains unchecked (it only reflects when every category is "
                     "checked). Note: the category LABEL text has no 'for' attribute linking it "
                     "to its checkbox (confirmed live) - clicking the label is a no-op; only the "
                     "checkbox input itself (or 'Check All', which has its own working handler) "
                     "toggles selection.",
        precondition="User is logged in and on the landing page.",
        test_data="Category: Liability to Tax",
        steps="1. Log in\n2. Click 'Liability to Tax's checkbox\n3. Verify it is checked and "
              "'Check All' remains unchecked",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click 'Liability to Tax's checkbox")
    case.click(landing.category_checkbox("Liability to Tax"), "'Liability to Tax' checkbox")
    page.wait_for_timeout(400)
    case.step(3, "Verify the individual checkbox state")
    liability_state = landing.is_category_checked("Liability to Tax")
    check_all_state = landing.is_category_checked("Check All")
    ok = liability_state is True and check_all_state is False
    case.check("'Liability to Tax' is checked while 'Check All' remains unchecked", ok,
               expected="Liability to Tax=True, Check All=False",
               actual=f"Liability to Tax={liability_state}, Check All={check_all_state}",
               locator=landing.category_label("Liability to Tax"))
    actual = ("A single category can be selected independently of 'Check All'." if ok else
              f"Unexpected state after selecting a single category: Liability to Tax="
              f"{liability_state}, Check All={check_all_state}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_39_search_countries_special_characters(page, result):
    case = Case(
        page, "LANDING_39", FEATURE, "Special-character input in the country search doesn't error",
        description="Typing special characters into the country search box must be handled "
                     "gracefully (the same 'No countries found...' empty state, no crash).",
        precondition="User is logged in and on the landing page.",
        test_data='Search term: @@@###$$$',
        steps="1. Log in\n2. Type '@@@###$$$' into the country search box\n"
              "3. Verify the page does not error and shows the no-match message",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type special characters into the country search box")
    case.fill(landing.search_countries, "@@@###$$$", "Country search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify graceful handling")
    message = page.get_by_text('No countries found matching "@@@###$$$"')
    panel_still_present = landing.jurisdictions_heading.is_visible()
    ok = message.is_visible() and panel_still_present
    case.check("Special-character search shows the no-match message without breaking the panel",
               ok, expected="no-match message visible, panel intact",
               actual=f"message visible={message.is_visible()}, panel visible={panel_still_present}")
    actual = ("Special-character input was handled gracefully with the expected empty-state "
              "message." if ok else
              "Special-character input did not produce the expected graceful empty state.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_40_search_categories_special_characters(page, result):
    case = Case(
        page, "LANDING_40", FEATURE, "Special-character input in the category search doesn't error",
        description="Typing special characters into the category search box must be handled "
                     "gracefully (the same 'No results found.' empty state, no crash).",
        precondition="User is logged in and on the landing page.",
        test_data='Search term: @@@###$$$',
        steps="1. Log in\n2. Type '@@@###$$$' into the category search box\n"
              "3. Verify the page does not error and shows 'No results found.'",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Type special characters into the category search box")
    case.fill(landing.search_categories, "@@@###$$$", "Category search box")
    page.wait_for_timeout(500)
    case.step(3, "Verify graceful handling")
    message = page.get_by_text("No results found.", exact=True)
    panel_still_present = landing.jurisdictions_heading.is_visible()
    ok = message.is_visible() and panel_still_present
    case.check("Special-character search shows 'No results found.' without breaking the panel",
               ok, expected="no-match message visible, panel intact",
               actual=f"message visible={message.is_visible()}, panel visible={panel_still_present}")
    actual = ("Special-character input was handled gracefully with the expected empty-state "
              "message." if ok else
              "Special-character input did not produce the expected graceful empty state.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_41_world_tax_analyzer_tab_stays_in_wta(page, result):
    case = Case(
        page, "LANDING_41", FEATURE, "'World Tax Analyzer' tab keeps the user within WTA",
        description="Clicking the already-active 'World Tax Analyzer' product tab must not "
                     "navigate away from the WTA module.",
        precondition="User is logged in and on the landing page (WTA already active).",
        test_data="-",
        steps="1. Log in\n2. Click the 'World Tax Analyzer' tab\n3. Verify the URL is still "
              "within /wta/",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Click the 'World Tax Analyzer' tab")
    case.click(landing.tab_world_tax_analyzer, "'World Tax Analyzer' tab")
    page.wait_for_timeout(1000)
    case.step(3, "Verify still within WTA")
    ok = "/wta/" in page.url
    case.check("URL remains within /wta/ after clicking the already-active tab", ok,
               expected="/wta/*", actual=page.url)
    actual = (f"Clicking the already-active 'World Tax Analyzer' tab correctly kept the user "
              f"within WTA, at {page.url}." if ok else
              f"Clicking 'World Tax Analyzer' unexpectedly navigated outside WTA, to {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_landing_42_information_nav_link_href(page, result):
    case = Case(
        page, "LANDING_42", FEATURE, "'Information' nav link points to /wta/Information",
        description="The 'Information' nav link's href must point to /wta/Information, "
                     "consistent with it being the post-login landing page.",
        precondition="User is logged in and on the landing page.",
        test_data="-",
        steps="1. Log in\n2. Verify the 'Information' nav link's href",
    )
    _login(case, page)
    landing = LandingPage(page)
    case.step(2, "Verify the 'Information' nav link href")
    case.verify_visible(landing.nav_information, "'Information' nav link")
    href = landing.nav_information.get_attribute("href")
    ok = bool(href) and "/wta/Information" in href
    case.check("'Information' nav link href contains /wta/Information", ok,
               expected="contains /wta/Information", actual=href,
               locator=landing.nav_information)
    actual = (f"'Information' nav link correctly points to {href}." if ok else
              f"'Information' nav link href was unexpected: {href!r}.")
    result(case, actual, ok)
    assert ok, actual
