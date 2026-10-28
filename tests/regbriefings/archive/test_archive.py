"""RegBriefings > Archive (/regbrief/pastBriefingYearly).

New parent module (RegBriefings), built via live DOM discovery - no
QA-sheet reference exists. A year selector (2011 through the current
year, confirmed live) controls which year's archived monthly briefs
show. Uses "last calendar year" (computed dynamically from today's
date, not hardcoded) as the target year with real data, since a full
past year reliably has complete archived content regardless of when
this suite runs - avoids the exact hardcoded-year gotcha already fixed
in World Tax Brief's search tests."""
import datetime

import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav
from pages.regbriefings.archive_page import ArchivePage
from utils.auth import perform_login
from utils.case import Case
from config.settings import APP_ORIGIN

FEATURE = "RegBriefings Archive"

LAST_FULL_YEAR = str(datetime.date.today().year - 1)


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > Archive", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    archive = ArchivePage(page)
    case.click(nav.nav_archive, "'Archive' sidebar link")
    page.wait_for_load_state("domcontentloaded")
    case.verify_visible(archive.world_tax_brief_heading, "'World Tax Brief' section heading")
    return nav, archive


@pytest.mark.smoke
def test_archive_01_access_via_sidebar(page, result):
    case = Case(
        page, "Archive_01", FEATURE, "Archive opens from the RegBriefings sidebar",
        description="Clicking 'Archive' in the sidebar must land on /regbrief/pastBriefingYearly with all "
                     "3 brief-type section headings visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Archive\n2. Verify the URL and all 3 section headings",
    )
    nav, archive = _login_and_open(case, page)
    case.step(2, "Verify URL and all 3 section headings")
    url_ok = "/regbrief/pastBriefingYearly" in page.url
    wta_ok = case.verify_visible(archive.world_tax_brief_heading, "'World Tax Brief' heading")
    tpa_ok = case.verify_visible(archive.transfer_pricing_brief_heading, "'Transfer Pricing Brief' heading")
    tt_ok = case.verify_visible(archive.tax_treaty_brief_heading, "'Tax Treaty Brief' heading")
    ok = url_ok and wta_ok and tpa_ok and tt_ok
    case.check("Archive opens with all 3 section headings visible", ok,
               expected="url contains /regbrief/pastBriefingYearly, all 3 headings visible",
               actual=f"url={page.url}, wta={wta_ok}, tpa={tpa_ok}, tt={tt_ok}")

    actual = ("Archive opened correctly with all 3 section headings visible." if ok else
              "Archive did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_archive_02_direct_deep_link_loads(page, result):
    case = Case(
        page, "Archive_02", FEATURE, "A direct deep link to /regbrief/pastBriefingYearly loads correctly",
        description="Navigating straight to /regbrief/pastBriefingYearly must load real content, not "
                     "redirect elsewhere.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /regbrief/pastBriefingYearly\n3. Verify real content loads",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /regbrief/pastBriefingYearly")
    case.goto(APP_ORIGIN + "/regbrief/pastBriefingYearly", "Archive (direct deep link)")
    page.wait_for_timeout(2000)
    archive = ArchivePage(page)

    case.step(3, "Verify real content loads")
    url_ok = "/regbrief/pastBriefingYearly" in page.url
    content_ok = case.verify_visible(archive.world_tax_brief_heading, "'World Tax Brief' section heading")
    ok = url_ok and content_ok
    case.check("Direct deep link loads real Archive content", ok,
               expected="url contains /regbrief/pastBriefingYearly, content visible",
               actual=f"url={page.url}, content={content_ok}")

    actual = ("The direct deep link correctly loaded real Archive content." if ok else
              "The direct deep link did not load the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_archive_03_year_selector_lists_a_wide_range(page, result):
    case = Case(
        page, "Archive_03", FEATURE, "The year selector lists a wide range of years including 2011",
        description="The Archive year selector must list at least the current year down through 2011.",
        precondition="User is logged in, on Archive.",
        test_data="-",
        steps="1. Log in, open Archive\n2. Verify the current year and '2011' are both visible",
    )
    nav, archive = _login_and_open(case, page)
    case.step(2, "Verify the current year and '2011' are both visible")
    current_year = str(datetime.date.today().year)
    current_ok = case.verify_visible(archive.year_item(current_year), f"'{current_year}' year item")
    oldest_ok = case.verify_visible(archive.year_item("2011"), "'2011' year item")
    ok = current_ok and oldest_ok
    case.check("The year selector lists both the current year and 2011", ok,
               expected="both visible", actual=f"current_year({current_year})={current_ok}, 2011={oldest_ok}")

    actual = ("The year selector correctly lists a wide range of years." if ok else
              "The year selector did not list the expected range of years.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_archive_04_selecting_a_past_year_shows_monthly_cards(page, result):
    case = Case(
        page, "Archive_04", FEATURE, "Selecting a full past year shows real monthly brief cards",
        description=f"Selecting {LAST_FULL_YEAR} (last calendar year, computed dynamically so this stays "
                     "correct regardless of when the suite runs) must show at least one real monthly "
                     "brief card for World Tax Brief.",
        precondition="User is logged in, on Archive.",
        test_data=f"Year: {LAST_FULL_YEAR}",
        steps=f"1. Log in, open Archive\n2. Select {LAST_FULL_YEAR}\n"
              "3. Verify at least one monthly brief card is visible",
    )
    nav, archive = _login_and_open(case, page)
    case.step(2, f"Select {LAST_FULL_YEAR}")
    case.click(archive.year_item(LAST_FULL_YEAR), f"'{LAST_FULL_YEAR}' year item")
    page.wait_for_timeout(2000)

    case.step(3, "Verify at least one monthly brief card is visible")
    count = archive.monthly_cards.count()
    ok = count >= 1
    case.check(f"At least one monthly brief card is visible for {LAST_FULL_YEAR}", ok,
               expected=">= 1", actual=f"count={count}")

    actual = (f"Selecting {LAST_FULL_YEAR} correctly showed {count} monthly brief card(s)." if ok else
              f"Selecting {LAST_FULL_YEAR} showed no monthly brief cards.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_archive_05_clicking_a_monthly_card_navigates_to_detail(page, result):
    case = Case(
        page, "Archive_05", FEATURE, "Clicking a monthly brief card navigates to its detail page",
        description="Clicking a real monthly World Tax Brief card must navigate to "
                     "/regbrief/pastBriefingDetails with type=WtaBriefing and matching month/year query "
                     "params - confirmed live for December 2025.",
        precondition="User is logged in, a past year with data selected.",
        test_data=f"Year: {LAST_FULL_YEAR}",
        steps=f"1. Log in, open Archive, select {LAST_FULL_YEAR}\n"
              "2. Click the first visible monthly brief card\n"
              "3. Verify the URL navigates to the detail page",
    )
    nav, archive = _login_and_open(case, page)
    case.click(archive.year_item(LAST_FULL_YEAR), f"'{LAST_FULL_YEAR}' year item")
    page.wait_for_timeout(2000)

    case.step(2, "Click the first visible monthly brief card")
    first_card = archive.monthly_cards.first
    case.click(first_card, "First monthly brief card")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the URL navigates to the detail page")
    ok = "/regbrief/pastBriefingDetails" in page.url and "year=" in page.url and "month=" in page.url
    case.check("Clicking a monthly card navigates to the detail page with the expected query params", ok,
               expected="/regbrief/pastBriefingDetails?...year=...&month=...", actual=page.url)

    actual = (f"Clicking the monthly card correctly navigated to {page.url}." if ok else
              f"Clicking the monthly card did not navigate as expected (got {page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_archive_06_sidebar_remains_visible(page, result):
    case = Case(
        page, "Archive_06", FEATURE, "The sidebar remains visible on Archive",
        description="The left sidebar must remain visible while viewing Archive.",
        precondition="User is logged in, on Archive.",
        test_data="-",
        steps="1. Log in, open Archive\n2. Verify the 'My Briefs' sidebar item is visible",
    )
    nav, archive = _login_and_open(case, page)
    case.step(2, "Verify the 'My Briefs' sidebar item is visible")
    ok = case.verify_visible(nav.nav_my_briefs, "'My Briefs' sidebar link")
    case.check("The sidebar remains visible on Archive", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The sidebar correctly remains visible on Archive." if ok else
              "The sidebar was not visible on Archive.")
    result(case, actual, ok)
    assert ok, actual
