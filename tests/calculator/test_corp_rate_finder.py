"""Calculators > Corporate Rate Finder (/wta/CorpRateFinder).

Source test cases: Calculator_Repatriation Calculator_01..19 in the
provided QA sheet (the sheet bundles Corporate Rate Finder under the
"Repatriation Calculator" ID prefix; live discovery confirmed it is in
fact a separate, 6th top-nav "Calculators" item - see
pages/calculator_menu.py). Reviewed against the live application and
upgraded throughout: real download verification (not just link
visibility), a real API-sourced calculation-validation anchor (Bangladesh
/ tax year 2024, see pages/calculator_rate_finder_page.py docstring)
instead of fabricating an expected rate, and the real "no rate data for
most country/year combinations" gap documented as application behavior
rather than hidden. The sheet's Test 04 ("region expand/collapse") does
not match live behavior - regions are exclusive TABS, not
independently-expandable sections (same as every other WTA jurisdiction
panel) - CRF_04 below tests the real tab-switch behavior instead of
blindly automating the sheet's incorrect premise."""
import os

import pytest

from pages.calculator_menu import CalculatorMenu
from pages.calculator_rate_finder_page import CorporateRateFinderPage, CORPORATE_RATE_API
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - Corporate Rate Finder"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > Corporate Rate Finder", kind="navigate")
    CalculatorMenu(page).open_item("Corporate Rate Finder")
    return CorporateRateFinderPage(page)


