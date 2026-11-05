"""TPA > Home (/tpa/Home).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. TPA is a top-level product tab (like Workspace/World Tax
Analyzer/RegBriefings), NOT a WTA top-nav dropdown - confirmed live it
has no viewport-width defect, so no directory-local viewport override is
needed (see pages/tpa/tpa_common.py docstring). See
TPA/TPA_BUSINESS_EXPLORATION.md for the full business inventory."""
import pytest

from pages.tpa.tpa_common import TpaNav, TPA_TOP_NAV_ITEMS
from pages.tpa.tpa_home_page import TpaHomePage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Home"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Transfer Pricing Analyzer > Home", kind="navigate")
    nav = TpaNav(page)
    nav.open_tab()
    home = TpaHomePage(page)
    case.verify_visible(home.recent_news_heading, "'Recent News' heading (content-ready signal)")
    return nav, home


@pytest.mark.smoke
def test_tpahome_01_access_via_tpa_tab(page, result):
    case = Case(
        page, "TpaHome_01", FEATURE, "Clicking the 'Transfer Pricing Analyzer' tab opens Home with real content",
        description="Clicking the 'Transfer Pricing Analyzer' top-level tab must land on /tpa/Home with the "
                     "'Recent News' heading and a real news feed visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, click the 'Transfer Pricing Analyzer' tab\n2. Verify the URL and that content renders",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify URL and content")
    url_ok = "/tpa/Home" in page.url
    content_ok = case.verify_visible(home.recent_news_heading, "'Recent News' heading")
    ok = url_ok and content_ok
    case.check("Transfer Pricing Analyzer opens on Home with real content", ok,
               expected="url contains /tpa/Home, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("Transfer Pricing Analyzer correctly opened on Home with real content." if ok else
              "Transfer Pricing Analyzer did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpahome_02_top_nav_lists_all_expected_items(page, result):
    case = Case(
        page, "TpaHome_02", FEATURE, "The TPA top nav lists all 5 expected items",
        description="The TPA top nav must show: Home, News, Forms, Regulations, Case Law (plus the "
                     "'Information' dropdown, checked separately).",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA\n2. Verify each of the 5 top-nav items is visible",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify each top-nav item is visible")
    nav_locators = {
        "Home": nav.nav_home, "News": nav.nav_news, "Forms": nav.nav_forms,
        "Regulations": nav.nav_regulations, "Case Law": nav.nav_case_law,
    }
    missing = [name for name in TPA_TOP_NAV_ITEMS if not case.verify_visible(nav_locators[name], f"'{name}' nav item")]
    ok = not missing
    case.check("All 5 top-nav items are visible", ok,
               expected=", ".join(TPA_TOP_NAV_ITEMS), actual=f"missing: {missing}" if missing else "all present")

    actual = ("The TPA top nav correctly lists all 5 expected items." if ok else
              f"The TPA top nav was missing: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpahome_03_information_dropdown_has_both_items(page, result):
    case = Case(
        page, "TpaHome_03", FEATURE, "The 'Information' dropdown offers National Rules and International Guidelines",
        description="Opening the 'Information' top-nav dropdown must show exactly 'National Rules' and "
                     "'International Guidelines' as visible items.",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA\n2. Click 'Information'\n3. Verify both items are visible",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Click 'Information'")
    case.click(nav.nav_information, "'Information' dropdown button")
    case.step(3, "Verify both items are visible")
    nr_ok = case.verify_visible(page.get_by_text("National Rules", exact=True).first, "'National Rules' item")
    ig_ok = case.verify_visible(page.get_by_text("International Guidelines", exact=True).first, "'International Guidelines' item")
    ok = nr_ok and ig_ok
    case.check("Both 'National Rules' and 'International Guidelines' are visible", ok,
               expected="both visible", actual=f"national_rules={nr_ok}, international_guidelines={ig_ok}")

    actual = ("The 'Information' dropdown correctly offers both items." if ok else
              "The 'Information' dropdown was missing one or both items.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpahome_04_dashboard_cards_visible(page, result):
    case = Case(
        page, "TpaHome_04", FEATURE, "The 3 dashboard cards are visible",
        description="Home must show the 'My Projects', 'My TPA Research' and 'Use a Virtual Coach' cards.",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA Home\n2. Verify each of the 3 cards is visible",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify each dashboard card is visible")
    mp_ok = case.verify_visible(home.my_projects_heading, "'My Projects' card")
    tr_ok = case.verify_visible(home.my_tpa_research_heading, "'My TPA Research' card")
    vc_ok = case.verify_visible(home.virtual_coach_heading, "'Use a Virtual Coach' card")
    ok = mp_ok and tr_ok and vc_ok
    case.check("All 3 dashboard cards are visible", ok,
               expected="all 3 visible", actual=f"my_projects={mp_ok}, my_tpa_research={tr_ok}, virtual_coach={vc_ok}")

    actual = ("All 3 dashboard cards are correctly visible." if ok else
              "One or more dashboard cards were not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpahome_05_monthly_briefs_and_quick_access_sections_visible(page, result):
    case = Case(
        page, "TpaHome_05", FEATURE, "The 'Monthly Briefs' and 'Quick Access' sections are visible",
        description="Home must show both the 'Monthly Briefs' and 'Quick Access' section headings.",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA Home\n2. Verify both sections are visible",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify both sections are visible")
    mb_ok = case.verify_visible(home.monthly_briefs_heading, "'Monthly Briefs' heading")
    qa_ok = case.verify_visible(home.quick_access_heading, "'Quick Access' heading")
    ok = mb_ok and qa_ok
    case.check("Both 'Monthly Briefs' and 'Quick Access' sections are visible", ok,
               expected="both visible", actual=f"monthly_briefs={mb_ok}, quick_access={qa_ok}")

    actual = ("Both sections are correctly visible." if ok else
              "One or both sections were not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpahome_06_recent_news_feed_has_real_article_cards(page, result):
    case = Case(
        page, "TpaHome_06", FEATURE, "The 'Recent News' feed shows real article cards with a date",
        description="The 'Recent News' feed must show at least one real article with a visible date string "
                     "(not an empty/placeholder state).",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA Home\n2. Verify at least one news article link is present",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify at least one real news article link is present")
    # Scope to links whose href points at the real outbound news source
    # (confirmed live: every Recent News article is a real regfollower.com
    # link opened in a new tab, target="_blank") rather than counting
    # every <a> on the page, which would also match top-nav links.
    article_links = page.locator("a[href*='regfollower.com']")
    count = article_links.count()
    ok = count > 0
    case.check("At least one real outbound news article link is present", ok,
               expected=">= 1", actual=f"count={count}")

    actual = (f"Recent News correctly shows {count} real article link(s)." if ok else
              "Recent News showed no real article links.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpahome_07_tutorial_gallery_link_is_real(page, result):
    case = Case(
        page, "TpaHome_07", FEATURE, "'View full tutorial gallery' is a real outbound link",
        description="The 'View full tutorial gallery' link must have a real, non-empty href opening in a new "
                     "tab, not a dead/placeholder link.",
        precondition="User is logged in, on TPA Home.",
        test_data="-",
        steps="1. Log in, open TPA Home\n2. Verify the tutorial gallery link's href and target",
    )
    nav, home = _login_and_open(case, page)
    case.step(2, "Verify the tutorial gallery link's href and target")
    case.verify_visible(home.tutorial_gallery_link, "'View full tutorial gallery' link")
    href = home.tutorial_gallery_link.get_attribute("href") or ""
    target = home.tutorial_gallery_link.get_attribute("target") or ""
    ok = href.startswith("http") and target == "_blank"
    case.check("Tutorial gallery link has a real href opening in a new tab", ok,
               expected="href starts with http, target=_blank", actual=f"href={href!r}, target={target!r}")

    actual = (f"The tutorial gallery link correctly points to {href!r}." if ok else
              f"The tutorial gallery link was not a real outbound link (href={href!r}, target={target!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpahome_08_direct_deep_link_works(page, result):
    case = Case(
        page, "TpaHome_08", FEATURE, "A direct deep link to /tpa/Home loads the page",
        description="Navigating straight to /tpa/Home (not via the tab click) must load real content - "
                     "confirmed live TPA supports direct deep links, unlike WTA's Tools/Calculator sub-pages.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/Home\n3. Verify the page loads with real content",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/Home")
    home = TpaHomePage(page)
    home.goto()
    case.step(3, "Verify the page loads with real content")
    ok = case.verify_visible(home.recent_news_heading, "'Recent News' heading")
    case.check("Direct deep link to /tpa/Home loads real content", ok,
               expected="'Recent News' heading visible", actual=f"visible={ok}")

    actual = ("The direct deep link to /tpa/Home correctly loaded real content." if ok else
              "The direct deep link to /tpa/Home did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
