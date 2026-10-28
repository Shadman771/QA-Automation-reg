"""RegBriefings > My Briefs (/regbrief/home/myBriefings).

New parent module (RegBriefings), built via live DOM discovery
(scratchpad scripts, not part of the suite) - no reference QA sheet
exists for this module. RegBriefings is a top-level product tab (like
Workspace/World Tax Analyzer/Transfer Pricing Analyzer), NOT a WTA
top-nav dropdown - confirmed live it has no viewport-width defect, so no
directory-local viewport override is needed (see
pages/regbriefings/regbriefings_common.py docstring)."""
import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav, REGBRIEFINGS_NAV_ITEMS
from pages.regbriefings.my_briefs_page import MyBriefsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "RegBriefings My Briefs"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > My Briefs", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    mb = MyBriefsPage(page)
    # A fixed wait is not enough on a slow environment (confirmed live
    # elsewhere in this project, e.g. WTA's ASSERTION_TIMEOUT_MS writeup) -
    # wait for a guaranteed-present element instead. quick_access_heading
    # is account-Preferences-independent (always renders), unlike any one
    # specific brief-type section (see test_03's docstring - which
    # sections appear depends on the account's own Preferences selection).
    case.verify_visible(mb.quick_access_heading, "'Quick Access' heading (content-ready signal)")
    return nav, mb


