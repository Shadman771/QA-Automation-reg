"""Treaties > WHT Rates (/wta/WHTRates). See pages/treaties_wht_rates_page.py
for the full confirmed-live layout notes."""
import os

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


@pytest.mark.regression
def test_whtrates_06_rate_link_opens_detail_modal(page, result):
    case = Case(
        page, "WHTRates_06", FEATURE, "Clicking a rate cell's link opens the treaty article modal",
        description="With Australia selected, clicking the Austria row's '15.00' Div-Sub. hold rate must open a "
                     "modal titled 'Treaty between Australia and Austria' showing the actual treaty article "
                     "(Article 10, Dividends) the rate derives from - same click-to-modal pattern confirmed on "
                     "Treaties > Other Articles.",
        precondition="User is logged in, Australia selected on WHT Rates.",
        test_data="Country: Australia, partner: Austria, column: Div-Sub. hold",
        steps="1. Log in and open WHT Rates\n2. Select Australia\n"
              "3. Click the Austria row's Div-Sub. hold rate link\n4. Verify the article modal title and content",
    )
    wht = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(wht.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(wht.table)

    case.step(3, "Click the Austria row's Div-Sub. hold rate link")
    link = wht.article_link_in_row("Austria", 1)
    link_present = link.count() >= 1
    if link_present:
        case.click(link.first, "'15.00' rate link (Austria row)")
        wht.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(4, "Verify the modal title and article content")
    title = wht.article_modal_title.first.inner_text() if link_present else ""
    body_text = page.locator(".rs-modal-body").first.inner_text() if link_present else ""
    title_ok = "Treaty between Australia and Austria" in title
    body_ok = "Article 10" in body_text
    ok = link_present and title_ok and body_ok
    case.check("The article modal opens with the correct treaty title and underlying article", ok,
               expected="title contains 'Treaty between Australia and Austria', body contains 'Article 10'",
               actual=f"link_present={link_present}, title={title!r}, body_ok={body_ok}",
               locator=wht.article_modal_title.first if link_present else None)

    if link_present:
        case.click(wht.article_modal_ok_button, "'OK' button (close modal)")

    actual = (f"Clicking the Austria rate link correctly opened the modal ({title!r})." if ok else
              f"The article modal did not open/match as expected (link_present={link_present}, title={title!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrates_07_article_modal_pdf_export_downloads(page, result):
    case = Case(
        page, "WHTRates_07", FEATURE, "The article modal's PDF export downloads a real, non-empty file",
        description="With the Austria article modal open (Australia selected), clicking 'PDF' under Export must "
                     "trigger a real file download with no failure and a non-zero size.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open WHT Rates, select Australia\n2. Open the Austria article modal\n"
              "3. Click 'PDF' under Export\n4. Verify a real, non-empty PDF download completed",
    )
    wht = _login_and_open(case, page)
    case.click(wht.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(wht.table)
    link = wht.article_link_in_row("Austria", 1)
    case.click(link.first, "'15.00' rate link (Austria row)")
    wht.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click 'PDF' under Export")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(wht.article_modal_export_pdf.first, "'PDF' export action")
    download = dl_info.value

    case.step(4, "Verify the PDF download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith(".pdf") and size > 0
    case.check("The PDF export downloads a real, non-empty .pdf file with no failure", ok,
               expected="failure=None, filename ends with .pdf, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    case.click(wht.article_modal_ok_button, "'OK' button (close modal)")
    actual = (f"PDF export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"PDF export did not produce a valid download (failure={failure}, filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrates_08_table_export_excel_downloads(page, result):
    case = Case(
        page, "WHTRates_08", FEATURE, "The table-level 'Export as Excel' button downloads the whole table",
        description="With Australia selected (no rate link clicked), clicking the table's 'Export as Excel' "
                     "icon button must trigger a real, non-empty .xlsx download.",
        precondition="User is logged in, Australia selected on WHT Rates.",
        test_data="Country: Australia",
        steps="1. Log in and open WHT Rates\n2. Select Australia\n"
              "3. Click the 'Export as Excel' icon button\n4. Verify a real, non-empty .xlsx download completed",
    )
    wht = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(wht.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(wht.table)

    case.step(3, "Click the 'Export as Excel' button")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(wht.export_excel_button.first, "'Export as Excel' button")
    download = dl_info.value

    case.step(4, "Verify the Excel download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith(".xlsx") and size > 0
    case.check("Exporting the table downloads a real, non-empty .xlsx file with no failure", ok,
               expected="failure=None, filename ends with .xlsx, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"Table export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"Table export did not produce a valid download (failure={failure}, filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual
