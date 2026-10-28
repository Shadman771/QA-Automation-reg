"""RegBriefings > Tax Treaty Brief (/regbrief/home/taxTreaties).

New parent module (RegBriefings), built via live DOM discovery - no
QA-sheet reference exists. Shares the shape confirmed for World Tax
Brief/Transfer Pricing Brief (see
pages/regbriefings/brief_detail_common.py) with one real difference:
entries are organized one per COUNTRY PAIR (e.g. "Armenia and Japan"),
not a single country - confirmed live the DOM shape (including the
`.brief-country-name` class used for entry counting) is otherwise
identical, and searching by just the first country in a pair (e.g.
"Armenia") correctly filters to that pair, same as searching the full
pair text."""
import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav
from pages.regbriefings.tax_treaty_brief_page import TaxTreatyBriefPage
from utils.auth import perform_login
from utils.case import Case
from config.settings import APP_ORIGIN

FEATURE = "RegBriefings Tax Treaty Brief"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > Tax Treaty Brief", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    ttb = TaxTreatyBriefPage(page)
    case.click(nav.nav_tax_treaty_brief, "'Tax Treaty Brief' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    case.verify_visible(ttb.section_heading, "'Tax Treaty Brief:' section heading")
    return nav, ttb


@pytest.mark.smoke
def test_taxtreatybrief_01_access_via_sidebar(page, result):
    case = Case(
        page, "TaxTreatyBrief_01", FEATURE, "Tax Treaty Brief opens from the RegBriefings sidebar",
        description="Clicking 'Tax Treaty Brief' in the sidebar must land on /regbrief/home/taxTreaties "
                     "with the section heading and real country-pair entries visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Tax Treaty Brief\n2. Verify the URL and section heading",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Verify URL and section heading")
    url_ok = "/regbrief/home/taxTreaties" in page.url
    heading_ok = case.verify_visible(ttb.section_heading, "'Tax Treaty Brief:' section heading")
    ok = url_ok and heading_ok
    case.check("Tax Treaty Brief opens with its section heading visible", ok,
               expected="url contains /regbrief/home/taxTreaties, heading visible",
               actual=f"url={page.url}, heading={heading_ok}")

    actual = ("Tax Treaty Brief opened correctly with its section heading visible." if ok else
              "Tax Treaty Brief did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_taxtreatybrief_02_direct_deep_link_loads(page, result):
    case = Case(
        page, "TaxTreatyBrief_02", FEATURE, "A direct deep link to /regbrief/home/taxTreaties loads correctly",
        description="Navigating straight to /regbrief/home/taxTreaties must load real content, not "
                     "redirect elsewhere.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /regbrief/home/taxTreaties\n3. Verify real content loads",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /regbrief/home/taxTreaties")
    case.goto(APP_ORIGIN + "/regbrief/home/taxTreaties", "Tax Treaty Brief (direct deep link)")
    page.wait_for_timeout(2000)
    ttb = TaxTreatyBriefPage(page)

    case.step(3, "Verify real content loads")
    url_ok = "/regbrief/home/taxTreaties" in page.url
    content_ok = case.verify_visible(ttb.section_heading, "'Tax Treaty Brief:' section heading")
    ok = url_ok and content_ok
    case.check("Direct deep link loads real Tax Treaty Brief content", ok,
               expected="url contains /regbrief/home/taxTreaties, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("The direct deep link correctly loaded real Tax Treaty Brief content." if ok else
              "The direct deep link did not load the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_taxtreatybrief_03_print_button_present(page, result):
    case = Case(
        page, "TaxTreatyBrief_03", FEATURE, "At least one 'Print' button is present",
        description="The Tax Treaty Brief section must show at least one 'Print' button.",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="-",
        steps="1. Log in, open Tax Treaty Brief\n2. Verify at least one 'Print' button is present",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Verify at least one 'Print' button is present")
    count = ttb.print_buttons.count()
    ok = count >= 1
    case.check("At least one 'Print' button is present", ok, expected=">= 1", actual=f"count={count}")

    actual = (f"Tax Treaty Brief correctly shows {count} 'Print' button(s)." if ok else
              "Tax Treaty Brief showed no 'Print' buttons.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_taxtreatybrief_04_country_pair_entries_are_real_content(page, result):
    case = Case(
        page, "TaxTreatyBrief_04", FEATURE, "Real country-pair entries are present",
        description="At least one real country-pair entry (e.g. 'Armenia and Japan') must be present, "
                     "identified via the stable environment-universal CSS class .brief-country-name - "
                     "confirmed live this is the same entry shape as World Tax Brief/Transfer Pricing "
                     "Brief, just with a country-pair name instead of a single country.",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="-",
        steps="1. Log in, open Tax Treaty Brief\n2. Verify at least one real country-pair entry is present",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Verify at least one real country-pair entry is present")
    entry_count = ttb.entries.count()
    story_count = ttb.full_story_links.count()
    ok = entry_count >= 1
    case.check("At least one real country-pair entry is present", ok,
               expected=">= 1 entries", actual=f"entries={entry_count}, full_story_links={story_count}")

    actual = (f"Tax Treaty Brief correctly shows {entry_count} real country-pair entries "
              f"({story_count} with 'Full Story' links on this environment)." if ok else
              "Tax Treaty Brief showed no real country-pair entries.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_taxtreatybrief_05_search_by_single_country_filters_pair_entries(page, result):
    case = Case(
        page, "TaxTreatyBrief_05", FEATURE, "Searching by one country in a pair filters to matching entries",
        description="Typing just the FIRST country's name from a real country-PAIR entry into Search "
                     "(e.g. 'Armenia' from 'Armenia and Japan') must leave only matching entries visible - "
                     "confirmed live this works the same way as searching the full pair text. Uses "
                     "whichever pair is ACTUALLY present this run (read dynamically, not hardcoded).",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="-",
        steps="1. Log in, open Tax Treaty Brief\n2. Read the first real entry's own country-pair name\n"
              "3. Search just its first country\n4. Verify only matching entries remain and it's still visible",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Read the first real entry's own country-pair name")
    before_count = ttb.entries.count()
    pair_text = ttb.entries.first.inner_text().strip() if before_count >= 1 else ""
    search_term = pair_text.split(" and ")[0] if " and " in pair_text else pair_text

    case.step(3, f"Search '{search_term}'")
    case.click(ttb.search_input, "'Search' input")
    ttb.search_input.fill(search_term)
    page.wait_for_timeout(1500)

    case.step(4, "Verify only matching entries remain and it's still visible")
    after_count = ttb.entries.count()
    entry_ok = case.verify_visible(ttb.entry_heading(pair_text), f"'{pair_text}' entry")
    ok = before_count >= 1 and after_count <= before_count and after_count >= 1 and entry_ok
    case.check(f"Searching '{search_term}' leaves only matching pair entries, still visible", ok,
               expected=f"1 <= after <= {before_count}, '{pair_text}' visible",
               actual=f"after={after_count}, visible={entry_ok}")

    actual = (f"Search correctly filtered from {before_count} to {after_count} entries, keeping "
              f"'{pair_text}' visible." if ok else
              f"Search did not filter as expected (before={before_count}, after={after_count}, "
              f"term={search_term!r}, visible={entry_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_taxtreatybrief_06_search_no_match_shows_no_entries(page, result):
    case = Case(
        page, "TaxTreatyBrief_06", FEATURE, "Searching for a non-existent country shows no entries",
        description="Searching for a jurisdiction name that doesn't exist must result in zero visible entries.",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="Search term: Zzzznotacountry",
        steps="1. Log in, open Tax Treaty Brief\n2. Search 'Zzzznotacountry'\n3. Verify zero entries remain",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Search 'Zzzznotacountry'")
    case.click(ttb.search_input, "'Search' input")
    ttb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1500)

    case.step(3, "Verify zero entries remain")
    count = ttb.entries.count()
    ok = count == 0
    case.check("No entries remain for a non-existent search term", ok, expected=0, actual=count)

    actual = ("Searching a non-existent term correctly left no entries visible." if ok else
              f"Searching a non-existent term unexpectedly left {count} entries visible.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_taxtreatybrief_07_clearing_search_restores_entries(page, result):
    case = Case(
        page, "TaxTreatyBrief_07", FEATURE, "Clearing the search box restores the full entry list",
        description="After searching and then clearing the Search box, the full, unfiltered entry list "
                     "must reappear.",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="-",
        steps="1. Log in, open Tax Treaty Brief\n2. Record the full entry count\n"
              "3. Search a term, then clear the search box\n4. Verify the entry count returns to the original",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Record the full entry count")
    original_count = ttb.entries.count()

    case.step(3, "Search a term, then clear the search box")
    case.click(ttb.search_input, "'Search' input")
    ttb.search_input.fill("Zzzznotacountry")
    page.wait_for_timeout(1200)
    ttb.search_input.fill("")
    page.wait_for_timeout(1200)

    case.step(4, "Verify the entry count returns to the original")
    restored_count = ttb.entries.count()
    ok = restored_count == original_count
    case.check("Clearing the search box restores the full entry list", ok,
               expected=original_count, actual=restored_count)

    actual = (f"Clearing the search box correctly restored all {restored_count} entries." if ok else
              f"Clearing the search box did not restore the original entry count (expected "
              f"{original_count}, got {restored_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_taxtreatybrief_08_sidebar_remains_visible(page, result):
    case = Case(
        page, "TaxTreatyBrief_08", FEATURE, "The sidebar remains visible on Tax Treaty Brief",
        description="The left sidebar must remain visible while viewing Tax Treaty Brief.",
        precondition="User is logged in, on Tax Treaty Brief.",
        test_data="-",
        steps="1. Log in, open Tax Treaty Brief\n2. Verify the 'Archive' sidebar item is visible",
    )
    nav, ttb = _login_and_open(case, page)
    case.step(2, "Verify the 'Archive' sidebar item is visible")
    ok = case.verify_visible(nav.nav_archive, "'Archive' sidebar link")
    case.check("The sidebar remains visible on Tax Treaty Brief", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The sidebar correctly remains visible on Tax Treaty Brief." if ok else
              "The sidebar was not visible on Tax Treaty Brief.")
    result(case, actual, ok)
    assert ok, actual
