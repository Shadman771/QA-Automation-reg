"""Treaties > MLI Data (/wta/MLIData). See pages/treaties_mli_data_page.py
for the full confirmed-live layout notes. Unlike the other 4 Treaties pages,
this one has NO jurisdiction panel - the table is server-rendered
immediately on load."""
import pytest

from pages.treaties_mli_data_page import MLIDataPage, MLI_DATA_HEADERS
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Treaties MLIData"


def _login_and_open(case, page):
    perform_login(case, page)
    mli = MLIDataPage(page)
    case.action("Navigating to /wta/MLIData", kind="navigate")
    mli.goto()
    return mli


@pytest.mark.smoke
def test_mlidata_01_page_loads_with_table_prerendered(page, result):
    case = Case(
        page, "MLIData_01", FEATURE, "MLI Data table renders immediately, with no jurisdiction panel required",
        description="Unlike the other Treaties pages, /wta/MLIData must render its full table on load, "
                     "with no country selection step, showing all 8 expected columns and more than 100 rows.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open MLI Data\n2. Verify the URL, the table headers, and the row count",
    )
    mli = _login_and_open(case, page)
    case.step(2, "Verify URL, headers and row count")
    url_ok = "/wta/MLIData" in page.url
    headers = mli.headers()
    headers_ok = headers == MLI_DATA_HEADERS
    row_count = mli.table_rows.count()
    rows_ok = row_count > 100
    ok = url_ok and headers_ok and rows_ok
    case.check("MLI Data table pre-renders with 8 expected columns and >100 rows", ok,
               expected=f"url_ok=True, headers={MLI_DATA_HEADERS}, rows>100",
               actual=f"url_ok={url_ok}, headers={headers}, rows={row_count}", locator=mli.table.first)

    actual = (f"MLI Data loaded at {page.url} with its table pre-rendered ({row_count} rows, expected "
              f"columns)." if ok else f"MLI Data did not load as expected (url_ok={url_ok}, headers={headers}, "
              f"rows={row_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_mlidata_02_first_row_matches_ascending_sort(page, result):
    case = Case(
        page, "MLIData_02", FEATURE, "Default '?sort=jurisdiction:asc' URL yields an alphabetically-first row",
        description="Loading /wta/MLIData?sort=jurisdiction%3Aasc must show 'Albania' as the first "
                     "jurisdiction in the table (alphabetically first among signatories).",
        precondition="User is logged in.",
        test_data="sort=jurisdiction:asc",
        steps="1. Log in and open MLI Data with the asc sort param\n"
              "2. Verify the first row's jurisdiction is 'Albania'",
    )
    mli = _login_and_open(case, page)
    case.step(2, "Verify the first row")
    first_row = mli.first_row_text()
    ok = first_row.strip().startswith("Albania")
    case.check("First row under ascending sort is 'Albania'", ok, expected="Albania...",
               actual=first_row[:60], locator=mli.table_rows.first)

    actual = ("The first row under the default ascending sort correctly starts with 'Albania'." if ok else
              f"The first row did not start with 'Albania' as expected (got: {first_row[:60]!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mlidata_03_clicking_jurisdiction_header_reverses_sort_order(page, result):
    case = Case(
        page, "MLIData_03", FEATURE, "Clicking the 'Jurisdiction' column header toggles sort direction",
        description="Clicking the sortable 'Jurisdiction' column header on a table loaded ascending must "
                     "flip the URL's sort param to 'jurisdiction:desc' and change the first visible row "
                     "from 'Albania' to the alphabetically-last jurisdiction.",
        precondition="User is logged in and on MLI Data (ascending sort).",
        test_data="-",
        steps="1. Log in and open MLI Data (asc)\n2. Click the 'Jurisdiction' column header\n"
              "3. Verify the URL sort param flips to desc and the first row changes",
    )
    mli = _login_and_open(case, page)
    before = mli.first_row_text()[:60]

    case.step(2, "Click the 'Jurisdiction' column header")
    case.click(mli.jurisdiction_header, "'Jurisdiction' column header")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)

    case.step(3, "Verify the sort flipped")
    url_ok = "jurisdiction%3Adesc" in page.url or "jurisdiction:desc" in page.url
    after = mli.first_row_text()[:60]
    row_changed = after != before
    ok = url_ok and row_changed
    case.check("Clicking the Jurisdiction header flips the URL sort param and reorders the table", ok,
               expected="sort=jurisdiction:desc, first row changed",
               actual=f"url={page.url}, before={before!r}, after={after!r}")

    actual = (f"Clicking the 'Jurisdiction' header flipped the sort to descending; the first row changed "
              f"from {before!r} to {after!r}." if ok else
              f"Clicking the 'Jurisdiction' header did not flip the sort as expected (url_ok={url_ok}, "
              f"row_changed={row_changed}, before={before!r}, after={after!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mlidata_04_no_jurisdiction_selection_panel_present(page, result):
    case = Case(
        page, "MLIData_04", FEATURE, "MLI Data has no jurisdiction selection panel, unlike the other Treaties pages",
        description="Confirmed live that MLI Data has no left 'Jurisdictions' panel and no 'Search "
                     "countries' box - the 'Select Jurisdiction' heading and country search input used on "
                     "the other 4 Treaties pages must both be ABSENT here.",
        precondition="User is logged in and on MLI Data.",
        test_data="-",
        steps="1. Log in and open MLI Data\n2. Verify no 'Select Jurisdiction' heading and no country search box are present",
    )
    mli = _login_and_open(case, page)
    case.step(2, "Verify the jurisdiction panel is absent")
    heading_absent = page.get_by_role("heading", name="Select Jurisdiction").count() == 0
    search_absent = page.get_by_placeholder("Search countries", exact=False).count() == 0
    ok = heading_absent and search_absent
    case.check("No jurisdiction-selection UI is present on MLI Data", ok,
               expected="heading_absent=True, search_absent=True",
               actual=f"heading_absent={heading_absent}, search_absent={search_absent}")

    actual = ("MLI Data correctly has no jurisdiction-selection heading or country search box, confirming "
              "it is not jurisdiction-gated like the other 4 Treaties pages." if ok else
              f"MLI Data unexpectedly showed jurisdiction-selection UI (heading_absent={heading_absent}, "
              f"search_absent={search_absent}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_mlidata_05_row_contains_known_jurisdiction_dates(page, result):
    case = Case(
        page, "MLIData_05", FEATURE, "The Albania row shows its known MLI signature and entry-into-force dates",
        description="The 'Albania' row must show '28 May 2019' (Signature) and '01 January 2021' (Entry "
                     "into Force).",
        precondition="User is logged in and on MLI Data.",
        test_data="Jurisdiction: Albania",
        steps="1. Log in and open MLI Data\n2. Verify the Albania row contains its known dates",
    )
    mli = _login_and_open(case, page)
    case.step(2, "Verify the Albania row's dates")
    row = mli.table_rows.filter(has_text="Albania")
    row_exists = row.count() >= 1
    row_text = row.first.inner_text() if row_exists else ""
    ok = row_exists and "28 May 2019" in row_text and "01 January 2021" in row_text
    case.check("Albania row shows its known Signature and Entry into Force dates", ok,
               expected="28 May 2019 and 01 January 2021", actual=row_text,
               locator=row.first if row_exists else None)

    actual = ("The Albania row correctly shows its known Signature (28 May 2019) and Entry into Force (01 "
              "January 2021) dates." if ok else
              f"The expected dates were not found in the Albania row (row_exists={row_exists}, "
              f"text={row_text!r}).")
    result(case, actual, ok)
    assert ok, actual