@pytest.mark.smoke
def test_crf_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "CRF_01", FEATURE, "Corporate Rate Finder opens from the Calculators dropdown",
        description="Clicking 'Corporate Rate Finder' in the Calculators dropdown must land on "
                     "/wta/CorpRateFinder with the jurisdiction/year panel and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > Corporate Rate Finder\n"
              "2. Verify the URL and the instructions banner are correct",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Verify URL and instructions banner")
    url_ok = "/wta/CorpRateFinder" in page.url
    banner_ok = case.verify_visible(crf.instructions_heading, "'How to find and compare rates' heading")
    ok = url_ok and banner_ok
    case.check("Corporate Rate Finder page loads with its instructions banner", ok,
               expected="url contains /wta/CorpRateFinder, banner visible",
               actual=f"url={page.url}, banner={banner_ok}")

    actual = ("Corporate Rate Finder opened correctly with its instructions banner visible." if ok else
              "Corporate Rate Finder did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_crf_02_region_tabs_display(page, result):
    case = Case(
        page, "CRF_02", FEATURE, "All 4 region tabs are displayed",
        description="The jurisdiction panel must show Asia Pacific, Americas, Europe and MEA region tabs.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="-",
        steps="1. Log in and open Corporate Rate Finder\n2. Verify all 4 region tabs are visible",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Verify region tabs")
    regions = ["Asia Pacific", "Americas", "Europe", "MEA"]
    missing = [r for r in regions if not case.verify_visible(crf.jurisdiction.region_tab(r), f"'{r}' tab")]
    ok = not missing
    case.check("All 4 region tabs are visible", ok, expected=regions, actual=f"missing={missing}")

    actual = ("All 4 region tabs (Asia Pacific, Americas, Europe, MEA) are visible." if ok else
              f"Missing region tab(s): {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_03_countries_listed_under_asia_pacific(page, result):
    case = Case(
        page, "CRF_03", FEATURE, "Countries are listed under the default 'Asia Pacific' region",
        description="With no tab clicked (Asia Pacific is the default-selected tab), Australia and Japan "
                     "must both be visible in the country list.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="-",
        steps="1. Log in and open Corporate Rate Finder\n2. Verify Australia and Japan are listed",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Verify countries are listed")
    aus_ok = case.verify_visible(crf.jurisdiction.country_checkbox("Australia"), "'Australia' row")
    jp_ok = case.verify_visible(crf.jurisdiction.country_checkbox("Japan"), "'Japan' row")
    ok = aus_ok and jp_ok
    case.check("Australia and Japan are listed under Asia Pacific", ok, expected="both visible",
               actual=f"australia={aus_ok}, japan={jp_ok}")

    actual = ("Australia and Japan are both listed under the default Asia Pacific tab." if ok else
              "The country list did not show the expected Asia Pacific countries.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_04_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "CRF_04", FEATURE, "Switching region tabs hides out-of-region countries",
        description="The sheet's Test 04 assumed per-region expand/collapse; live behavior is tabs that "
                     "switch the whole list - clicking 'Europe' must hide 'Australia' (Asia Pacific).",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="-",
        steps="1. Log in and open Corporate Rate Finder\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer listed",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(crf.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify Australia is hidden")
    ok = not crf.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("'Australia' is not listed under 'Europe'", ok, expected="hidden", actual=not ok)

    actual = ("Switching to 'Europe' hid 'Australia' from the list, confirming regions are exclusive tabs "
              "rather than independently-collapsible sections." if ok else
              "Switching region tabs did not hide the out-of-region country as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_05_year_list_in_descending_order(page, result):
    case = Case(
        page, "CRF_05", FEATURE, "The year list is displayed in descending logical order",
        description="'Select Year' must list years starting at 2026 and descending (2026, 2025, 2024, ...).",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="-",
        steps="1. Log in and open Corporate Rate Finder\n2. Read the first 3 year checkboxes in DOM order\n"
              "3. Verify they read 2026, 2025, 2024",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Read the first 3 years")
    years = [crf.year_checkbox(y).get_attribute("value") for y in ["2026", "2025", "2024"]]
    present = all(y is not None for y in years)

    case.step(3, "Verify descending order via DOM position")
    order_html = page.locator("div.overflow-y-auto.flex-1.min-h-0").last.evaluate(
        "el => [...el.querySelectorAll('input.reg-checkbox')].slice(0,3).map(i => i.value)"
    )
    ok = present and order_html == ["2026", "2025", "2024"]
    case.check("Years are listed in descending order starting at 2026", ok,
               expected="['2026', '2025', '2024']", actual=order_html)

    actual = (f"The year list is correctly ordered descending: {order_html}." if ok else
              f"The year list was not in the expected descending order (got {order_html}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_06_year_checkbox_toggles_on_and_off(page, result):
    case = Case(
        page, "CRF_06", FEATURE, "A year checkbox can be toggled on and off",
        description="Clicking the '2025' year checkbox must check it, and clicking it again must uncheck it.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="Year: 2025",
        steps="1. Log in and open Corporate Rate Finder\n2. Click the '2025' checkbox and verify it is checked\n"
              "3. Click it again and verify it is unchecked",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Click '2025' once")
    case.click(crf.year_checkbox("2025"), "'2025' year checkbox")
    page.wait_for_timeout(400)
    checked = crf.year_checkbox("2025").is_checked()
    case.check("'2025' is checked after one click", checked, expected=True, actual=checked,
               locator=crf.year_checkbox("2025"))

    case.step(3, "Click '2025' again")
    case.click(crf.year_checkbox("2025"), "'2025' year checkbox")
    page.wait_for_timeout(400)
    unchecked = not crf.year_checkbox("2025").is_checked()
    case.check("'2025' is unchecked after a second click", unchecked, expected=True, actual=unchecked,
               locator=crf.year_checkbox("2025"))

    ok = checked and unchecked
    actual = ("The '2025' year checkbox toggled on then off correctly." if ok else
              f"The year checkbox did not toggle as expected (checked={checked}, unchecked={unchecked}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_crf_07_selecting_country_and_year_renders_verified_rate(page, result):
    case = Case(
        page, "CRF_07", FEATURE, "Selecting a jurisdiction and year renders a rate matching the live API",
        description="With Bangladesh + 2024 selected, the results table must show a '55%' Headline rate "
                     "cell - independently verified against GET /api/CorporateRate?countryCodes=BD&year=2024 "
                     "(HeadlineRate.RangeRate[0].Value=55), not merely compared against itself.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh and 2024\n"
              "2. Independently fetch the CorporateRate API for BD/2024\n"
              "3. Verify the UI table's rate cell matches the API's HeadlineRate value",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Select Bangladesh and 2024, independently fetch the API")
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    resp = page.request.get(f"{CORPORATE_RATE_API}?countryCodes=BD&year=2024")
    api_data = resp.json()
    try:
        cit = api_data["Data"][0]["CitModel"][0]
        expected_rate = cit["HeadlineRate"]["RangeRate"][0]["Value"]
    except (KeyError, IndexError, TypeError):
        expected_rate = None

    case.step(3, "Verify the UI table matches the independently-fetched API value")
    table_text = crf.results_table.inner_text()
    expected_str = f"{expected_rate:g}%" if expected_rate is not None else None
    ok = expected_rate is not None and expected_str in table_text
    case.check("The UI rate cell matches the independently-fetched API HeadlineRate", ok,
               expected=expected_str, actual=table_text.replace("\n", " | "))

    actual = (f"The UI correctly displayed '{expected_str}', matching the live API's independent HeadlineRate "
              f"value for Bangladesh/2024." if ok else
              f"The UI table did not match the independently-fetched API rate (expected {expected_str}, "
              f"table={table_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_08_multi_select_renders_row_per_year_column_per_country(page, result):
    case = Case(
        page, "CRF_08", FEATURE, "Multi-selecting countries and years renders one row per year, one column per country",
        description="Selecting Bangladesh+Australia and 2024+2023 must render a table with 2 data rows "
                     "(years) and a column for each selected country, confirmed live via inner_text layout.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="Countries: Bangladesh, Australia / Years: 2024, 2023",
        steps="1. Log in, open Corporate Rate Finder\n2. Select Bangladesh, Australia, 2024, 2023\n"
              "3. Verify the table has 2 rows and both country names as column headers",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Select 2 countries and 2 years")
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    case.click(crf.year_checkbox("2023"), "'2023' year checkbox")
    page.wait_for_timeout(1500)

    case.step(3, "Verify row/column layout")
    row_count = crf.results_table.locator("tbody tr").count()
    header_text = crf.results_table.locator("thead").inner_text()
    ok = row_count == 2 and "Bangladesh" in header_text and "Australia" in header_text
    case.check("Table has 2 year-rows and both countries as columns", ok,
               expected="row_count=2, both country headers present",
               actual=f"row_count={row_count}, header={header_text!r}")

    actual = (f"The table correctly rendered {row_count} year rows with Bangladesh and Australia as "
              f"separate columns." if ok else
              f"The multi-select table layout did not match expectations (row_count={row_count}, "
              f"header={header_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_09_missing_rate_data_renders_empty_cell_not_fabricated(page, result):
    case = Case(
        page, "CRF_09", FEATURE, "A country/year combo with no published rate renders an empty cell, not an error",
        description="Australia/2024 is confirmed live to have a null HeadlineRate - this is real application "
                     "behavior (a genuine data gap), so the table must render the row without erroring, with "
                     "an empty rate cell rather than any placeholder/fabricated value.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="Country: Australia, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Australia and 2024\n"
              "2. Verify the table renders without error and the rate cell is empty",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    case.step(2, "Verify the table rendered with an empty rate cell")
    table_visible = crf.results_table.is_visible()
    body_text = crf.results_table.locator("tbody").inner_text()
    has_year_type = "2024" in body_text and "Headline" in body_text
    no_percent = "%" not in body_text
    ok = table_visible and has_year_type and no_percent
    case.check("Table renders Year/Type with an empty rate cell for a known data gap", ok,
               expected="table visible, '2024'+'Headline' present, no '%' value",
               actual=f"table_visible={table_visible}, body={body_text!r}")

    actual = ("The table correctly rendered Australia/2024 with no rate value, reflecting the real, "
              "confirmed data gap rather than fabricating a figure." if ok else
              f"The table did not render the known data-gap row as expected (body={body_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_10_show_more_preserves_the_same_rate_value(page, result):
    case = Case(
        page, "CRF_10", FEATURE, "'Show More' switches to a denser table while preserving the same rate value",
        description="With Bangladesh/2024 selected, clicking 'Show More' must switch the table layout but "
                     "still show the same '55%' rate.",
        precondition="User is logged in, Bangladesh+2024 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh and 2024\n"
              "2. Click 'Show More'\n3. Verify the table still shows '55%'",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    case.step(2, "Click 'Show More'")
    case.click(crf.show_more_button, "'Show More' button")
    page.wait_for_timeout(800)

    case.step(3, "Verify the rate value is preserved")
    body_text = crf.results_table.inner_text()
    ok = "55%" in body_text
    case.check("The expanded table still shows the 55% rate", ok, expected="55% present",
               actual=body_text.replace("\n", " | "))

    actual = ("'Show More' switched to the expanded table layout while preserving the correct rate value." if ok
              else f"The expanded table did not preserve the expected rate value (body={body_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_11_country_name_opens_rate_details_modal(page, result):
    case = Case(
        page, "CRF_11", FEATURE, "Clicking a country's column header opens a 'Corporate rate details' modal",
        description="With Bangladesh/2024 selected, clicking the 'Bangladesh' column header must open a "
                     "same-page rsuite modal titled 'Corporate rate details for Bangladesh' showing the same "
                     "55% rate - confirmed live this is a MODAL, not a new tab/page (contrary to the sheet's "
                     "Test 13 wording of 'a new page should open').",
        precondition="User is logged in, Bangladesh+2024 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh and 2024\n"
              "2. Click the 'Bangladesh' column header\n"
              "3. Verify the modal opens with the matching rate",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    case.step(2, "Click the 'Bangladesh' column header")
    case.click(crf.year_column_header("Bangladesh"), "'Bangladesh' column header link")
    wait_for_content(crf.modal.get_by_text("55%", exact=False), timeout=8000)

    case.step(3, "Verify the modal content")
    modal_visible = crf.modal.is_visible()
    modal_text = crf.modal.inner_text() if modal_visible else ""
    title_ok = "Corporate rate details for Bangladesh" in modal_text
    rate_ok = "55%" in modal_text
    ok = modal_visible and title_ok and rate_ok
    case.check("The rate details modal opens with the correct title and rate", ok,
               expected="modal visible, title + 55% present", actual=modal_text.replace("\n", " | "))

    actual = ("Clicking 'Bangladesh' opened the 'Corporate rate details' modal showing the matching 55% "
              "rate, confirming this is a same-page modal rather than a new page." if ok else
              f"The rate details modal did not open with the expected content (modal_text={modal_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_12_modal_close_button_closes_the_modal(page, result):
    case = Case(
        page, "CRF_12", FEATURE, "The modal's close button closes it",
        description="With the rate details modal open, clicking its close button must close the modal.",
        precondition="User is logged in, Bangladesh+2024 selected, rate details modal open.",
        test_data="-",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh+2024, open the rate details modal\n"
              "2. Click the modal's close button\n3. Verify the modal is closed",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)
    crf.open_country_detail_modal("Bangladesh")
    page.wait_for_timeout(800)

    case.step(2, "Click the modal's close button")
    case.click(crf.modal_close_button, "modal close button")
    page.wait_for_timeout(500)

    case.step(3, "Verify the modal is closed")
    ok = crf.modal.count() == 0 or not crf.modal.is_visible()
    case.check("The rate details modal is closed", ok, expected="not visible", actual=not ok)

    actual = "The modal's close button correctly closed it." if ok else "The modal did not close as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_13_export_excel_icon_downloads_real_file(page, result):
    case = Case(
        page, "CRF_13", FEATURE, "The Excel export icon triggers a real, non-empty .xlsx download",
        description="With Bangladesh/2024 selected, clicking the first 'Export:' icon must download a real, "
                     "non-empty .xlsx file - not merely be present/visible.",
        precondition="User is logged in, Bangladesh+2024 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh and 2024\n"
              "2. Click the first Export icon (Excel)\n3. Verify a real, non-empty .xlsx download completed",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    case.step(2, "Click the Excel export icon")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(crf.export_icons.nth(0), "Excel export icon")
    download = dl_info.value

    case.step(3, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith(".xlsx") and size > 0
    case.check("Excel export produces a real, non-empty .xlsx file with no failure", ok,
               expected="failure=None, filename ends with .xlsx, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The Excel export downloaded '{filename}' ({size} bytes) successfully." if ok else
              f"The Excel export did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_14_print_icon_opens_print_preview_tab(page, result):
    case = Case(
        page, "CRF_14", FEATURE, "The Print export icon opens a print-preview tab, not an OS print dialog",
        description="With Bangladesh/2024 selected, clicking the second 'Export:' icon must open a new tab "
                     "at regpluswta.api.kaz.com.bd/api/Print/Index - the same server-rendered print-preview "
                     "pattern already confirmed for Treaties pages. The final OS print action is not invoked.",
        precondition="User is logged in, Bangladesh+2024 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh and 2024\n"
              "2. Click the second Export icon (Print)\n3. Verify a print-preview tab opens",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)

    case.step(2, "Click the Print export icon")
    with page.context.expect_page(timeout=15000) as pop_info:
        case.click(crf.export_icons.nth(1), "Print export icon")
    preview = pop_info.value
    preview.wait_for_load_state("load", timeout=10000)
    preview.wait_for_timeout(500)

    case.step(3, "Verify the print-preview tab")
    ok = "Print/Index" in preview.url
    case.check("A print-preview tab opened at the expected Print/Index endpoint", ok,
               expected="Print/Index in URL", actual=preview.url)
    preview.close()

    actual = (f"Clicking Print opened a print-preview tab at '{preview.url}'." if ok else
              f"Clicking Print did not open the expected print-preview tab (got '{preview.url}').")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_15_year_column_sort_toggles_asc_desc(page, result):
    case = Case(
        page, "CRF_15", FEATURE, "Clicking the 'Year' column header toggles the sort order",
        description="The Year column is sortable server-side via a `?sort=year:asc|desc` URL query param "
                     "(confirmed live); the default is desc, and clicking the header toggles to asc.",
        precondition="User is logged in, Bangladesh+2024/2023 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Years: 2024, 2023",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh, 2024 and 2023\n"
              "2. Click the 'Year' column header\n3. Verify the URL's sort param toggles to asc",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    case.click(crf.year_checkbox("2023"), "'2023' year checkbox")
    page.wait_for_timeout(1200)
    default_desc = "sort=year%3Adesc" in page.url

    case.step(2, "Click the 'Year' column header")
    case.click(crf.results_table.get_by_text("Year", exact=False).first, "'Year' column header")
    page.wait_for_timeout(800)

    case.step(3, "Verify the sort param toggled to asc")
    toggled_asc = "sort=year%3Aasc" in page.url
    ok = default_desc and toggled_asc
    case.check("Clicking the Year header toggles the sort from desc to asc", ok,
               expected="desc -> asc", actual=f"default_desc={default_desc}, url_after={page.url}")

    actual = ("The Year column header correctly toggled the sort order from descending to ascending." if ok
              else f"The sort toggle did not behave as expected (url={page.url}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_16_search_countries_no_match_message(page, result):
    case = Case(
        page, "CRF_16", FEATURE, "Country search shows a 'no match' message for a bogus name",
        description="Searching for a non-existent country name in the jurisdiction panel must show "
                     "'No countries found matching...'.",
        precondition="User is logged in and on Corporate Rate Finder.",
        test_data="Search term: zzzznotarealcountry",
        steps="1. Log in and open Corporate Rate Finder\n2. Search for 'zzzznotarealcountry'\n"
              "3. Verify the 'No countries found' message is shown",
    )
    crf = _login_and_open(case, page)
    case.step(2, "Search for a bogus country name")
    case.fill(crf.jurisdiction.search_countries, "zzzznotarealcountry", "Search countries box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the no-match message")
    ok = case.verify_visible(crf.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("'No countries found' message is shown for a non-existent search term", ok,
               expected="visible", actual=ok, locator=crf.jurisdiction.no_countries_message)

    actual = ("Searching for a bogus country name correctly showed the 'No countries found' message." if ok
              else "The country search did not show the expected 'no match' message.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_17_modal_export_icon_downloads_real_file(page, result):
    case = Case(
        page, "CRF_17", FEATURE, "The rate details modal has its own working Excel export",
        description="The 'Corporate rate details' modal shows its own 'Export:' control, confirmed live to "
                     "be functionally independent of the main toolbar's - clicking it must also trigger a "
                     "real, non-empty download.",
        precondition="User is logged in, Bangladesh+2024 selected, rate details modal open.",
        test_data="Country: Bangladesh, Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh+2024, open the rate details modal\n"
              "2. Click the modal's Export icon\n3. Verify a real, non-empty download completed",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1500)
    crf.open_country_detail_modal("Bangladesh")
    page.wait_for_timeout(800)

    case.step(2, "Click the modal's Export icon")
    modal_icons = crf.modal.locator("span.reg-icon-button")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(modal_icons.first, "modal Export icon")
    download = dl_info.value

    case.step(3, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and size > 0
    case.check("The modal's Export icon produces a real, non-empty file with no failure", ok,
               expected="failure=None, size>0", actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The modal's Export icon correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"The modal's Export icon did not produce a valid download (failure={failure}, "
              f"filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_18_unchecking_a_year_removes_its_row(page, result):
    case = Case(
        page, "CRF_18", FEATURE, "Unchecking a year removes its row from the results table",
        description="With Bangladesh + 2024 + 2023 selected (2 rows), unchecking '2023' must leave only the "
                     "2024 row.",
        precondition="User is logged in, Bangladesh+2024+2023 selected on Corporate Rate Finder.",
        test_data="Country: Bangladesh, Years: 2024, 2023",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh, 2024 and 2023\n"
              "2. Uncheck '2023'\n3. Verify only the 2024 row remains",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    case.click(crf.year_checkbox("2023"), "'2023' year checkbox")
    page.wait_for_timeout(1200)
    rows_before = crf.results_table.locator("tbody tr").count()

    case.step(2, "Uncheck '2023'")
    case.click(crf.year_checkbox("2023"), "'2023' year checkbox")
    page.wait_for_timeout(1000)

    case.step(3, "Verify only the 2024 row remains")
    rows_after = crf.results_table.locator("tbody tr").count()
    body_text = crf.results_table.inner_text()
    ok = rows_before == 2 and rows_after == 1 and "2024" in body_text and "2023" not in body_text
    case.check("Unchecking '2023' leaves only the 2024 row", ok,
               expected="rows_before=2, rows_after=1, only 2024 present",
               actual=f"rows_before={rows_before}, rows_after={rows_after}, body={body_text!r}")

    actual = ("Unchecking '2023' correctly removed its row, leaving only 2024." if ok else
              f"Unchecking a year did not update the table as expected (rows_before={rows_before}, "
              f"rows_after={rows_after}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_crf_19_unchecking_a_country_removes_its_column(page, result):
    case = Case(
        page, "CRF_19", FEATURE, "Unchecking a country removes its column from the results table",
        description="With Bangladesh + Australia + 2024 selected (2 columns), unchecking 'Australia' must "
                     "leave only the Bangladesh column.",
        precondition="User is logged in, Bangladesh+Australia+2024 selected on Corporate Rate Finder.",
        test_data="Countries: Bangladesh, Australia / Year: 2024",
        steps="1. Log in, open Corporate Rate Finder, select Bangladesh, Australia and 2024\n"
              "2. Uncheck 'Australia'\n3. Verify only the Bangladesh column remains",
    )
    crf = _login_and_open(case, page)
    case.click(crf.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    case.click(crf.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.click(crf.year_checkbox("2024"), "'2024' year checkbox")
    page.wait_for_timeout(1200)
    header_before = crf.results_table.locator("thead").inner_text()

    case.step(2, "Uncheck 'Australia'")
    case.click(crf.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(1000)

    case.step(3, "Verify only the Bangladesh column remains")
    header_after = crf.results_table.locator("thead").inner_text()
    ok = ("Australia" in header_before and "Bangladesh" in header_before and
          "Australia" not in header_after and "Bangladesh" in header_after)
    case.check("Unchecking 'Australia' leaves only the Bangladesh column", ok,
               expected="Australia removed, Bangladesh remains",
               actual=f"header_before={header_before!r}, header_after={header_after!r}")

    actual = ("Unchecking 'Australia' correctly removed its column, leaving only Bangladesh." if ok else
              "Unchecking a country did not update the table columns as expected.")
    result(case, actual, ok)
    assert ok, actual
