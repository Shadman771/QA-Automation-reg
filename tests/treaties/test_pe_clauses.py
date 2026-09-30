"""Treaties > PE Clause (/wta/PEClauses). See pages/treaties_pe_clauses_page.py
for the full confirmed-live layout notes."""
import os

import pytest

from pages.treaties_pe_clauses_page import PEClausesPage, PE_CLAUSES_HEADERS
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Treaties PEClauses"


def _login_and_open(case, page):
    perform_login(case, page)
    pe = PEClausesPage(page)
    case.action("Navigating to /wta/PEClauses", kind="navigate")
    pe.goto()
    return pe


@pytest.mark.smoke
def test_peclauses_01_page_loads(page, result):
    case = Case(
        page, "PEClauses_01", FEATURE, "PE Clause page loads with the jurisdiction panel",
        description="The page must load at /wta/PEClauses with the 'Select Jurisdiction' heading and the "
                     "left-panel placeholder text visible before any country is selected.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open PE Clause\n2. Verify URL, heading and placeholder text",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Verify URL, heading and placeholder")
    url_ok = "/wta/PEClauses" in page.url
    heading_ok = case.verify_visible(pe.heading, "'Select Jurisdiction' heading")
    placeholder_ok = case.verify_visible(pe.placeholder_text, "left-panel placeholder text")
    ok = url_ok and heading_ok and placeholder_ok
    case.check("PE Clause loads with URL/heading/placeholder all present", ok,
               expected="url_ok=True, heading_ok=True, placeholder_ok=True",
               actual=f"url_ok={url_ok}, heading_ok={heading_ok}, placeholder_ok={placeholder_ok}")

    actual = (f"PE Clause loaded correctly at {page.url}." if ok else
              f"PE Clause did not load as expected (url_ok={url_ok}, heading_ok={heading_ok}, "
              f"placeholder_ok={placeholder_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_peclauses_02_selecting_country_renders_table(page, result):
    case = Case(
        page, "PEClauses_02", FEATURE, "Selecting a jurisdiction renders the PE clause table",
        description="Checking 'Australia' must render a table with columns ['Jurisdiction', 'Fixed Base', "
                     "'Construction Assembly', 'Dependent Agent', 'Services', 'Exempt PE'] and multiple rows.",
        precondition="User is logged in and on PE Clause.",
        test_data="Country: Australia",
        steps="1. Log in and open PE Clause\n2. Select Australia\n3. Verify the table headers and row count",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(pe.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(pe.table)

    case.step(3, "Verify table headers and rows")
    headers = pe.headers()
    headers_ok = headers == PE_CLAUSES_HEADERS
    row_count = pe.table_rows.count()
    rows_ok = row_count > 0
    ok = headers_ok and rows_ok
    case.check("PE clause table shows the expected columns and at least one row", ok,
               expected=f"headers={PE_CLAUSES_HEADERS}, rows>0", actual=f"headers={headers}, rows={row_count}",
               locator=pe.table.first)

    actual = (f"Selecting Australia rendered the PE clause table with the expected headers and {row_count} "
              f"rows." if ok else f"The PE clause table did not match expectations (headers={headers}, "
              f"rows={row_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_03_table_row_contains_known_article_reference(page, result):
    case = Case(
        page, "PEClauses_03", FEATURE, "The Austria row shows the expected Fixed Base article reference",
        description="With Australia selected, the row for 'Austria' must show 'Art. 5(1)' as its Fixed "
                     "Base article reference.",
        precondition="User is logged in, Australia selected on PE Clause.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in and open PE Clause\n2. Select Australia\n"
              "3. Verify the 'Austria' row contains 'Art. 5(1)'",
    )
    pe = _login_and_open(case, page)
    pe.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(pe.table)

    case.step(3, "Verify the Austria row's article reference")
    row = pe.table_rows.filter(has_text="Austria")
    row_exists = row.count() >= 1
    row_text = row.first.inner_text() if row_exists else ""
    ok = row_exists and "Art. 5(1)" in row_text
    case.check("The 'Austria' row contains 'Art. 5(1)'", ok, expected="Art. 5(1)", actual=row_text,
               locator=row.first if row_exists else None)

    actual = ("The 'Austria' row correctly shows 'Art. 5(1)' as its Fixed Base article reference." if ok else
              f"The expected article reference was not found (row_exists={row_exists}, text={row_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_04_region_tab_switches_country_list(page, result):
    case = Case(
        page, "PEClauses_04", FEATURE, "Switching the 'Europe' region tab shows a European jurisdiction",
        description="Clicking the 'Europe' region tab must make a known European country (e.g. 'Belgium') "
                     "visible in the left jurisdiction list.",
        precondition="User is logged in and on PE Clause.",
        test_data="Region: Europe, expected country: Belgium",
        steps="1. Log in and open PE Clause\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Belgium' is visible in the jurisdiction list",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(pe.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Belgium' is visible")
    ok = case.verify_visible(pe.jurisdiction.country_checkbox("Belgium"), "'Belgium' jurisdiction")
    case.check("'Belgium' is visible under the Europe region tab", ok, expected=True, actual=ok,
               locator=pe.jurisdiction.country_checkbox("Belgium"))

    actual = ("Switching to the 'Europe' region tab made 'Belgium' visible in the jurisdiction list." if ok else
              "Switching to the 'Europe' region tab did not show 'Belgium' as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_05_no_countries_found_on_bad_search(page, result):
    case = Case(
        page, "PEClauses_05", FEATURE, "Searching for a non-existent country shows the 'No countries found' message",
        description="Typing an unmatched string into 'Search countries' must show the "
                     "'No countries found matching ...' message and hide the jurisdiction list.",
        precondition="User is logged in and on PE Clause.",
        test_data="Search text: zzzznotarealcountry",
        steps="1. Log in and open PE Clause\n2. Type 'zzzznotarealcountry' into the search box\n"
              "3. Verify the 'No countries found' message is shown",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Type an unmatched search term")
    case.fill(pe.jurisdiction.search_countries, "zzzznotarealcountry", "'Search countries' box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the no-results message")
    ok = case.verify_visible(pe.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("'No countries found matching...' message is shown for an unmatched search", ok,
               expected=True, actual=ok, locator=pe.jurisdiction.no_countries_message)

    actual = ("Searching for a non-existent country correctly showed the 'No countries found' message." if ok
              else "The 'No countries found' message was not shown for an unmatched search term.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_06_article_link_opens_detail_modal(page, result):
    case = Case(
        page, "PEClauses_06", FEATURE, "Clicking an article-reference link opens the treaty article modal",
        description="With Australia selected, clicking the 'Art. 5(1)' link in the Austria row's 'Fixed Base' "
                     "column must open a modal titled 'Treaty between Australia and Austria' - same "
                     "click-to-modal pattern confirmed on Treaties > Other Articles.",
        precondition="User is logged in, Australia selected on PE Clause.",
        test_data="Country: Australia, partner: Austria, column: Fixed Base",
        steps="1. Log in and open PE Clause\n2. Select Australia\n"
              "3. Click the 'Art. 5(1)' link in the Austria row\n4. Verify the article modal title",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(pe.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(pe.table)

    case.step(3, "Click the Austria row's Fixed Base article link")
    link = pe.article_link_in_row("Austria", 1)
    link_present = link.count() >= 1
    if link_present:
        case.click(link.first, "'Art. 5(1)' article link (Austria row)")
        pe.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(4, "Verify the modal title")
    title = pe.article_modal_title.first.inner_text() if link_present else ""
    title_ok = "Treaty between Australia and Austria" in title
    ok = link_present and title_ok
    case.check("The article modal opens with the correct treaty title", ok,
               expected="title contains 'Treaty between Australia and Austria'",
               actual=f"link_present={link_present}, title={title!r}",
               locator=pe.article_modal_title.first if link_present else None)

    if link_present:
        case.click(pe.article_modal_ok_button, "'OK' button (close modal)")

    actual = (f"Clicking the Austria article link correctly opened the modal ({title!r})." if ok else
              f"The article modal did not open/match as expected (link_present={link_present}, title={title!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_07_article_modal_pdf_export_downloads(page, result):
    case = Case(
        page, "PEClauses_07", FEATURE, "The article modal's PDF export downloads a real, non-empty file",
        description="With the Austria article modal open (Australia selected), clicking 'PDF' under Export must "
                     "trigger a real file download with no failure and a non-zero size.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open PE Clause, select Australia\n2. Open the Austria article modal\n"
              "3. Click 'PDF' under Export\n4. Verify a real, non-empty PDF download completed",
    )
    pe = _login_and_open(case, page)
    case.click(pe.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(pe.table)
    link = pe.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 5(1)' article link (Austria row)")
    pe.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click 'PDF' under Export")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(pe.article_modal_export_pdf.first, "'PDF' export action")
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

    case.click(pe.article_modal_ok_button, "'OK' button (close modal)")
    actual = (f"PDF export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"PDF export did not produce a valid download (failure={failure}, filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_peclauses_08_table_export_excel_downloads(page, result):
    case = Case(
        page, "PEClauses_08", FEATURE, "The table-level 'Export as Excel' button downloads the whole table",
        description="With Australia selected (no article link clicked), clicking the table's 'Export as Excel' "
                     "icon button must trigger a real, non-empty .xlsx download.",
        precondition="User is logged in, Australia selected on PE Clause.",
        test_data="Country: Australia",
        steps="1. Log in and open PE Clause\n2. Select Australia\n"
              "3. Click the 'Export as Excel' icon button\n4. Verify a real, non-empty .xlsx download completed",
    )
    pe = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(pe.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(pe.table)

    case.step(3, "Click the 'Export as Excel' button")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(pe.export_excel_button.first, "'Export as Excel' button")
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
