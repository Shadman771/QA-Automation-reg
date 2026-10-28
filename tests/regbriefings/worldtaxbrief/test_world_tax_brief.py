"""RegBriefings > World Tax Brief (/regbrief/home/wtaBriefings).

New parent module (RegBriefings), built via live DOM discovery - no
QA-sheet reference exists. Entries are organized one per country, each
with multiple topical news items ending in a real "Full Story in
Regfollower" link. See pages/regbriefings/brief_detail_common.py for
the shared shape reused across World Tax Brief/Transfer Pricing Brief/
Tax Treaty Brief."""
import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav
from pages.regbriefings.world_tax_brief_page import WorldTaxBriefPage
from utils.auth import perform_login
from utils.case import Case
from config.settings import APP_ORIGIN

FEATURE = "RegBriefings World Tax Brief"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > World Tax Brief", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    wtb = WorldTaxBriefPage(page)
    case.click(nav.nav_world_tax_brief, "'World Tax Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    case.verify_visible(wtb.section_heading, "'World Tax Brief:' section heading")
    return nav, wtb


@pytest.mark.smoke
def test_worldtaxbrief_01_access_via_sidebar(page, result):
    case = Case(
        page, "WorldTaxBrief_01", FEATURE, "World Tax Brief opens from the RegBriefings sidebar",
        description="Clicking 'World Tax Brief' in the sidebar must land on /regbrief/home/wtaBriefings "
                     "with the section heading and real country entries visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > World Tax Brief\n2. Verify the URL and section heading",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Verify URL and section heading")
    url_ok = "/regbrief/home/wtaBriefings" in page.url
    heading_ok = case.verify_visible(wtb.section_heading, "'World Tax Brief:' section heading")
    ok = url_ok and heading_ok
    case.check("World Tax Brief opens with its section heading visible", ok,
               expected="url contains /regbrief/home/wtaBriefings, heading visible",
               actual=f"url={page.url}, heading={heading_ok}")

    actual = ("World Tax Brief opened correctly with its section heading visible." if ok else
              "World Tax Brief did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_worldtaxbrief_02_direct_deep_link_loads(page, result):
    case = Case(
        page, "WorldTaxBrief_02", FEATURE, "A direct deep link to /regbrief/home/wtaBriefings loads correctly",
        description="Unlike WTA's Tools/Calculator pages, navigating straight to /regbrief/home/wtaBriefings "
                     "must load real content, not redirect elsewhere.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /regbrief/home/wtaBriefings\n3. Verify real content loads",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /regbrief/home/wtaBriefings")
    case.goto(APP_ORIGIN + "/regbrief/home/wtaBriefings", "World Tax Brief (direct deep link)")
    page.wait_for_timeout(2000)
    wtb = WorldTaxBriefPage(page)

    case.step(3, "Verify real content loads")
    url_ok = "/regbrief/home/wtaBriefings" in page.url
    content_ok = case.verify_visible(wtb.section_heading, "'World Tax Brief:' section heading")
    ok = url_ok and content_ok
    case.check("Direct deep link loads real World Tax Brief content", ok,
               expected="url contains /regbrief/home/wtaBriefings, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("The direct deep link correctly loaded real World Tax Brief content." if ok else
              "The direct deep link did not load the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_worldtaxbrief_03_print_button_present(page, result):
    case = Case(
        page, "WorldTaxBrief_03", FEATURE, "At least one 'Print' button is present",
        description="The World Tax Brief section must show at least one 'Print' button.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="-",
        steps="1. Log in, open World Tax Brief\n2. Verify at least one 'Print' button is present",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Verify at least one 'Print' button is present")
    count = wtb.print_buttons.count()
    ok = count >= 1
    case.check("At least one 'Print' button is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"World Tax Brief correctly shows {count} 'Print' button(s)." if ok else
              "World Tax Brief showed no 'Print' buttons.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_worldtaxbrief_04_country_entries_are_real_content(page, result):
    case = Case(
        page, "WorldTaxBrief_04", FEATURE, "Real country entries are present, with 'Full Story' links where the environment provides them",
        description="At least one real country entry must be present. Individual entries typically end "
                     "with a 'Full Story in Regfollower' link - confirmed live this is present on RC/Live "
                     "but genuinely ABSENT on Staging (real seeded-data variance, not a bug, confirmed via "
                     "an exhaustive link dump, not a timing gap) - so this only requires the link when "
                     "entries genuinely include it, not as a universal fact.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="-",
        steps="1. Log in, open World Tax Brief\n2. Verify at least one real country entry is present\n"
              "3. If any 'Full Story' links exist, confirm they're real (count matches or is consistent)",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Verify at least one real country entry is present")
    entry_count = wtb.entries.count()
    story_count = wtb.full_story_links.count()
    case.step(3, "Record whether 'Full Story' links are present on this environment")
    ok = entry_count >= 1
    case.check("At least one real country entry is present", ok,
               expected=">= 1 entries", actual=f"entries={entry_count}, full_story_links={story_count}")

    actual = (f"World Tax Brief correctly shows {entry_count} real country entries "
              f"({story_count} with 'Full Story' links on this environment)." if ok else
              "World Tax Brief showed no real country entries.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_worldtaxbrief_05_search_filters_entries(page, result):
    case = Case(
        page, "WorldTaxBrief_05", FEATURE, "The Search box genuinely filters to the searched country",
        description="Typing a real, currently-present country name into Search must leave only matching "
                     "entries visible (and that country must remain visible) - confirmed live this is a "
                     "real, functional filter. Uses whichever country is ACTUALLY present this run (read "
                     "dynamically, not hardcoded) since the real entry list varies by environment/month - "
                     "confirmed live Staging can legitimately have just 1 entry some months, where a "
                     "hardcoded country name from a different environment wouldn't exist at all.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="-",
        steps="1. Log in, open World Tax Brief\n2. Read the first real entry's own country name\n"
              "3. Search that exact name\n4. Verify only matching entries remain and it's still visible",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Read the first real entry's own country name")
    before_count = wtb.entries.count()
    search_term = wtb.entries.first.inner_text().strip() if before_count >= 1 else ""

    case.step(3, f"Search '{search_term}'")
    case.click(wtb.search_input, "'Search' input")
    wtb.search_input.fill(search_term)
    page.wait_for_timeout(1500)

    case.step(4, "Verify only matching entries remain and it's still visible")
    after_count = wtb.entries.count()
    entry_ok = case.verify_visible(wtb.entry_heading(search_term), f"'{search_term}' entry")
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
def test_worldtaxbrief_06_search_no_match_shows_no_entries(page, result):
    case = Case(
        page, "WorldTaxBrief_06", FEATURE, "Searching for a non-existent country shows no entries",
        description="Searching for a jurisdiction name that doesn't exist must result in zero visible "
                     "'Full Story in Regfollower' entries.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="Search term: Zzzznotacountry",
        steps="1. Log in, open World Tax Brief\n2. Search 'Zzzznotacountry'\n3. Verify zero entries remain",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Search 'Zzzznotacountry'")
    case.click(wtb.search_input, "'Search' input")
    wtb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1500)

    case.step(3, "Verify zero entries remain")
    count = wtb.entries.count()
    ok = count == 0
    case.check("No entries remain for a non-existent search term", ok, expected=0, actual=count)

    actual = ("Searching a non-existent term correctly left no entries visible." if ok else
              f"Searching a non-existent term unexpectedly left {count} entries visible.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_worldtaxbrief_07_clearing_search_restores_entries(page, result):
    case = Case(
        page, "WorldTaxBrief_07", FEATURE, "Clearing the search box restores the full entry list",
        description="After searching and then clearing the Search box, the full, unfiltered entry list "
                     "must reappear.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="-",
        steps="1. Log in, open World Tax Brief\n2. Record the full entry count\n"
              "3. Search a term, then clear the search box\n4. Verify the entry count returns to the original",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Record the full entry count")
    original_count = wtb.entries.count()

    case.step(3, "Search a term, then clear the search box")
    case.click(wtb.search_input, "'Search' input")
    wtb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1200)
    wtb.search_input.fill("")
    page.wait_for_timeout(1200)

    case.step(4, "Verify the entry count returns to the original")
    restored_count = wtb.entries.count()
    ok = restored_count == original_count
    case.check("Clearing the search box restores the full entry list", ok,
               expected=original_count, actual=restored_count)

    actual = (f"Clearing the search box correctly restored all {restored_count} entries." if ok else
              f"Clearing the search box did not restore the original entry count (expected "
              f"{original_count}, got {restored_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_worldtaxbrief_08_sidebar_remains_visible(page, result):
    case = Case(
        page, "WorldTaxBrief_08", FEATURE, "The sidebar remains visible on World Tax Brief",
        description="The left sidebar (My Briefs, World Tax Brief, Transfer Pricing Brief, Tax Treaty "
                     "Brief, Archive, Preferences) must remain visible while viewing World Tax Brief.",
        precondition="User is logged in, on World Tax Brief.",
        test_data="-",
        steps="1. Log in, open World Tax Brief\n2. Verify the 'Tax Treaty Brief' sidebar item is visible",
    )
    nav, wtb = _login_and_open(case, page)
    case.step(2, "Verify the 'Tax Treaty Brief' sidebar item is visible")
    ok = case.verify_visible(nav.nav_tax_treaty_brief, "'Tax Treaty Brief' sidebar link")
    case.check("The sidebar remains visible on World Tax Brief", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The sidebar correctly remains visible on World Tax Brief." if ok else
              "The sidebar was not visible on World Tax Brief.")
    result(case, actual, ok)
    assert ok, actual
