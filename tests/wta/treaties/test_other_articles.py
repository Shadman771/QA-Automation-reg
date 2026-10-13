"""Treaties > Other Articles (/wta/OtherArticles). See
pages/treaties_other_articles_page.py for the full confirmed-live layout
notes."""
import os

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


def _select_country(case, oa, country: str):
    """Types into 'Search countries' first so this works regardless of
    which region tab is active by default - confirmed live: 'Canada' and
    'Germany' are NOT in the default 'Asia Pacific' region tab, so looking
    up their `<label>` directly (as Australia's test does) times out with
    'element is not visible' unless the country list is first filtered down
    to just that country via search."""
    case.fill(oa.jurisdiction.search_countries, country, "'Search countries' box")
    page = oa.page
    page.wait_for_timeout(600)
    case.click(oa.jurisdiction.country_checkbox(country), f"'{country}' jurisdiction")
    wait_for_content(oa.table)


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


@pytest.mark.regression
def test_otherarticles_06_article_link_opens_detail_modal(page, result):
    case = Case(
        page, "OtherArticles_06", FEATURE, "Clicking an article-reference link opens the treaty article modal",
        description="With Australia selected, clicking the 'Art. 4(4)' link in the Austria row's 'Tie Breaker "
                     "Corporate' column must open a modal titled 'Treaty between Australia and Austria' showing "
                     "the Article 4(4) text.",
        precondition="User is logged in, Australia selected on Other Articles.",
        test_data="Country: Australia, partner: Austria, column: Tie Breaker Corporate",
        steps="1. Log in and open Other Articles\n2. Select Australia\n"
              "3. Click the 'Art. 4(4)' link in the Austria row\n4. Verify the article modal title and content",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Australia")
    _select_country(case, oa, "Australia")

    case.step(3, "Click the Austria row's Tie Breaker Corporate article link")
    link = oa.article_link_in_row("Austria", 1)
    link_present = link.count() >= 1
    if link_present:
        case.click(link.first, "'Art. 4(4)' article link (Austria row)")
        oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(4, "Verify the modal title and article text")
    title = oa.article_modal_title.first.inner_text() if link_present else ""
    body_text = oa.article_modal_body_text.first.inner_text() if link_present else ""
    title_ok = "Treaty between Australia and Austria" in title
    body_ok = "Article 4(4)" in body_text
    ok = link_present and title_ok and body_ok
    case.check("The article modal opens with the correct treaty title and article text", ok,
               expected="title contains 'Treaty between Australia and Austria', body contains 'Article 4(4)'",
               actual=f"link_present={link_present}, title={title!r}, body contains Article 4(4)={body_ok}",
               locator=oa.article_modal_title.first if link_present else None)

    if link_present:
        case.click(oa.article_modal_ok_button, "'OK' button (close modal)")

    actual = (f"Clicking the Austria article link correctly opened the modal ({title!r})." if ok else
              f"The article modal did not open/match as expected (link_present={link_present}, title={title!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_07_article_modal_pdf_export_downloads(page, result):
    case = Case(
        page, "OtherArticles_07", FEATURE, "The article modal's PDF export downloads a real, non-empty file",
        description="With the Austria article modal open (Australia selected), clicking 'PDF' under Export must "
                     "trigger a real file download with no failure and a non-zero size.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Other Articles, select Australia\n2. Open the Austria article modal\n"
              "3. Click 'PDF' under Export\n4. Verify a real, non-empty PDF download completed",
    )
    oa = _login_and_open(case, page)
    _select_country(case, oa, "Australia")
    link = oa.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 4(4)' article link (Austria row)")
    oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click 'PDF' under Export")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(oa.article_modal_export_pdf.first, "'PDF' export action")
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

    case.click(oa.article_modal_ok_button, "'OK' button (close modal)")
    actual = (f"PDF export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"PDF export did not produce a valid download (failure={failure}, filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_08_article_modal_word_export_downloads(page, result):
    case = Case(
        page, "OtherArticles_08", FEATURE, "The article modal's Word export downloads a real, non-empty file",
        description="With the Austria article modal open (Australia selected), clicking 'Word' under Export must "
                     "trigger a real file download with no failure and a non-zero size.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Other Articles, select Australia\n2. Open the Austria article modal\n"
              "3. Click 'Word' under Export\n4. Verify a real, non-empty Word download completed",
    )
    oa = _login_and_open(case, page)
    _select_country(case, oa, "Australia")
    link = oa.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 4(4)' article link (Austria row)")
    oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click 'Word' under Export")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(oa.article_modal_export_word.first, "'Word' export action")
    download = dl_info.value

    case.step(4, "Verify the Word download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith((".doc", ".docx")) and size > 0
    case.check("The Word export downloads a real, non-empty .doc(x) file with no failure", ok,
               expected="failure=None, filename ends with .doc/.docx, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    case.click(oa.article_modal_ok_button, "'OK' button (close modal)")
    actual = (f"Word export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"Word export did not produce a valid download (failure={failure}, filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_09_article_modal_print_opens_preview_tab(page, result):
    case = Case(
        page, "OtherArticles_09", FEATURE, "The article modal's Print action opens a print-preview tab with the "
                                            "expected content",
        description="With the Austria article modal open (Australia selected), clicking 'Print' under Export must "
                     "open a NEW browser tab showing a print-preview rendering of the treaty name and article "
                     "text. The test verifies the preview content and closes the tab - it never clicks any actual "
                     "'Print' confirmation control.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Other Articles, select Australia\n2. Open the Austria article modal\n"
              "3. Click 'Print' under Export\n4. Verify the new print-preview tab shows the treaty name and "
              "article text, then close it",
    )
    oa = _login_and_open(case, page)
    _select_country(case, oa, "Australia")
    link = oa.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 4(4)' article link (Austria row)")
    oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click 'Print' under Export")
    with page.context.expect_page(timeout=10000) as new_page_info:
        case.click(oa.article_modal_export_print.first, "'Print' export action")
    preview_page = new_page_info.value
    preview_page.wait_for_load_state("load", timeout=10000)
    preview_page.wait_for_timeout(500)

    case.step(4, "Verify the print-preview content, then close the tab (no Print button clicked)")
    preview_text = preview_page.inner_text("body")
    ok = "Australia" in preview_text and "Austria" in preview_text and "Article 4(4)" in preview_text
    case.check("The print-preview tab shows the treaty name and Article 4(4) text", ok,
               expected="preview body contains 'Australia', 'Austria' and 'Article 4(4)'",
               actual=f"preview_url={preview_page.url}, preview_text_snippet={preview_text[:200]!r}")
    preview_page.close()

    case.click(oa.article_modal_ok_button, "'OK' button (close article modal)")
    actual = ("The Print action correctly opened a print-preview tab with the expected treaty/article content "
              "(no Print confirmation control was clicked)." if ok else
              f"The print-preview tab did not show the expected content (snippet={preview_text[:200]!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_10_full_dta_link_opens_full_document_viewer(page, result):
    case = Case(
        page, "OtherArticles_10", FEATURE, "The article modal's 'Full DTA' link swaps in the full document viewer",
        description="With the Austria article modal open (Australia selected), clicking the 'Full DTA' link in "
                     "the modal header must swap the modal's content for the full DTA document viewer - a "
                     "'Contents' sidebar listing every treaty article.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Other Articles, select Australia\n2. Open the Austria article modal\n"
              "3. Click the 'Full DTA' link\n4. Verify the 'Contents' sidebar with article entries is shown",
    )
    oa = _login_and_open(case, page)
    _select_country(case, oa, "Australia")
    link = oa.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 4(4)' article link (Austria row)")
    oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click the 'Full DTA' link")
    case.click(oa.article_modal_full_dta_link.first, "'Full DTA' link")
    page.wait_for_timeout(1000)

    case.step(4, "Verify the Contents sidebar of the full document viewer")
    contents_ok = case.verify_visible(oa.full_dta_contents_heading, "'Contents' sidebar heading")
    list_count = oa.full_dta_contents_list_items.count()
    ok = contents_ok and list_count > 5
    case.check("The 'Full DTA' link swaps in the full document viewer with a populated Contents sidebar", ok,
               expected="'Contents' heading visible, article list items > 5",
               actual=f"contents_ok={contents_ok}, list_count={list_count}",
               locator=oa.full_dta_contents_heading if contents_ok else None)

    actual = (f"The 'Full DTA' link correctly opened the full document viewer ({list_count} article entries)."
              if ok else f"The 'Full DTA' link did not open the expected viewer (contents_ok={contents_ok}, "
              f"list_count={list_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_11_article_modal_close_x_dismisses(page, result):
    case = Case(
        page, "OtherArticles_11", FEATURE, "The article modal's header X button closes it",
        description="With the Austria article modal open (Australia selected), clicking the header X close "
                     "button must dismiss the modal.",
        precondition="User is logged in, Australia selected, Austria's article modal open.",
        test_data="Country: Australia, partner: Austria",
        steps="1. Log in, open Other Articles, select Australia\n2. Open the Austria article modal\n"
              "3. Click the header X close button\n4. Verify the modal is no longer visible",
    )
    oa = _login_and_open(case, page)
    _select_country(case, oa, "Australia")
    link = oa.article_link_in_row("Austria", 1)
    case.click(link.first, "'Art. 4(4)' article link (Austria row)")
    oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)

    case.step(3, "Click the header X close button")
    case.click(oa.article_modal_close_x.first, "modal header X close button")
    page.wait_for_timeout(500)

    case.step(4, "Verify the modal is dismissed")
    still_visible = oa.article_modal_wrapper.first.is_visible() if oa.article_modal_wrapper.count() else False
    ok = not still_visible
    case.check("The article modal is no longer visible after clicking the X close button", ok,
               expected=False, actual=still_visible)

    actual = ("The header X button correctly closed the article modal." if ok else
              "The article modal remained visible after clicking the X close button.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_12_table_export_excel_downloads(page, result):
    case = Case(
        page, "OtherArticles_12", FEATURE, "The table-level 'Export as Excel' button downloads the whole table",
        description="With Australia selected (no article link clicked), clicking the table's 'Export as Excel' "
                     "icon button must trigger a real, non-empty .xlsx download.",
        precondition="User is logged in, Australia selected on Other Articles.",
        test_data="Country: Australia",
        steps="1. Log in and open Other Articles\n2. Select Australia\n"
              "3. Click the 'Export as Excel' icon button\n4. Verify a real, non-empty .xlsx download completed",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Australia")
    _select_country(case, oa, "Australia")

    case.step(3, "Click the 'Export as Excel' button")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(oa.export_excel_button.first, "'Export as Excel' button")
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


@pytest.mark.regression
def test_otherarticles_13_second_country_canada_article_modal_and_pdf(page, result):
    case = Case(
        page, "OtherArticles_13", FEATURE, "Article link + PDF export work correctly for a second country (Canada)",
        description="With Canada selected, clicking the Algeria row's Tie Breaker Corporate article link must "
                     "open the correctly-titled modal, and its PDF export must download a real, non-empty file - "
                     "confirming the behavior is not Australia-specific.",
        precondition="User is logged in and on Other Articles.",
        test_data="Country: Canada, partner: Algeria",
        steps="1. Log in and open Other Articles\n2. Select Canada\n"
              "3. Click the Algeria row's article link and verify the modal title\n"
              "4. Click 'PDF' under Export and verify a real download",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Canada")
    _select_country(case, oa, "Canada")

    case.step(3, "Click the Algeria row's article link and verify the modal")
    link = oa.article_link_in_row("Algeria", 1)
    link_present = link.count() >= 1
    title = ""
    if link_present:
        case.click(link.first, "article link (Algeria row)")
        oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)
        title = oa.article_modal_title.first.inner_text()
    title_ok = "Treaty between Canada and Algeria" in title

    case.step(4, "Click 'PDF' under Export and verify a real download")
    filename, failure, size = "", "not attempted", 0
    if title_ok:
        with page.expect_download(timeout=15000) as dl_info:
            case.click(oa.article_modal_export_pdf.first, "'PDF' export action")
        download = dl_info.value
        filename = download.suggested_filename
        failure = download.failure()
        path = download.path()
        size = os.path.getsize(path) if path else 0
        case.click(oa.article_modal_ok_button, "'OK' button (close modal)")

    ok = link_present and title_ok and failure is None and filename.lower().endswith(".pdf") and size > 0
    case.check("Canada's article modal and PDF export both work correctly", ok,
               expected="title contains 'Treaty between Canada and Algeria', PDF download succeeds",
               actual=f"title={title!r}, filename={filename!r}, failure={failure}, size={size}")

    actual = (f"Canada's article link/modal/PDF export all worked correctly ('{filename}', {size} bytes)."
              if ok else f"Canada's article link/modal/PDF export did not behave as expected "
              f"(title={title!r}, failure={failure}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_14_third_country_germany_article_modal_and_pdf(page, result):
    case = Case(
        page, "OtherArticles_14", FEATURE, "Article link + PDF export work correctly for a third country (Germany)",
        description="With Germany selected, clicking the Albania row's Tie Breaker Corporate article link must "
                     "open the correctly-titled modal, and its PDF export must download a real, non-empty file - "
                     "confirming the behavior generalizes across countries.",
        precondition="User is logged in and on Other Articles.",
        test_data="Country: Germany, partner: Albania",
        steps="1. Log in and open Other Articles\n2. Select Germany\n"
              "3. Click the Albania row's article link and verify the modal title\n"
              "4. Click 'PDF' under Export and verify a real download",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Germany")
    _select_country(case, oa, "Germany")

    case.step(3, "Click the Albania row's article link and verify the modal")
    link = oa.article_link_in_row("Albania", 1)
    link_present = link.count() >= 1
    title = ""
    if link_present:
        case.click(link.first, "article link (Albania row)")
        oa.article_modal_wrapper.first.wait_for(state="visible", timeout=10000)
        title = oa.article_modal_title.first.inner_text()
    title_ok = "Treaty between Germany and Albania" in title

    case.step(4, "Click 'PDF' under Export and verify a real download")
    filename, failure, size = "", "not attempted", 0
    if title_ok:
        with page.expect_download(timeout=15000) as dl_info:
            case.click(oa.article_modal_export_pdf.first, "'PDF' export action")
        download = dl_info.value
        filename = download.suggested_filename
        failure = download.failure()
        path = download.path()
        size = os.path.getsize(path) if path else 0
        case.click(oa.article_modal_ok_button, "'OK' button (close modal)")

    ok = link_present and title_ok and failure is None and filename.lower().endswith(".pdf") and size > 0
    case.check("Germany's article modal and PDF export both work correctly", ok,
               expected="title contains 'Treaty between Germany and Albania', PDF download succeeds",
               actual=f"title={title!r}, filename={filename!r}, failure={failure}, size={size}")

    actual = (f"Germany's article link/modal/PDF export all worked correctly ('{filename}', {size} bytes)."
              if ok else f"Germany's article link/modal/PDF export did not behave as expected "
              f"(title={title!r}, failure={failure}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_otherarticles_15_none_cell_has_no_clickable_article_link(page, result):
    case = Case(
        page, "OtherArticles_15", FEATURE, "A cell with no treaty article coverage ('None') has no clickable link",
        description="With Australia selected, Belgium's 'Other Income' cell shows plain 'None' text with no "
                     "linked article - clicking it must not open any modal. This is the genuine negative case "
                     "for the article-link feature.",
        precondition="User is logged in, Australia selected on Other Articles.",
        test_data="Country: Australia, partner: Belgium, column: Other Income",
        steps="1. Log in and open Other Articles\n2. Select Australia\n"
              "3. Verify Belgium's 'Other Income' cell has no '.reg-link-button' article link\n"
              "4. Verify no article modal opens",
    )
    oa = _login_and_open(case, page)
    case.step(2, "Select Australia")
    _select_country(case, oa, "Australia")

    case.step(3, "Verify Belgium's Other Income cell has no article link")
    none_cell = oa.none_cell_in_row("Belgium", 3)
    none_visible = case.verify_visible(none_cell, "Belgium 'Other Income' cell ('None')")
    no_link = oa.article_link_in_row("Belgium", 3).count() == 0

    case.step(4, "Verify no article modal is present")
    no_modal = oa.article_modal_wrapper.count() == 0

    ok = none_visible and no_link and no_modal
    case.check("Belgium's 'Other Income' cell shows plain 'None' text with no clickable article link", ok,
               expected="none_visible=True, no_link=True, no_modal=True",
               actual=f"none_visible={none_visible}, no_link={no_link}, no_modal={no_modal}",
               locator=none_cell if none_visible else None)

    actual = ("Belgium's 'Other Income' cell correctly shows plain 'None' text with no clickable article link "
              "(genuine no-coverage case)." if ok else
              f"Belgium's 'Other Income' cell did not behave as the expected no-link case "
              f"(none_visible={none_visible}, no_link={no_link}, no_modal={no_modal}).")
    result(case, actual, ok)
    assert ok, actual
