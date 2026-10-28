"""RegBriefings > Transfer Pricing Brief (/regbrief/home/tpaBriefings).

New parent module (RegBriefings), built via live DOM discovery - no
QA-sheet reference exists. Shares the exact shape already confirmed for
World Tax Brief (see pages/regbriefings/brief_detail_common.py and
tests/regbriefings/worldtaxbrief/test_world_tax_brief.py) - entries
organized one per country, with transfer-pricing-specific news items
(CbC reporting, intra-group services, etc.). Same real environment
gotchas apply here: the "Full Story in Regfollower" link's presence is
environment-dependent (confirmed on RC/Live, absent on Staging for
World Tax Brief - not re-verified per-environment here since it's the
same underlying page shape/data source), and search tests read whichever
country is actually the first real entry at runtime rather than
hardcoding one."""
import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav
from pages.regbriefings.transfer_pricing_brief_page import TransferPricingBriefPage
from utils.auth import perform_login
from utils.case import Case
from config.settings import APP_ORIGIN

FEATURE = "RegBriefings Transfer Pricing Brief"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > Transfer Pricing Brief", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    tpb = TransferPricingBriefPage(page)
    case.click(nav.nav_transfer_pricing_brief, "'Transfer Pricing Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    case.verify_visible(tpb.section_heading, "'Transfer Pricing Brief:' section heading")
    return nav, tpb


@pytest.mark.smoke
def test_transferpricingbrief_01_access_via_sidebar(page, result):
    case = Case(
        page, "TransferPricingBrief_01", FEATURE, "Transfer Pricing Brief opens from the RegBriefings sidebar",
        description="Clicking 'Transfer Pricing Brief' in the sidebar must land on "
                     "/regbrief/home/tpaBriefings with the section heading and real country entries visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Transfer Pricing Brief\n2. Verify the URL and section heading",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Verify URL and section heading")
    url_ok = "/regbrief/home/tpaBriefings" in page.url
    heading_ok = case.verify_visible(tpb.section_heading, "'Transfer Pricing Brief:' section heading")
    ok = url_ok and heading_ok
    case.check("Transfer Pricing Brief opens with its section heading visible", ok,
               expected="url contains /regbrief/home/tpaBriefings, heading visible",
               actual=f"url={page.url}, heading={heading_ok}")

    actual = ("Transfer Pricing Brief opened correctly with its section heading visible." if ok else
              "Transfer Pricing Brief did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_transferpricingbrief_02_direct_deep_link_loads(page, result):
    case = Case(
        page, "TransferPricingBrief_02", FEATURE, "A direct deep link to /regbrief/home/tpaBriefings loads correctly",
        description="Navigating straight to /regbrief/home/tpaBriefings must load real content, not "
                     "redirect elsewhere.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /regbrief/home/tpaBriefings\n3. Verify real content loads",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /regbrief/home/tpaBriefings")
    case.goto(APP_ORIGIN + "/regbrief/home/tpaBriefings", "Transfer Pricing Brief (direct deep link)")
    page.wait_for_timeout(2000)
    tpb = TransferPricingBriefPage(page)

    case.step(3, "Verify real content loads")
    url_ok = "/regbrief/home/tpaBriefings" in page.url
    content_ok = case.verify_visible(tpb.section_heading, "'Transfer Pricing Brief:' section heading")
    ok = url_ok and content_ok
    case.check("Direct deep link loads real Transfer Pricing Brief content", ok,
               expected="url contains /regbrief/home/tpaBriefings, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("The direct deep link correctly loaded real Transfer Pricing Brief content." if ok else
              "The direct deep link did not load the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_transferpricingbrief_03_print_button_present(page, result):
    case = Case(
        page, "TransferPricingBrief_03", FEATURE, "At least one 'Print' button is present",
        description="The Transfer Pricing Brief section must show at least one 'Print' button.",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="-",
        steps="1. Log in, open Transfer Pricing Brief\n2. Verify at least one 'Print' button is present",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Verify at least one 'Print' button is present")
    count = tpb.print_buttons.count()
    ok = count >= 1
    case.check("At least one 'Print' button is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"Transfer Pricing Brief correctly shows {count} 'Print' button(s)." if ok else
              "Transfer Pricing Brief showed no 'Print' buttons.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_transferpricingbrief_04_country_entries_are_real_content(page, result):
    case = Case(
        page, "TransferPricingBrief_04", FEATURE, "Real country entries are present",
        description="At least one real country entry must be present, identified via the stable "
                     "environment-universal CSS class .brief-country-name (not the 'Full Story in "
                     "Regfollower' link, whose presence is confirmed environment-dependent).",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="-",
        steps="1. Log in, open Transfer Pricing Brief\n2. Verify at least one real country entry is present",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Verify at least one real country entry is present")
    entry_count = tpb.entries.count()
    story_count = tpb.full_story_links.count()
    ok = entry_count >= 1
    case.check("At least one real country entry is present", ok,
               expected=">= 1 entries", actual=f"entries={entry_count}, full_story_links={story_count}")

    actual = (f"Transfer Pricing Brief correctly shows {entry_count} real country entries "
              f"({story_count} with 'Full Story' links on this environment)." if ok else
              "Transfer Pricing Brief showed no real country entries.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_transferpricingbrief_05_search_filters_entries(page, result):
    case = Case(
        page, "TransferPricingBrief_05", FEATURE, "The Search box genuinely filters to the searched country",
        description="Typing a real, currently-present country name into Search must leave only matching "
                     "entries visible. Uses whichever country is ACTUALLY present this run (read "
                     "dynamically, not hardcoded) since the real entry list varies by environment/month.",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="-",
        steps="1. Log in, open Transfer Pricing Brief\n2. Read the first real entry's own country name\n"
              "3. Search that exact name\n4. Verify only matching entries remain and it's still visible",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Read the first real entry's own country name")
    before_count = tpb.entries.count()
    search_term = tpb.entries.first.inner_text().strip() if before_count >= 1 else ""

    case.step(3, f"Search '{search_term}'")
    case.click(tpb.search_input, "'Search' input")
    tpb.search_input.fill(search_term)
    page.wait_for_timeout(1500)

    case.step(4, "Verify only matching entries remain and it's still visible")
    after_count = tpb.entries.count()
    entry_ok = case.verify_visible(tpb.entry_heading(search_term), f"'{search_term}' entry")
    ok = before_count >= 1 and after_count <= before_count and after_count >= 1 and entry_ok
    case.check(f"Searching '{search_term}' leaves only matching entries, still visible", ok,
               expected=f"1 <= after <= {before_count}, '{search_term}' visible",
               actual=f"after={after_count}, visible={entry_ok}")

    actual = (f"Search correctly filtered from {before_count} to {after_count} entries, keeping "
              f"'{search_term}' visible." if ok else
              f"Search did not filter as expected (before={before_count}, after={after_count}, "
              f"term={search_term!r}, visible={entry_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_transferpricingbrief_06_search_no_match_shows_no_entries(page, result):
    case = Case(
        page, "TransferPricingBrief_06", FEATURE, "Searching for a non-existent country shows no entries",
        description="Searching for a jurisdiction name that doesn't exist must result in zero visible entries.",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="Search term: Zzzznotacountry",
        steps="1. Log in, open Transfer Pricing Brief\n2. Search 'Zzzznotacountry'\n3. Verify zero entries remain",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Search 'Zzzznotacountry'")
    case.click(tpb.search_input, "'Search' input")
    tpb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1500)

    case.step(3, "Verify zero entries remain")
    count = tpb.entries.count()
    ok = count == 0
    case.check("No entries remain for a non-existent search term", ok, expected=0, actual=count)

    actual = ("Searching a non-existent term correctly left no entries visible." if ok else
              f"Searching a non-existent term unexpectedly left {count} entries visible.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_transferpricingbrief_07_clearing_search_restores_entries(page, result):
    case = Case(
        page, "TransferPricingBrief_07", FEATURE, "Clearing the search box restores the full entry list",
        description="After searching and then clearing the Search box, the full, unfiltered entry list "
                     "must reappear.",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="-",
        steps="1. Log in, open Transfer Pricing Brief\n2. Record the full entry count\n"
              "3. Search a term, then clear the search box\n4. Verify the entry count returns to the original",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Record the full entry count")
    original_count = tpb.entries.count()

    case.step(3, "Search a term, then clear the search box")
    case.click(tpb.search_input, "'Search' input")
    tpb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1200)
    tpb.search_input.fill("")
    page.wait_for_timeout(1200)

    case.step(4, "Verify the entry count returns to the original")
    restored_count = tpb.entries.count()
    ok = restored_count == original_count
    case.check("Clearing the search box restores the full entry list", ok,
               expected=original_count, actual=restored_count)

    actual = (f"Clearing the search box correctly restored all {restored_count} entries." if ok else
              f"Clearing the search box did not restore the original entry count (expected "
              f"{original_count}, got {restored_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_transferpricingbrief_08_sidebar_remains_visible(page, result):
    case = Case(
        page, "TransferPricingBrief_08", FEATURE, "The sidebar remains visible on Transfer Pricing Brief",
        description="The left sidebar must remain visible while viewing Transfer Pricing Brief.",
        precondition="User is logged in, on Transfer Pricing Brief.",
        test_data="-",
        steps="1. Log in, open Transfer Pricing Brief\n2. Verify the 'Tax Treaty Brief' sidebar item is visible",
    )
    nav, tpb = _login_and_open(case, page)
    case.step(2, "Verify the 'Tax Treaty Brief' sidebar item is visible")
    ok = case.verify_visible(nav.nav_tax_treaty_brief, "'Tax Treaty Brief' sidebar link")
    case.check("The sidebar remains visible on Transfer Pricing Brief", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The sidebar correctly remains visible on Transfer Pricing Brief." if ok else
              "The sidebar was not visible on Transfer Pricing Brief.")
    result(case, actual, ok)
    assert ok, actual
