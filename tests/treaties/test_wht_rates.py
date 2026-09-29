"""Treaties > WHT Rates (/wta/WHTRates). See pages/treaties_wht_rates_page.py
for the full confirmed-live layout notes."""
import pytest

from pages.treaties_wht_rates_page import WHTRatesPage, WHT_RATES_HEADERS
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Treaties WHTRates"


def _login_and_open(case, page):
    perform_login(case, page)
    wht = WHTRatesPage(page)
    case.action("Navigating to /wta/WHTRates", kind="navigate")
    wht.goto()
    return wht


@pytest.mark.smoke
def test_whtrates_01_page_loads(page, result):
    case = Case(
        page, "WHTRates_01", FEATURE, "WHT Rates page loads with the jurisdiction panel",
        description="The page must load at /wta/WHTRates with the 'Select Jurisdiction' heading and the "
                     "left-panel placeholder text visible before any country is selected.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open WHT Rates\n2. Verify URL, heading and placeholder text",
    )
    wht = _login_and_open(case, page)
    case.step(2, "Verify URL, heading and placeholder")
    url_ok = "/wta/WHTRates" in page.url
    heading_ok = case.verify_visible(wht.heading, "'Select Jurisdiction' heading")
    placeholder_ok = case.verify_visible(wht.placeholder_text, "left-panel placeholder text")
    ok = url_ok and heading_ok and placeholder_ok
    case.check("WHT Rates loads with URL/heading/placeholder all present", ok,
               expected="url_ok=True, heading_ok=True, placeholder_ok=True",
               actual=f"url_ok={url_ok}, heading_ok={heading_ok}, placeholder_ok={placeholder_ok}")

    actual = (f"WHT Rates loaded correctly at {page.url}." if ok else
              f"WHT Rates did not load as expected (url_ok={url_ok}, heading_ok={heading_ok}, "
              f"placeholder_ok={placeholder_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrates_02_selecting_country_renders_table(page, result):
    case = Case(
        page, "WHTRates_02", FEATURE, "Selecting a jurisdiction renders the WHT rates table",
        description="Checking 'Australia' must render a table with the 11 expected rate columns and "
                     "multiple rows.",
        precondition="User is logged in and on WHT Rates.",
        test_data="Country: Australia",
        steps="1. Log in and open WHT Rates\n2. Select Australia\n3. Verify the table headers and row count",
    )
    wht = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(wht.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(wht.table)

    case.step(3, "Verify table headers and rows")
    headers = wht.headers()
    headers_ok = headers == WHT_RATES_HEADERS
    row_count = wht.table_rows.count()
    rows_ok = row_count > 0
    ok = headers_ok and rows_ok
    case.check("WHT rates table shows the expected 11 columns and at least one row", ok,
               expected=f"headers={WHT_RATES_HEADERS}, rows>0", actual=f"headers={headers}, rows={row_count}",
               locator=wht.table.first)

    actual = (f"Selecting Australia rendered the WHT rates table with the expected headers and {row_count} "
              f"rows." if ok else f"The WHT rates table did not match expectations (headers={headers}, "
              f"rows={row_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrates_03_first_row_is_domestic_rates(page, result):
    case = Case(
        page, "WHTRates_03", FEATURE, "The first table row is always 'Domestic WHT rates' for the selected country",
        description="With Australia selected, the first row of the WHT rates table must be the literal "
                     "'Domestic WHT rates' row (the selected country's own domestic rates), not a treaty "
                     "partner row.",
        precondition="User is logged in, Australia selected on WHT Rates.",
        test_data="Country: Australia",
        steps="1. Log in and open WHT Rates\n2. Select Australia\n"
              "3. Verify the first table row reads 'Domestic WHT rates'",
    )
    wht = _login_and_open(case, page)
    wht.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(wht.table)

    case.step(3, "Verify the first row")
    first_row_text = wht.table_rows.first.inner_text()
    ok = "Domestic WHT rates" in first_row_text
    case.check("First row is 'Domestic WHT rates'", ok, expected="Domestic WHT rates",
               actual=first_row_text, locator=wht.table_rows.first)

    actual = ("The first row of the WHT rates table correctly reads 'Domestic WHT rates'." if ok else
              f"The first row did not read 'Domestic WHT rates' as expected (got: {first_row_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrates_04_row_contains_known_partner_rate(page, result):
    case = Case(
        page, "WHTRates_04", FEATURE, "The Austria row shows the expected Dividend (Sub-hold) rate",
        description="With Australia selected, the row for 'Austria' must show '15.00' as its "
                     "Div-Sub. hold rate.",
        precondition="User is logged in, Australia selected on WHT Rates.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in and open WHT Rates\n2. Select Australia\n"
              "3. Verify the 'Austria' row contains '15.00'",
    )
    wht = _login_and_open(case, page)
    wht.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(wht.table)

    case.step(3, "Verify the Austria row's Div-Sub. hold rate")
    row = wht.table_rows.filter(has_text="Austria")
    row_exists = row.count() >= 1
    row_text = row.first.inner_text() if row_exists else ""
    ok = row_exists and "15.00" in row_text
    case.check("The 'Austria' row contains a '15.00' rate", ok, expected="15.00", actual=row_text,
               locator=row.first if row_exists else None)

    actual = ("The 'Austria' row correctly shows a '15.00' Div-Sub. hold rate." if ok else
              f"The expected rate was not found (row_exists={row_exists}, text={row_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrates_05_no_countries_found_on_bad_search(page, result):
    case = Case(
        page, "WHTRates_05", FEATURE, "Searching for a non-existent country shows the 'No countries found' message",
        description="Typing an unmatched string into 'Search countries' must show the "
                     "'No countries found matching ...' message.",
        precondition="User is logged in and on WHT Rates.",
        test_data="Search text: zzzznotarealcountry",
        steps="1. Log in and open WHT Rates\n2. Type 'zzzznotarealcountry' into the search box\n"
              "3. Verify the 'No countries found' message is shown",
    )
    wht = _login_and_open(case, page)
    case.step(2, "Type an unmatched search term")
    case.fill(wht.jurisdiction.search_countries, "zzzznotarealcountry", "'Search countries' box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the no-results message")
    ok = case.verify_visible(wht.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("'No countries found matching...' message is shown for an unmatched search", ok,
               expected=True, actual=ok, locator=wht.jurisdiction.no_countries_message)

    actual = ("Searching for a non-existent country correctly showed the 'No countries found' message." if ok
              else "The 'No countries found' message was not shown for an unmatched search term.")
    result(case, actual, ok)
    assert ok, actual
