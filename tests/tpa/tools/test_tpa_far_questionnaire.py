"""TPA > Tools > FAR Questionnaire (/tpa/FARQuestionnaireCreator). See
pages/tpa/tpa_tools_far_questionnaire_page.py for the full confirmed-live
layout (AI-driven 'Create & Generate' flow, per-row kebab menu).

The one test that completes creation uses a unique, clearly-tagged title
(`ToolsQA_FAR_<timestamp>`) and deletes it again before the test ends."""
import time

import pytest

from pages.tpa.tpa_tools_far_questionnaire_page import TpaFarQuestionnairePage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "TPA Tools FAR Questionnaire"


def _unique_title(tag: str) -> str:
    return f"ToolsQA_FAR_{tag}_{int(time.time() * 1000)}"


def _login_and_open(case, page):
    perform_login(case, page)
    far = TpaFarQuestionnairePage(page)
    case.action("Navigating to /tpa/FARQuestionnaireCreator", kind="navigate")
    far.goto()
    return far


@pytest.mark.smoke
def test_tpafar_01_page_loads_with_table_and_add_button(page, result):
    case = Case(
        page, "TpaFar_01", FEATURE, "FAR Questionnaire loads with the table and 'Add Questionnaire' button",
        description="The page must load at /tpa/FARQuestionnaireCreator with the 'Add Questionnaire' button "
                     "visible and at least one existing questionnaire row.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open FAR Questionnaire\n2. Verify URL and 'Add Questionnaire' button\n"
              "3. Verify at least one existing row is visible",
    )
    far = _login_and_open(case, page)
    case.step(2, "Verify URL and 'Add Questionnaire' button")
    url_ok = "/tpa/FARQuestionnaireCreator" in page.url
    add_btn_ok = case.verify_visible(far.add_questionnaire_button, "'Add Questionnaire' button")

    case.step(3, "Verify at least one existing row is visible")
    rows_ok = far.table_rows.count() > 0
    ok = url_ok and add_btn_ok and rows_ok
    case.check("FAR Questionnaire loads with 'Add Questionnaire' and existing rows", ok,
               expected="url_ok=True, add_btn_ok=True, rows_ok=True",
               actual=f"url_ok={url_ok}, add_btn_ok={add_btn_ok}, rows_ok={rows_ok}, "
                      f"row_count={far.table_rows.count()}")

    actual = (f"FAR Questionnaire loaded correctly at {page.url} with {far.table_rows.count()} existing rows."
              if ok else f"FAR Questionnaire did not load as expected (url_ok={url_ok}, "
              f"add_btn_ok={add_btn_ok}, rows_ok={rows_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpafar_02_table_has_expected_columns(page, result):
    case = Case(
        page, "TpaFar_02", FEATURE, "The table shows the expected columns",
        description="Confirmed live: the columns are Title, SIC Code, Status, Created, Updated.",
        precondition="User is logged in and on FAR Questionnaire.",
        test_data="-",
        steps="1. Log in and open FAR Questionnaire\n2. Verify all expected column headers are present",
    )
    far = _login_and_open(case, page)
    case.step(2, "Verify all expected column headers are present")
    expected = ["Title", "SIC Code", "Status", "Created", "Updated"]
    headers = far.table.first.locator("th").all_inner_texts()
    missing = [c for c in expected if not any(c in h for h in headers)]
    ok = not missing
    case.check("All expected columns are present in the table header", ok,
               expected=expected, actual=f"headers={headers}, missing={missing}")

    actual = f"FAR Questionnaire table correctly shows all expected columns: {expected}." if ok else \
             f"FAR Questionnaire table was missing expected columns: {missing} (headers={headers})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpafar_03_add_questionnaire_modal_shows_required_fields(page, result):
    case = Case(
        page, "TpaFar_03", FEATURE, "'Add Questionnaire' opens a modal with Title, SIC Code and Attachments",
        description="Clicking 'Add Questionnaire' must open a modal titled 'Add FAR Questionnaire' with a "
                     "'Title*' text field, a 'SIC Code*' dropdown, an optional Attachments upload area, and "
                     "Cancel/'Create & Generate' buttons. 'Create & Generate' must be disabled while both "
                     "required fields are empty.",
        precondition="User is logged in and on FAR Questionnaire.",
        test_data="-",
        steps="1. Log in and open FAR Questionnaire\n2. Click 'Add Questionnaire'\n"
              "3. Verify the modal's fields and that 'Create & Generate' is disabled while empty",
    )
    far = _login_and_open(case, page)
    case.step(2, "Click 'Add Questionnaire'")
    case.click(far.add_questionnaire_button, "'Add Questionnaire' button")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the modal's fields and that 'Create & Generate' is disabled while empty")
    modal_ok = case.verify_visible(far.modal_heading, "'Add FAR Questionnaire' modal heading")
    title_ok = far.title_input.count() > 0
    sic_ok = far.sic_code_select.count() > 0
    disabled_ok = far.create_and_generate_button.is_disabled()
    ok = modal_ok and title_ok and sic_ok and disabled_ok
    case.check("The 'Add FAR Questionnaire' modal shows its expected fields, disabled by default", ok,
               expected="modal_ok=True, title_ok=True, sic_ok=True, disabled_ok=True",
               actual=f"modal_ok={modal_ok}, title_ok={title_ok}, sic_ok={sic_ok}, disabled_ok={disabled_ok}")

    case.click(far.modal_cancel_button, "'Cancel' button (cleanup)")

    actual = "The 'Add FAR Questionnaire' modal correctly showed its expected fields, disabled by default." \
        if ok else f"The modal did not match expectations (modal_ok={modal_ok}, title_ok={title_ok}, " \
                   f"sic_ok={sic_ok}, disabled_ok={disabled_ok})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpafar_04_cancel_closes_modal_without_creating(page, result):
    title = _unique_title("Cancel")
    case = Case(
        page, "TpaFar_04", FEATURE, "'Cancel' closes the 'Add FAR Questionnaire' modal without creating anything",
        description=f"Filling the Title field with a unique title ({title}) and clicking 'Cancel' (instead "
                     f"of 'Create & Generate') must close the modal without adding any new row.",
        precondition="User is logged in and on FAR Questionnaire.",
        test_data=f"Title: {title}",
        steps=f"1. Log in and open FAR Questionnaire\n2. Fill Title with '{title}'\n3. Click 'Cancel'\n"
              f"4. Verify '{title}' does NOT appear in the table",
    )
    far = _login_and_open(case, page)
    case.step(2, f"Fill Title with '{title}'")
    case.click(far.add_questionnaire_button, "'Add Questionnaire' button")
    page.wait_for_timeout(1000)
    case.fill(far.title_input, title, "'Title' field")

    case.step(3, "Click 'Cancel'")
    case.click(far.modal_cancel_button, "'Cancel' button")
    page.wait_for_timeout(1000)

    case.step(4, f"Verify '{title}' does NOT appear in the table")
    not_created = not far.row_exists(title)
    ok = not_created
    case.check(f"'{title}' was correctly NOT created after Cancel", ok, expected=True, actual=not_created)

    actual = f"'Cancel' correctly created no new questionnaire for '{title}'." if ok else \
             f"'{title}' unexpectedly appeared in the table despite clicking Cancel."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpafar_05_filling_title_and_sic_enables_create_and_generate(page, result):
    title = _unique_title("EnableProbe")
    case = Case(
        page, "TpaFar_05", FEATURE, "Filling Title and SIC Code enables 'Create & Generate'",
        description=f"Filling the Title field ({title}) and picking a real SIC Code option must change "
                     f"'Create & Generate' from disabled to enabled.",
        precondition="User is logged in and on FAR Questionnaire.",
        test_data=f"Title: {title}",
        steps=f"1. Log in and open FAR Questionnaire\n2. Fill Title with '{title}'\n"
              f"3. Pick the first real SIC Code option\n4. Verify 'Create & Generate' becomes enabled\n"
              f"5. Cancel (no creation)",
    )
    far = _login_and_open(case, page)
    case.step(2, f"Fill Title with '{title}'")
    case.click(far.add_questionnaire_button, "'Add Questionnaire' button")
    page.wait_for_timeout(1000)
    case.fill(far.title_input, title, "'Title' field")

    case.step(3, "Pick the first real SIC Code option")
    case.click(far.sic_code_select, "'Select SIC Code' dropdown")
    page.wait_for_timeout(800)
    options = page.locator("[role='option']:visible, li.rs-picker-select-menu-item:visible")
    if options.count() > 0:
        case.click(options.first, "first SIC Code option")
    page.wait_for_timeout(500)

    case.step(4, "Verify 'Create & Generate' becomes enabled")
    enabled_ok = far.create_and_generate_button.is_enabled()
    case.check("'Create & Generate' is enabled once Title and SIC Code are filled", enabled_ok,
               expected=True, actual=enabled_ok, locator=far.create_and_generate_button)

    case.step(5, "Cancel (no creation)")
    case.click(far.modal_cancel_button, "'Cancel' button")

    ok = enabled_ok
    actual = "'Create & Generate' correctly became enabled once Title and SIC Code were filled." if ok else \
             "'Create & Generate' did not become enabled as expected after filling Title and SIC Code."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpafar_06_create_a_questionnaire_end_to_end(page, result):
    title = _unique_title("Create")
    case = Case(
        page, "TpaFar_06", FEATURE, "Creating a FAR questionnaire adds it to the list",
        description=f"Filling Title ({title}) and a real SIC Code, then clicking 'Create & Generate', must "
                     f"add a new row for '{title}' to the table - this is an AI-driven flow, so a generous "
                     f"wait is used before asserting the row exists.",
        precondition="User is logged in and on FAR Questionnaire.",
        test_data=f"Title: {title}",
        steps=f"1. Log in and open FAR Questionnaire\n2. Fill Title with '{title}', pick a SIC Code\n"
              f"3. Click 'Create & Generate'\n4. Verify '{title}' appears in the table\n"
              f"5. Clean up: delete it via its kebab menu",
    )
    far = _login_and_open(case, page)
    case.step(2, f"Fill Title with '{title}', pick a SIC Code")
    case.click(far.add_questionnaire_button, "'Add Questionnaire' button")
    page.wait_for_timeout(1000)
    case.fill(far.title_input, title, "'Title' field")
    case.click(far.sic_code_select, "'Select SIC Code' dropdown")
    page.wait_for_timeout(800)
    options = page.locator("[role='option']:visible, li.rs-picker-select-menu-item:visible")
    if options.count() > 0:
        case.click(options.first, "first SIC Code option")
    page.wait_for_timeout(500)

    case.step(3, "Click 'Create & Generate'")
    case.click(far.create_and_generate_button, "'Create & Generate' button")
    page.wait_for_timeout(2000)
    far.goto()
    wait_for_content(far.row_by_title(title), timeout=20000)

    case.step(4, f"Verify '{title}' appears in the table")
    created_ok = far.row_exists(title)
    case.check(f"New questionnaire '{title}' appears in the table", created_ok, expected=True, actual=created_ok)

    case.step(5, "Clean up: delete it via its kebab menu")
    if created_ok:
        menu = far.open_row_menu(title)
        page.wait_for_timeout(500)
        delete_item = menu.filter(has_text="Delete Questionnaire")
        if delete_item.count() > 0:
            case.click(delete_item.first, "'Delete Questionnaire' menu item")
            page.wait_for_timeout(600)
            confirm = page.get_by_role("button", name="Delete")
            if confirm.count() > 0:
                case.click(confirm.first, "'Delete' confirm button")
            page.wait_for_timeout(1000)

    ok = created_ok
    actual = f"Creating a FAR questionnaire named '{title}' correctly added it to the table." if ok else \
             f"The new questionnaire '{title}' did not appear in the table after 'Create & Generate'."
    result(case, actual, ok)
    assert ok, actual
