"""Treaties > Full DTA (/wta/FullDta). See pages/treaties_full_dta_page.py
for the full confirmed-live layout notes."""
import os

import pytest

from pages.treaties_full_dta_page import FullDtaPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Treaties FullDta"


def _login_and_open(case, page):
    perform_login(case, page)
    fd = FullDtaPage(page)
    case.action("Navigating to /wta/FullDta", kind="navigate")
    fd.goto()
    return fd


@pytest.mark.smoke
def test_fulldta_01_page_loads(page, result):
    case = Case(
        page, "FullDta_01", FEATURE, "Full DTA page loads with the jurisdiction panel",
        description="The page must load at /wta/FullDta with the 'Select Jurisdiction' heading and the "
                     "left-panel placeholder text visible before any country is selected.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Full DTA\n2. Verify URL, heading and placeholder text",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Verify URL, heading and placeholder")
    url_ok = "/wta/FullDta" in page.url
    heading_ok = case.verify_visible(fd.heading, "'Select Jurisdiction' heading")
    placeholder_ok = case.verify_visible(fd.placeholder_text, "left-panel placeholder text")
    ok = url_ok and heading_ok and placeholder_ok
    case.check("Full DTA loads with URL/heading/placeholder all present", ok,
               expected="url_ok=True, heading_ok=True, placeholder_ok=True",
               actual=f"url_ok={url_ok}, heading_ok={heading_ok}, placeholder_ok={placeholder_ok}")

    actual = (f"Full DTA loaded correctly at {page.url} with the expected heading and placeholder." if ok else
              f"Full DTA did not load as expected (url_ok={url_ok}, heading_ok={heading_ok}, "
              f"placeholder_ok={placeholder_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_fulldta_02_selecting_country_renders_dta_table(page, result):
    case = Case(
        page, "FullDta_02", FEATURE, "Selecting a jurisdiction renders the DTA table with expected columns",
        description="Checking 'Australia' must render a table with columns ['', 'Partner Country', "
                     "'Status', 'Signature', 'Entry Into Force', 'Effective'] and at least one row.",
        precondition="User is logged in and on Full DTA.",
        test_data="Country: Australia",
        steps="1. Log in and open Full DTA\n2. Select Australia\n3. Verify the table headers and row count",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(fd.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(fd.table)

    case.step(3, "Verify table headers and rows")
    headers = fd.headers()
    expected_headers = ["", "Partner Country", "Status", "Signature", "Entry Into Force", "Effective"]
    headers_ok = headers == expected_headers
    row_count = fd.table_rows.count()
    rows_ok = row_count > 0
    ok = headers_ok and rows_ok
    case.check("DTA table shows the expected columns and at least one row", ok,
               expected=f"headers={expected_headers}, rows>0", actual=f"headers={headers}, rows={row_count}",
               locator=fd.table.first)

    actual = (f"Selecting Australia rendered the DTA table with the expected headers and {row_count} rows."
              if ok else f"The DTA table did not match expectations (headers={headers}, rows={row_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_03_table_row_contains_known_treaty_partner(page, result):
    case = Case(
        page, "FullDta_03", FEATURE, "The Australia DTA table lists a known treaty partner with its status",
        description="With Australia selected, the DTA table must include a row for 'Austria' whose status "
                     "is 'In Force'.",
        precondition="User is logged in, Australia selected on Full DTA.",
        test_data="Country: Australia, expected partner: Austria",
        steps="1. Log in and open Full DTA\n2. Select Australia\n"
              "3. Verify a row for 'Austria' exists and shows 'In Force'",
    )
    fd = _login_and_open(case, page)
    fd.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(fd.table)

    case.step(3, "Verify the Austria row")
    row = fd.table_rows.filter(has_text="Austria")
    row_exists = row.count() >= 1
    row_text = row.first.inner_text() if row_exists else ""
    status_ok = row_exists and "In Force" in row_text
    ok = row_exists and status_ok
    case.check("A row for 'Austria' exists and shows 'In Force'", ok,
               expected="Austria row containing 'In Force'", actual=row_text, locator=row.first if row_exists else None)

    actual = ("The DTA table includes an 'Austria' row showing 'In Force', as expected for a live treaty "
              "partner." if ok else f"The expected Austria/'In Force' row was not found (row_exists={row_exists}, "
              f"text={row_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_04_region_tab_switches_country_list(page, result):
    case = Case(
        page, "FullDta_04", FEATURE, "Switching the 'Americas' region tab shows an Americas jurisdiction",
        description="Clicking the 'Americas' region tab must make a known Americas country (e.g. 'Canada') "
                     "visible in the left jurisdiction list.",
        precondition="User is logged in and on Full DTA.",
        test_data="Region: Americas, expected country: Canada",
        steps="1. Log in and open Full DTA\n2. Click the 'Americas' region tab\n"
              "3. Verify 'Canada' is visible in the jurisdiction list",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Click the 'Americas' region tab")
    case.click(fd.jurisdiction.region_tab("Americas"), "'Americas' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Canada' is visible")
    ok = case.verify_visible(fd.jurisdiction.country_checkbox("Canada"), "'Canada' jurisdiction")
    case.check("'Canada' is visible under the Americas region tab", ok, expected=True, actual=ok,
               locator=fd.jurisdiction.country_checkbox("Canada"))

    actual = ("Switching to the 'Americas' region tab made 'Canada' visible in the jurisdiction list." if ok else
              "Switching to the 'Americas' region tab did not show 'Canada' as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_05_search_filters_jurisdiction_list(page, result):
    case = Case(
        page, "FullDta_05", FEATURE, "The country search box narrows the jurisdiction list by substring",
        description="Typing 'Aus' into the search box must keep 'Australia' visible while filtering out "
                     "'Bangladesh' (which does not match).",
        precondition="User is logged in and on Full DTA.",
        test_data="Search text: Aus",
        steps="1. Log in and open Full DTA\n2. Type 'Aus' into the search box\n"
              "3. Verify 'Australia' stays visible and 'Bangladesh' is filtered out",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Type 'Aus' into the search box")
    case.fill(fd.jurisdiction.search_countries, "Aus", "search countries/models box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the filtered list")
    australia_visible = case.verify_visible(fd.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    bangladesh_hidden = fd.jurisdiction.country_checkbox("Bangladesh").count() == 0 or \
        not fd.jurisdiction.country_checkbox("Bangladesh").is_visible()
    ok = australia_visible and bangladesh_hidden
    case.check("Search narrows the list to matches only", ok,
               expected="Australia visible, Bangladesh hidden",
               actual=f"australia_visible={australia_visible}, bangladesh_hidden={bangladesh_hidden}")

    actual = ("Typing 'Aus' kept 'Australia' visible and filtered out non-matching 'Bangladesh', confirming "
              "the search box narrows the jurisdiction list." if ok else
              f"The search box did not filter as expected (australia_visible={australia_visible}, "
              f"bangladesh_hidden={bangladesh_hidden}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_06_models_dropdown_switches_to_model_convention_view(page, result):
    case = Case(
        page, "FullDta_06", FEATURE, "The 'Models' dropdown switches the table to a Model Tax Convention view",
        description="Clicking 'Models' then 'OECD' must replace the per-jurisdiction DTA table with the "
                     "OECD Model Tax Convention list (the 'Model Tax Conventions: OECD' heading becomes "
                     "visible).",
        precondition="User is logged in and on Full DTA.",
        test_data="Model: OECD",
        steps="1. Log in and open Full DTA\n2. Click 'Models', then 'OECD'\n"
              "3. Verify the Model Tax Convention view is shown",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Open Models and select OECD")
    case.click(fd.models_button, "'Models' dropdown button")
    wait_for_content(fd.model_oecd)
    case.click(fd.model_oecd, "'OECD' model option")
    # NOTE: a plain get_by_text("Model Tax Convention", exact=False) matches
    # TWO elements live - the "Model Tax Conventions: OECD" page heading AND
    # the (singular, no colon) "Model Tax Convention" table column header -
    # which is a Playwright strict-mode violation. Target the unique,
    # plural/colon heading text instead so the locator resolves to exactly
    # one element.
    model_text = page.get_by_text("Model Tax Conventions: OECD", exact=False)
    wait_for_content(model_text, timeout=15000)

    case.step(3, "Verify the Model Tax Convention view")
    ok = case.verify_visible(model_text, "'Model Tax Conventions: OECD' heading")
    case.check("Model Tax Convention view is shown after selecting 'OECD'", ok,
               expected=True, actual=ok)

    actual = ("Selecting 'OECD' from the Models dropdown switched the page to the OECD Model Tax Convention "
              "view." if ok else "Selecting 'OECD' from the Models dropdown did not switch to the expected view.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_07_view_link_opens_full_document_viewer(page, result):
    case = Case(
        page, "FullDta_07", FEATURE, "A row's 'View' link opens the full treaty document viewer",
        description="With Australia selected, clicking the Austria row's 'View' link (previously defined in "
                     "the page object but never clicked by any test) must replace the table with the full "
                     "document viewer - a 'Contents' sidebar and the treaty pair's title.",
        precondition="User is logged in, Australia selected on Full DTA.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in and open Full DTA\n2. Select Australia\n"
              "3. Click the Austria row's 'View' link\n"
              "4. Verify the document viewer's 'Contents' sidebar and treaty title are shown",
    )
    fd = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(fd.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(fd.table)

    case.step(3, "Click the Austria row's 'View' link")
    view_link = fd.view_link_in_row("Austria")
    link_present = view_link.count() >= 1
    if link_present:
        case.click(view_link.first, "'View' link (Austria row)")
        fd.viewer_contents_heading.wait_for(state="visible", timeout=10000)

    case.step(4, "Verify the document viewer")
    contents_ok = case.verify_visible(fd.viewer_contents_heading, "'Contents' sidebar heading") if link_present else False
    title_ok = case.verify_visible(page.get_by_text("Australia - Austria", exact=True), "'Australia - Austria' title") \
        if link_present else False
    ok = link_present and contents_ok and title_ok
    case.check("The 'View' link opens the full document viewer with the correct title and Contents sidebar", ok,
               expected="link_present=True, contents_ok=True, title_ok=True",
               actual=f"link_present={link_present}, contents_ok={contents_ok}, title_ok={title_ok}")

    actual = ("The Austria row's 'View' link correctly opened the full document viewer." if ok else
              f"The 'View' link did not open the expected viewer (link_present={link_present}, "
              f"contents_ok={contents_ok}, title_ok={title_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_fulldta_08_viewer_export_pdf_downloads(page, result):
    case = Case(
        page, "FullDta_08", FEATURE, "The document viewer's Export button downloads a real, non-empty PDF",
        description="With the Austria document viewer open (Australia selected), clicking 'Export as PDF' must "
                     "trigger a real download with no failure and a non-zero size.",
        precondition="User is logged in, Australia selected, Austria's document viewer open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Full DTA, select Australia\n2. Open the Austria document viewer\n"
              "3. Click the 'Export as PDF' button\n4. Verify a real, non-empty PDF download completed",
    )
    fd = _login_and_open(case, page)
    case.click(fd.jurisdiction.country_checkbox("Australia"), "'Australia' jurisdiction")
    wait_for_content(fd.table)
    view_link = fd.view_link_in_row("Austria")
    case.click(view_link.first, "'View' link (Austria row)")
    fd.viewer_contents_heading.wait_for(state="visible", timeout=10000)

    case.step(3, "Click the 'Export as PDF' button")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(fd.viewer_export_pdf_button.first, "'Export as PDF' button")
    download = dl_info.value

    case.step(4, "Verify the PDF download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith(".pdf") and size > 0
    case.check("The document viewer's Export button downloads a real, non-empty .pdf file with no failure", ok,
               expected="failure=None, filename ends with .pdf, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The Export button downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"The Export button did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual
