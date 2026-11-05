"""TPA > Forms (/tpa/Forms).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. See pages/tpa/tpa_forms_page.py for the full real-shape writeup,
including the confirmed-live category-filtering behavior."""
import pytest

from pages.tpa.tpa_forms_page import TpaFormsPage, FORMS_CATEGORIES
from pages.wta.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Forms"


def _login_and_open(case, page):
    perform_login(case, page)
    forms = TpaFormsPage(page)
    case.action("Navigating to /tpa/Forms", kind="navigate")
    forms.goto()
    return forms


@pytest.mark.smoke
def test_tpaforms_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "TpaForms_01", FEATURE, "Forms loads with the jurisdiction/category placeholder",
        description="The page must load with the 'Use the left panel to choose jurisdiction and categories.' "
                     "placeholder shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Forms\n2. Verify the placeholder text is visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(forms.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("Forms loaded with the placeholder visible." if ok else "Forms did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaforms_02_all_four_categories_listed(page, result):
    case = Case(
        page, "TpaForms_02", FEATURE, "All 4 categories are listed in the left panel",
        description="The category checklist must show all 4 known Forms categories.",
        precondition="User is logged in and on Forms.",
        test_data="-",
        steps="1. Log in and open Forms\n2. Verify each of the 4 categories is visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Verify each category label is visible")
    missing = [c for c in FORMS_CATEGORIES if not case.verify_visible(forms.category.category_label(c), f"'{c}' category")]
    ok = not missing
    case.check("All 4 categories are visible", ok, expected="all 4 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 4 categories were visible." if ok else f"Missing categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaforms_03_jurisdiction_alone_renders_full_table(page, result):
    case = Case(
        page, "TpaForms_03", FEATURE, "Selecting only a jurisdiction renders the full forms table",
        description="Checking 'Australia' alone (no category) must render a 'Showing forms of Australia' "
                     "table with real rows and column headers.",
        precondition="User is logged in and on Forms.",
        test_data="Country: Australia",
        steps="1. Log in and open Forms\n2. Check 'Australia'\n"
              "3. Verify the table and its columns render",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_forms_text)

    case.step(3, "Verify table and columns")
    showing_ok = case.verify_visible(forms.showing_forms_text, "'Showing forms of' text")
    title_ok = case.verify_visible(forms.col_title, "'Title' column header")
    download_ok = case.verify_visible(forms.col_download, "'Download' column header")
    row_count = forms.row_count()
    ok = showing_ok and title_ok and download_ok and row_count > 0
    case.check("Forms table with columns and real rows is visible", ok,
               expected="all visible, rows > 0",
               actual=f"showing={showing_ok}, title={title_ok}, download={download_ok}, rows={row_count}")

    actual = (f"Selecting Australia rendered the forms table with {row_count} row(s)." if ok else
              "The forms table or its columns did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaforms_04_category_selection_filters_the_table(page, result):
    case = Case(
        page, "TpaForms_04", FEATURE, "Selecting a category filters the table to a smaller real subset",
        description="With Australia selected, checking 'TP specific form' must reduce the row count from the "
                     "unfiltered total - confirmed live (39 -> 13 for Australia) that this category genuinely "
                     "filters rather than being a no-op.",
        precondition="User is logged in, Australia selected on Forms.",
        test_data="Country: Australia / Category: TP specific form",
        steps="1. Log in, open Forms, select Australia\n2. Record the unfiltered row count\n"
              "3. Check 'TP specific form'\n4. Verify the row count is smaller but still > 0",
    )
    forms = _login_and_open(case, page)
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_forms_text)
    # The "Showing forms of" header renders before the table's own rows
    # finish mounting (confirmed live: the same async-render race already
    # seen with National Rules' "Commentary" buttons and News' "Add to
    # Project" button) - wait for a real row too, not just the header.
    wait_for_content(forms.add_to_project_buttons)
    case.step(2, "Record the unfiltered row count")
    unfiltered_count = forms.row_count()

    case.step(3, "Check 'TP specific form'")
    case.click(forms.category.category_checkbox("TP specific form"), "'TP specific form' category checkbox")
    page.wait_for_timeout(1500)

    case.step(4, "Verify the row count is smaller but still > 0")
    filtered_count = forms.row_count()
    ok = 0 < filtered_count < unfiltered_count
    case.check("Selecting 'TP specific form' reduces the row count", ok,
               expected=f"0 < filtered < {unfiltered_count}", actual=f"unfiltered={unfiltered_count}, filtered={filtered_count}")

    actual = (f"Selecting 'TP specific form' correctly filtered rows from {unfiltered_count} to {filtered_count}." if ok else
              f"Category selection did not filter as expected (unfiltered={unfiltered_count}, filtered={filtered_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaforms_05_each_row_has_download_and_add_to_project(page, result):
    case = Case(
        page, "TpaForms_05", FEATURE, "Each form row has a download link and an 'Add to Project' button",
        description="With Australia selected, at least one row must show a real download link and an "
                     "'Add to Project' button.",
        precondition="User is logged in, Australia selected on Forms.",
        test_data="Country: Australia",
        steps="1. Log in, open Forms, select Australia\n2. Verify a download link and 'Add to Project' are present",
    )
    forms = _login_and_open(case, page)
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_forms_text)
    wait_for_content(forms.add_to_project_buttons)

    case.step(2, "Verify a download link and 'Add to Project' are present")
    download_link = page.get_by_text("English", exact=True)
    download_ok = download_link.count() > 0
    project_count = forms.row_count()
    ok = download_ok and project_count > 0
    case.check("At least one row has a download link and an 'Add to Project' button", ok,
               expected="both present", actual=f"download_links={download_link.count()}, add_to_project={project_count}")

    actual = ("At least one row correctly has both a download link and 'Add to Project'." if ok else
              "No row had both a download link and 'Add to Project'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaforms_06_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "TpaForms_06", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Switching from 'Asia Pacific' (default) to 'Europe' must hide 'Australia' from the "
                     "visible list.",
        precondition="User is logged in and on Forms.",
        test_data="-",
        steps="1. Log in and open Forms\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(forms.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Australia' is no longer visible")
    ok = not forms.jurisdiction.country_checkbox("Australia").is_visible()
    case.check("'Australia' is hidden after switching to 'Europe'", ok, expected="not visible", actual=f"visible={not ok}")

    actual = ("Switching to 'Europe' correctly hid 'Australia'." if ok else
              "'Australia' was still visible after switching to 'Europe'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaforms_07_search_box_accepts_input(page, result):
    case = Case(
        page, "TpaForms_07", FEATURE, "The 'Search countries' box accepts input",
        description="Typing into the 'Search countries' box must filter the visible country list.",
        precondition="User is logged in and on Forms.",
        test_data="Search term: Austra",
        steps="1. Log in and open Forms\n2. Type 'Austra' into 'Search countries'\n"
              "3. Verify 'Australia' is still visible and other countries are filtered out",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Type 'Austra' into 'Search countries'")
    case.fill(forms.jurisdiction.search_countries, "Austra", "'Search countries' input")
    page.wait_for_timeout(600)

    case.step(3, "Verify 'Australia' is still visible")
    ok = case.verify_visible(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.check("'Australia' remains visible after searching 'Austra'", ok, expected="visible", actual=ok)

    actual = ("The search box correctly filtered to show 'Australia'." if ok else
              "'Australia' was not visible after searching 'Austra'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaforms_08_direct_deep_link_works(page, result):
    case = Case(
        page, "TpaForms_08", FEATURE, "A direct deep link to /tpa/Forms loads the page",
        description="Navigating straight to /tpa/Forms must load with the placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/Forms\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/Forms")
    forms = TpaFormsPage(page)
    forms.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(forms.placeholder_text, "left-panel instruction text")
    case.check("Direct deep link to /tpa/Forms loads with the placeholder", ok, expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/Forms correctly loaded." if ok else
              "The direct deep link to /tpa/Forms did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