@pytest.mark.smoke
def test_mybriefs_01_access_via_regbriefings_tab(page, result):
    case = Case(
        page, "MyBriefs_01", FEATURE, "RegBriefings opens on 'My Briefs' by default",
        description="Clicking the 'RegBriefings' top-level tab must land on /regbrief/home/myBriefings with "
                     "the 'My Briefs' sidebar item active.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, click the 'RegBriefings' tab\n2. Verify the URL and that content renders",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify URL and content")
    url_ok = "/regbrief/home/myBriefings" in page.url
    # quick_access_heading, not a specific brief-type heading - confirmed
    # live which brief-type sections appear depends on the account's own
    # Preferences subscription (see test_03), so it's not a reliable
    # "did real content load" signal across every account/environment.
    content_ok = case.verify_visible(mb.quick_access_heading, "'Quick Access' heading")
    ok = url_ok and content_ok
    case.check("RegBriefings opens on 'My Briefs' with real content", ok,
               expected="url contains /regbrief/home/myBriefings, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("RegBriefings correctly opened on 'My Briefs' with real content." if ok else
              "RegBriefings did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_mybriefs_02_sidebar_lists_all_six_nav_items(page, result):
    case = Case(
        page, "MyBriefs_02", FEATURE, "The sidebar lists all 6 expected navigation items",
        description="The RegBriefings left sidebar must show exactly: My Briefs, World Tax Brief, Transfer "
                     "Pricing Brief, Tax Treaty Brief, Archive, Preferences.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify each of the 6 sidebar items is visible",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify each sidebar item is visible")
    missing = [name for name in REGBRIEFINGS_NAV_ITEMS if not case.verify_visible(nav.nav_item(name), f"'{name}' sidebar link")]
    ok = not missing
    case.check("All 6 sidebar items are visible", ok,
               expected=", ".join(REGBRIEFINGS_NAV_ITEMS), actual=f"missing: {missing}" if missing else "all present")

    actual = ("The sidebar correctly lists all 6 expected navigation items." if ok else
              f"The sidebar was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_mybriefs_03_aggregated_sections_match_preferences_subscription(page, result):
    case = Case(
        page, "MyBriefs_03", FEATURE, "My Briefs shows exactly the brief-type sections the account subscribes to",
        description="My Briefs aggregates one section per brief type the account has subscribed to via "
                     "Preferences (World Tax Brief/Transfer Pricing Brief/Tax Treaty Brief) - confirmed "
                     "live this is account-specific, NOT always all 3 (e.g. one real account subscribes "
                     "only to Tax Treaty Brief, so My Briefs shows only that one section). This test reads "
                     "the real Preferences checkbox state first, then verifies My Briefs shows exactly "
                     "those sections - not hardcoding a fixed count.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n2. Read which brief types are checked\n"
              "3. Open My Briefs\n4. Verify exactly the subscribed sections are visible",
    )
    perform_login(case, page)
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)

    case.step(2, "Read which brief types are checked in Preferences")
    case.click(nav.nav_preferences, "'Preferences' sidebar link")
    page.wait_for_timeout(1200)
    subscriptions = {}
    for label in ["World Tax Brief", "Transfer Pricing Brief", "Tax Treaty Brief"]:
        checkbox = page.get_by_text(label, exact=True).locator("xpath=preceding-sibling::input[@type='checkbox'][1]")
        subscriptions[label] = checkbox.is_checked()
    subscribed = [k for k, v in subscriptions.items() if v]

    # Preferences opens as an OVERLAY MODAL, not a route change (confirmed
    # live, see pages/regbriefings/regbriefings_common.py docstring) - it
    # must be closed (via Cancel, to avoid altering the real account's
    # settings) before any other sidebar item is clickable again.
    case.click(page.get_by_role("button", name="Cancel"), "'Cancel' button (closing Preferences overlay)")
    page.wait_for_timeout(500)

    case.step(3, "Open My Briefs")
    case.click(nav.nav_my_briefs, "'My Briefs' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    mb = MyBriefsPage(page)
    case.verify_visible(mb.quick_access_heading, "'Quick Access' heading")

    case.step(4, "Verify exactly the subscribed sections are visible")
    heading_map = {
        "World Tax Brief": mb.world_tax_brief_heading,
        "Transfer Pricing Brief": mb.transfer_pricing_brief_heading,
        "Tax Treaty Brief": mb.tax_treaty_brief_heading,
    }
    actual_visible = {label: heading_map[label].count() > 0 for label in heading_map}
    expected_visible = {label: label in subscribed for label in heading_map}
    ok = actual_visible == expected_visible and len(subscribed) >= 1
    case.check("My Briefs shows exactly the Preferences-subscribed sections", ok,
               expected=expected_visible, actual=actual_visible)

    actual = (f"My Briefs correctly shows exactly the subscribed sections: {subscribed}." if ok else
              f"My Briefs did not match the Preferences subscription (subscribed={subscribed}, "
              f"visible={actual_visible}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_04_each_brief_section_has_a_print_button(page, result):
    case = Case(
        page, "MyBriefs_04", FEATURE, "Each aggregated brief section has its own 'Print' button",
        description="There must be at least 1 'Print' button visible per aggregated brief-type section - "
                     "how many sections appear depends on the account's Preferences subscription (see "
                     "MyBriefs_03), so this checks '>= 1' rather than a fixed count.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify at least 1 'Print' button is present",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify at least 1 'Print' button is present")
    count = mb.print_buttons.count()
    ok = count >= 1
    case.check("At least 1 'Print' button is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"My Briefs correctly shows {count} 'Print' button(s)." if ok else
              "My Briefs showed no 'Print' buttons.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_05_news_items_have_full_story_links(page, result):
    case = Case(
        page, "MyBriefs_05", FEATURE, "News items include real 'Full Story in Regfollower' links",
        description="Individual news items within the aggregated brief sections must end with a real "
                     "'Full Story in Regfollower' link - confirmed live, not a placeholder.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify at least one 'Full Story in Regfollower' link is present",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify 'Full Story in Regfollower' links are present")
    count = mb.full_story_links.count()
    ok = count >= 1
    case.check("At least one 'Full Story in Regfollower' link is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"My Briefs correctly shows {count} 'Full Story in Regfollower' link(s)." if ok else
              "My Briefs showed no 'Full Story in Regfollower' links.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_mybriefs_06_quick_access_panel_present(page, result):
    case = Case(
        page, "MyBriefs_06", FEATURE, "The 'Quick Access' panel with 'Recent Briefs' is visible",
        description="The right-hand 'Quick Access' panel must show a 'Recent Briefs' heading with a 'See "
                     "All' link.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify 'Quick Access', 'Recent Briefs' and 'See All' are visible",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify the Quick Access panel elements")
    qa_ok = case.verify_visible(mb.quick_access_heading, "'Quick Access' heading")
    rb_ok = case.verify_visible(mb.recent_briefs_heading, "'Recent Briefs' heading")
    sa_ok = case.verify_visible(mb.see_all_link, "'See All' link")
    ok = qa_ok and rb_ok and sa_ok
    case.check("The Quick Access panel's elements are all visible", ok,
               expected="all 3 visible", actual=f"quick_access={qa_ok}, recent_briefs={rb_ok}, see_all={sa_ok}")

    actual = ("The 'Quick Access' panel is correctly visible with its expected elements." if ok else
              "The 'Quick Access' panel did not show the expected elements.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_07_news_related_to_interest_panel_present(page, result):
    case = Case(
        page, "MyBriefs_07", FEATURE, "The 'News related to your interest' panel is visible",
        description="The right-hand panel must also show a 'News related to your interest' section.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify the 'News related to your interest' heading is visible",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify the 'News related to your interest' heading")
    ok = case.verify_visible(mb.news_related_heading, "'News related to your interest' heading")
    case.check("'News related to your interest' panel is visible", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The 'News related to your interest' panel is correctly visible." if ok else
              "The 'News related to your interest' panel was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_08_search_input_present(page, result):
    case = Case(
        page, "MyBriefs_08", FEATURE, "A 'Search' input is present on My Briefs",
        description="The page must show a search input (placeholder 'Search') for filtering briefs.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Verify the Search input is visible",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Verify the Search input is visible")
    ok = case.verify_visible(nav.search_input, "'Search' input")
    case.check("The 'Search' input is visible", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The 'Search' input is correctly visible." if ok else "The 'Search' input was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_mybriefs_09_clicking_world_tax_brief_navigates(page, result):
    case = Case(
        page, "MyBriefs_09", FEATURE, "Clicking 'World Tax Brief' in the sidebar navigates to its own page",
        description="Clicking 'World Tax Brief' must navigate to /regbrief/home/wtaBriefings.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Click 'World Tax Brief'\n3. Verify the URL",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Click 'World Tax Brief'")
    case.click(nav.nav_world_tax_brief, "'World Tax Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the URL")
    ok = "/regbrief/home/wtaBriefings" in page.url
    case.check("URL contains /regbrief/home/wtaBriefings", ok,
               expected="/regbrief/home/wtaBriefings", actual=page.url)

    actual = (f"Clicking 'World Tax Brief' navigated to {page.url}." if ok else
              f"Clicking 'World Tax Brief' did not navigate as expected (got {page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_10_clicking_transfer_pricing_brief_navigates(page, result):
    case = Case(
        page, "MyBriefs_10", FEATURE, "Clicking 'Transfer Pricing Brief' in the sidebar navigates to its own page",
        description="Clicking 'Transfer Pricing Brief' must navigate to /regbrief/home/tpaBriefings.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Click 'Transfer Pricing Brief'\n3. Verify the URL",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Click 'Transfer Pricing Brief'")
    case.click(nav.nav_transfer_pricing_brief, "'Transfer Pricing Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the URL")
    ok = "/regbrief/home/tpaBriefings" in page.url
    case.check("URL contains /regbrief/home/tpaBriefings", ok,
               expected="/regbrief/home/tpaBriefings", actual=page.url)

    actual = (f"Clicking 'Transfer Pricing Brief' navigated to {page.url}." if ok else
              f"Clicking 'Transfer Pricing Brief' did not navigate as expected (got {page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_11_clicking_tax_treaty_brief_navigates(page, result):
    case = Case(
        page, "MyBriefs_11", FEATURE, "Clicking 'Tax Treaty Brief' in the sidebar navigates to its own page",
        description="Clicking 'Tax Treaty Brief' must navigate to /regbrief/home/taxTreaties.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Click 'Tax Treaty Brief'\n3. Verify the URL",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Click 'Tax Treaty Brief'")
    case.click(nav.nav_tax_treaty_brief, "'Tax Treaty Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the URL")
    ok = "/regbrief/home/taxTreaties" in page.url
    case.check("URL contains /regbrief/home/taxTreaties", ok,
               expected="/regbrief/home/taxTreaties", actual=page.url)

    actual = (f"Clicking 'Tax Treaty Brief' navigated to {page.url}." if ok else
              f"Clicking 'Tax Treaty Brief' did not navigate as expected (got {page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_12_clicking_archive_navigates(page, result):
    case = Case(
        page, "MyBriefs_12", FEATURE, "Clicking 'Archive' in the sidebar navigates to its own page",
        description="Clicking 'Archive' must navigate to /regbrief/pastBriefingYearly.",
        precondition="User is logged in, on My Briefs.",
        test_data="-",
        steps="1. Log in, open RegBriefings\n2. Click 'Archive'\n3. Verify the URL",
    )
    nav, mb = _login_and_open(case, page)
    case.step(2, "Click 'Archive'")
    case.click(nav.nav_archive, "'Archive' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the URL")
    ok = "/regbrief/pastBriefingYearly" in page.url
    case.check("URL contains /regbrief/pastBriefingYearly", ok,
               expected="/regbrief/pastBriefingYearly", actual=page.url)

    actual = (f"Clicking 'Archive' navigated to {page.url}." if ok else
              f"Clicking 'Archive' did not navigate as expected (got {page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mybriefs_13_direct_deep_link_loads_my_briefs(page, result):
    case = Case(
        page, "MyBriefs_13", FEATURE, "A direct deep link to /regbrief/home/myBriefings loads correctly",
        description="Unlike WTA's Tools/Calculator pages, RegBriefings pages support a direct full-page "
                     "deep link (confirmed live) - navigating straight to /regbrief/home/myBriefings must "
                     "load real content, not redirect elsewhere.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /regbrief/home/myBriefings\n3. Verify real content loads",
    )
    perform_login(case, page)
    from config.settings import APP_ORIGIN
    case.step(2, "Navigate directly to /regbrief/home/myBriefings")
    case.goto(APP_ORIGIN + "/regbrief/home/myBriefings", "My Briefs (direct deep link)")
    page.wait_for_timeout(2000)
    mb = MyBriefsPage(page)

    case.step(3, "Verify real content loads")
    url_ok = "/regbrief/home/myBriefings" in page.url
    content_ok = case.verify_visible(mb.quick_access_heading, "'Quick Access' heading")
    ok = url_ok and content_ok
    case.check("Direct deep link loads real My Briefs content", ok,
               expected="url contains /regbrief/home/myBriefings, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("The direct deep link correctly loaded real My Briefs content." if ok else
              "The direct deep link did not load the expected content.")
    result(case, actual, ok)
    assert ok, actual
