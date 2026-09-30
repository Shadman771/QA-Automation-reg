"""Treaties > Other Articles (/wta/OtherArticles). See
pages/treaties_other_articles_page.py for the full confirmed-live layout
notes."""
import pytest

from pages.treaties_other_articles_page import OtherArticlesPage, OTHER_ARTICLES_HEADERS
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Treaties OtherArticles"


def _login_and_open(case, page):
    perform_login(case, page)
    oa = OtherArticlesPage(page)
    case.action("Navigating to /wta/OtherArticles", kind="navigate")
    oa.goto()
    return oa


@pytest.mark.smoke
def test_otherarticles_01_page_loads(page, result):
    case = Case(
        page, "OtherArticles_01", FEATURE, "Other Articles page loads with the jurisdiction panel",
        description="The page must load at /wta/OtherArticles with the 'Select Jurisdiction' heading and "
                     "the left-panel placeholder text visible before any country is selected.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Other Articles\n2. Verify URL, heading and placeholder text",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Verify URL, heading and placeholder")
    url_ok = "/wta/OtherArticles" in page.url
    heading_ok = case.verify_visible(oa.heading, "'Select Jurisdiction' heading")
    placeholder_ok = case.verify_visible(oa.placeholder_text, "left-panel placeholder text")
    ok = url_ok and heading_ok and placeholder_ok
    case.check("Other Articles loads with URL/heading/placeholder all present", ok,
               expected="url_ok=True, heading_ok=True, placeholder_ok=True",
               actual=f"url_ok={url_ok}, heading_ok={heading_ok}, placeholder_ok={placeholder_ok}")

    actual = (f"Other Articles loaded correctly at {page.url}." if ok else
              f"Other Articles did not load as expected (url_ok={url_ok}, heading_ok={heading_ok}, "
              f"placeholder_ok={placeholder_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_otherarticles_02_selecting_country_renders_table(page, result):
    case = Case(
        page, "OtherArticles_02", FEATURE, "Selecting a jurisdiction renders the Other Articles table",
        description="Checking 'Australia' must render a table with columns ['Jurisdiction', 'Tie Breaker "
                     "Corporate', 'Capital Gain', 'Other Income', 'Exchange of Information'] and multiple rows.",
        precondition="User is logged in and on Other Articles.",
        test_data="Country: Australia",
        steps="1. Log in and open Other Articles\n2. Select Australia\n3. Verify the table headers and row count",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(oa.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(oa.table)

    case.step(3, "Verify table headers and rows")
    headers = oa.headers()
    headers_ok = headers == OTHER_ARTICLES_HEADERS
    row_count = oa.table_rows.count()
    rows_ok = row_count > 0
    ok = headers_ok and rows_ok
    case.check("Other Articles table shows the expected columns and at least one row", ok,
               expected=f"headers={OTHER_ARTICLES_HEADERS}, rows>0", actual=f"headers={headers}, rows={row_count}",
               locator=oa.table.first)

    actual = (f"Selecting Australia rendered the Other Articles table with the expected headers and "
              f"{row_count} rows." if ok else f"The Other Articles table did not match expectations "
              f"(headers={headers}, rows={row_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_03_table_row_contains_known_article_reference(page, result):
    case = Case(
        page, "OtherArticles_03", FEATURE, "The Austria row shows the expected Tie Breaker Corporate article",
        description="With Australia selected, the row for 'Austria' must show 'Art. 4(4)' as its Tie "
                     "Breaker Corporate article reference.",
        precondition="User is logged in, Australia selected on Other Articles.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in and open Other Articles\n2. Select Australia\n"
              "3. Verify the 'Austria' row contains 'Art. 4(4)'",
    )
    oa = _login_and_open(case, page)
    oa.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(oa.table)

    case.step(3, "Verify the Austria row's article reference")
    row = oa.table_rows.filter(has_text="Austria")
    row_exists = row.count() >= 1
    row_text = row.first.inner_text() if row_exists else ""
    ok = row_exists and "Art. 4(4)" in row_text
    case.check("The 'Austria' row contains 'Art. 4(4)'", ok, expected="Art. 4(4)", actual=row_text,
               locator=row.first if row_exists else None)

    actual = ("The 'Austria' row correctly shows 'Art. 4(4)' as its Tie Breaker Corporate article reference."
              if ok else f"The expected article reference was not found (row_exists={row_exists}, "
              f"text={row_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_04_region_tab_switches_country_list(page, result):
    case = Case(
        page, "OtherArticles_04", FEATURE, "Switching the 'MEA' region tab changes the visible country list",
        description="Clicking the 'MEA' region tab must change the visible jurisdiction list away from the "
                     "default Asia Pacific set - confirmed by 'Australia' no longer being visible.",
        precondition="User is logged in and on Other Articles.",
        test_data="Region: MEA",
        steps="1. Log in and open Other Articles\n2. Click the 'MEA' region tab\n"
              "3. Verify 'Australia' is no longer visible",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Click the 'MEA' region tab")
    case.click(oa.jurisdiction.region_tab("MEA"), "'MEA' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Australia' is no longer visible")
    australia_locator = oa.jurisdiction.country_checkbox("Australia")
    still_visible = australia_locator.count() > 0 and australia_locator.is_visible()
    ok = not still_visible
    case.check("'Australia' is not visible under the MEA region tab", ok, expected=False, actual=still_visible,
               locator=australia_locator if australia_locator.count() > 0 else None)

    actual = ("Switching to the 'MEA' region tab correctly changed the jurisdiction list away from Asia "
              "Pacific ('Australia' no longer visible)." if ok else
              "Switching to the 'MEA' region tab did not change the jurisdiction list as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_05_no_countries_found_on_bad_search(page, result):
    case = Case(
        page, "OtherArticles_05", FEATURE, "Searching for a non-existent country shows the 'No countries found' message",
        description="Typing an unmatched string into 'Search countries' must show the "
                     "'No countries found matching ...' message.",
        precondition="User is logged in and on Other Articles.",
        test_data="Search text: zzzznotarealcountry",
        steps="1. Log in and open Other Articles\n2. Type 'zzzznotarealcountry' into the search box\n"
              "3. Verify the 'No countries found' message is shown",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Type an unmatched search term")
    case.fill(oa.jurisdiction.search_countries, "zzzznotarealcountry", "'Search countries' box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the no-results message")
    ok = case.verify_visible(oa.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("'No countries found matching...' message is shown for an unmatched search", ok,
               expected=True, actual=ok, locator=oa.jurisdiction.no_countries_message)

    actual = ("Searching for a non-existent country correctly showed the 'No countries found' message." if ok
              else "The 'No countries found' message was not shown for an unmatched search term.")
    result(case, actual, ok)
    assert ok, actual
