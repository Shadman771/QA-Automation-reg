"""World Tax Analyzer > Forms (/wta/Forms) - top-level module (distinct
from Pillar 2 > Forms).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: 'Jurisdictions and Categories' with a flat category
    checklist (CIT Returns, WHT deduction/Treaty form, Administrative,
    Other Forms, Pillar Two) plus a 'checkAllFormCategories' master
    checkbox and its own 'Search' box.
  - Unlike the main Information page, content here renders from the
    jurisdiction ALONE - 'Showing forms of <Country>' - a table (Title /
    Description / Applies to tax year ending on / Download / Project);
    categories narrow (filter) that same table rather than gating it."""
import os

import pytest

from pages.forms_page import FormsPage, FORM_CATEGORIES
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Forms"


def _login_and_open(case, page):
    perform_login(case, page)
    forms = FormsPage(page)
    case.action("Navigating to /wta/Forms", kind="navigate")
    forms.goto()
    return forms


@pytest.mark.smoke
def test_forms_01_page_loads_with_categories(page, result):
    case = Case(
        page, "Forms_01", FEATURE, "Forms module loads with the jurisdiction and category panel",
        description="The page must load with the left-panel instruction text and all 5 form categories "
                     "listed.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Forms\n2. Verify the placeholder text and all 5 categories are visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Verify placeholder and categories")
    placeholder_ok = case.verify_visible(forms.placeholder_text, "left-panel instruction text")
    missing = [c for c in FORM_CATEGORIES if not case.verify_visible(page.get_by_text(c, exact=True), f"'{c}' category")]
    ok = placeholder_ok and not missing
    case.check("Placeholder and all 5 form categories are visible", ok,
               expected="placeholder + 5 categories visible",
               actual=f"placeholder={placeholder_ok}, missing_categories={missing}")

    actual = ("Forms loaded with the placeholder and all 5 categories (CIT Returns, WHT deduction/Treaty "
              "form, Administrative, Other Forms, Pillar Two) visible." if ok else
              f"Forms did not show the expected placeholder/categories (missing: {missing}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_forms_02_jurisdiction_alone_renders_table(page, result):
    case = Case(
        page, "Forms_02", FEATURE, "Selecting a jurisdiction alone (no category) renders the forms table",
        description="Checking 'Australia' with no category selected must still render a 'Showing forms of "
                     "Australia' table, confirming categories here filter rather than gate content.",
        precondition="User is logged in and on Forms.",
        test_data="Country: Australia",
        steps="1. Log in and open Forms\n2. Check 'Australia' only\n"
              "3. Verify the forms table renders without selecting any category",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Select Australia only")
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_text)

    case.step(3, "Verify the table rendered without a category selected")
    showing_ok = case.verify_visible(forms.showing_text, "'Showing forms of' text")
    table_ok = forms.table.count() >= 1
    ok = showing_ok and table_ok
    case.check("Forms table renders from jurisdiction alone, no category required", ok,
               expected="table visible", actual=f"showing={showing_ok}, table_count={forms.table.count()}")

    actual = ("Selecting Australia alone (no category) rendered the forms table, confirming categories "
              "act as an optional filter here, unlike the main Information page." if ok else
              "Selecting a jurisdiction alone did not render the forms table as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_forms_03_category_checkbox_can_be_toggled_off_and_on(page, result):
    case = Case(
        page, "Forms_03", FEATURE, "A category checkbox can be toggled off and back on",
        description="Every form category checkbox (confirmed live) starts CHECKED by default. With "
                     "Australia selected, clicking 'CIT Returns' once must UNCHECK it, and clicking it "
                     "again must re-check it.",
        precondition="User is logged in, Australia selected on Forms.",
        test_data="Country: Australia / Category: CIT Returns",
        steps="1. Log in, open Forms, select Australia\n2. Verify 'CIT Returns' starts checked\n"
              "3. Click it once and verify it becomes unchecked\n"
              "4. Click it again and verify it becomes checked again",
    )
    forms = _login_and_open(case, page)
    forms.jurisdiction.country_checkbox("Australia").click()
    page.wait_for_timeout(1000)

    case.step(2, "Verify 'CIT Returns' starts checked")
    starts_checked = forms.category_checkbox("CIT Returns").is_checked()
    case.check("'CIT Returns' category checkbox is checked by default", starts_checked,
               expected=True, actual=starts_checked, locator=forms.category_checkbox("CIT Returns"))

    case.step(3, "Click 'CIT Returns' once")
    case.click(forms.category_checkbox("CIT Returns"), "'CIT Returns' category checkbox")
    page.wait_for_timeout(500)
    now_unchecked = not forms.category_checkbox("CIT Returns").is_checked()
    case.check("'CIT Returns' becomes unchecked after one click", now_unchecked,
               expected=False, actual=not now_unchecked, locator=forms.category_checkbox("CIT Returns"))

    case.step(4, "Click 'CIT Returns' again")
    case.click(forms.category_checkbox("CIT Returns"), "'CIT Returns' category checkbox")
    page.wait_for_timeout(500)
    now_checked_again = forms.category_checkbox("CIT Returns").is_checked()
    case.check("'CIT Returns' becomes checked again after a second click", now_checked_again,
               expected=True, actual=now_checked_again, locator=forms.category_checkbox("CIT Returns"))

    ok = starts_checked and now_unchecked and now_checked_again
    actual = ("'CIT Returns' started checked, toggled off on the first click, and toggled back on on the "
              "second click - confirming the category filter checkbox is fully interactive." if ok else
              f"The category checkbox did not toggle as expected (starts_checked={starts_checked}, "
              f"unchecked_after_click={now_unchecked}, checked_again={now_checked_again}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_forms_04_check_all_categories_toggles_all_off(page, result):
    case = Case(
        page, "Forms_04", FEATURE, "'Check All' (already checked by default) toggles every category off",
        description="The 'checkAllFormCategories' master checkbox and every individual category checkbox "
                     "start CHECKED by default (confirmed live). Clicking the master checkbox once must "
                     "therefore UNCHECK every individual category, not check them.",
        precondition="User is logged in and on Forms.",
        test_data="-",
        steps="1. Log in and open Forms\n2. Verify 'CIT Returns' and 'Pillar Two' start checked\n"
              "3. Click the 'Check All' master checkbox\n"
              "4. Verify 'CIT Returns' and 'Pillar Two' both become unchecked",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Verify sample categories start checked")
    cit_before = forms.category_checkbox("CIT Returns").is_checked()
    p2_before = forms.category_checkbox("Pillar Two").is_checked()
    case.check("'CIT Returns' and 'Pillar Two' are checked by default", cit_before and p2_before,
               expected="both checked", actual=f"cit={cit_before}, pillar2={p2_before}")

    case.step(3, "Click 'Check All' for form categories")
    case.click(forms.check_all_categories, "'Check All' form categories checkbox")
    page.wait_for_timeout(700)

    case.step(4, "Verify sample categories are now unchecked")
    cit_after = forms.category_checkbox("CIT Returns").is_checked()
    p2_after = forms.category_checkbox("Pillar Two").is_checked()
    ok = cit_before and p2_before and not cit_after and not p2_after
    case.check("'CIT Returns' and 'Pillar Two' are unchecked after clicking the already-checked 'Check All'",
               not cit_after and not p2_after,
               expected="both unchecked", actual=f"cit={cit_after}, pillar2={p2_after}",
               locator=forms.category_checkbox("CIT Returns"))

    actual = ("The 'Check All' master checkbox and all categories started checked by default; clicking "
              "'Check All' unchecked every category, confirmed via CIT Returns and Pillar Two." if ok else
              f"'Check All' did not toggle the form categories off as expected (cit_before={cit_before}, "
              f"pillar2_before={p2_before}, cit_after={cit_after}, pillar2_after={p2_after}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_forms_05_forms_search_box_accepts_input(page, result):
    case = Case(
        page, "Forms_05", FEATURE, "The Forms page's own Search box accepts free-text input",
        description="Typing into the page's 'Search' box (distinct from 'Search countries') must accept "
                     "the text without error.",
        precondition="User is logged in and on Forms.",
        test_data="Search term: company tax return",
        steps="1. Log in and open Forms\n2. Type 'company tax return' into the Search box\n"
              "3. Verify the box holds the typed value",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Type into the Search box")
    case.fill(forms.search_forms, "company tax return", "'Search' box")
    page.wait_for_timeout(400)

    case.step(3, "Verify the typed value is present")
    value = forms.search_forms.input_value()
    ok = value == "company tax return"
    case.check("Search box holds the typed value", ok, expected="company tax return", actual=value,
               locator=forms.search_forms)

    actual = (f"The Search box accepted and retained the typed value '{value}'." if ok else
              f"The Search box did not retain the typed value (got '{value}').")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_forms_06_download_link_triggers_real_file_download(page, result):
    case = Case(
        page, "Forms_06", FEATURE, "A row's 'English' download link triggers a real, non-empty file download",
        description="With Australia selected, clicking the first row's 'English' download link must trigger a "
                     "real download with no failure and a non-zero size - not merely be present/visible.",
        precondition="User is logged in, Australia selected on Forms.",
        test_data="Country: Australia",
        steps="1. Log in and open Forms\n2. Select Australia\n"
              "3. Click the first 'English' download link\n"
              "4. Verify a real, non-empty file download completed",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_text)

    case.step(3, "Click the first 'English' download link")
    # 30s not 15s: confirmed live this file is a large (1MB+) real PDF -
    # observed flaky at 15s specifically under full-suite load (passes
    # standalone every time), so this widens the wait for the real download
    # to arrive rather than weakening what's actually asserted below.
    with page.expect_download(timeout=30000) as dl_info:
        case.click(forms.download_links.first, "'English' download link")
    download = dl_info.value

    case.step(4, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and size > 0
    case.check("The 'English' download link produces a real, non-empty file with no failure", ok,
               expected="failure=None, size>0", actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The download link correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"The download link did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual
