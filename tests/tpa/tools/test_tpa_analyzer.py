"""TPA > Tools > Analyzer (/tpa/DecisionFlows, on-page "Analyzer"). See
pages/tpa/tpa_tools_analyzer_page.py for the full confirmed-live layout
(Create Analysis modal with By Jurisdiction/By Entity modes, hover-only
Edit/Delete links).

Every test that creates an analysis uses a unique, clearly-tagged name
(`ToolsQA_DF_<timestamp>`) and deletes it again before the test ends, so
this suite does not add to this shared live account's existing analyses."""
import time

import pytest

from pages.tpa.tpa_tools_analyzer_page import TpaAnalyzerPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "TPA Tools Analyzer"


def _unique_name(tag: str) -> str:
    return f"ToolsQA_DF_{tag}_{int(time.time() * 1000)}"


def _login_and_open(case, page):
    perform_login(case, page)
    analyzer = TpaAnalyzerPage(page)
    case.action("Navigating to /tpa/DecisionFlows", kind="navigate")
    analyzer.goto()
    return analyzer


def _fill_minimal_form(case, analyzer, name: str):
    case.fill(analyzer.name_input, name, "'Analysis name' field")
    case.fill(analyzer.tested_party_input, "Bangladesh", "'Tested Party' field")
    case.fill(analyzer.related_party_input, "Singapore", "'Related Party' field")
    case.action("Selecting 'Tax Residence Tested Party' (first option)", kind="select")
    analyzer.pick_first_tax_residence_option()
    case.action("Selecting 'Tax Residence Related Party' (first option)", kind="select")
    analyzer.pick_first_tax_residence_option()


def _delete_analysis(case, page, analyzer: TpaAnalyzerPage, name: str):
    delete_link = analyzer.row_action(name, "Delete")
    case.click(delete_link, f"'Delete' action for '{name}'")
    page.wait_for_timeout(600)
    confirm_delete = page.get_by_role("button", name="Delete")
    if confirm_delete.count() > 0:
        case.click(confirm_delete.first, "'Delete' confirm button")
    page.wait_for_timeout(1000)


@pytest.mark.smoke
def test_tpaanalyzer_01_page_loads_with_new_analysis_button(page, result):
    case = Case(
        page, "TpaAnalyzer_01", FEATURE, "Analyzer loads with the 'New Analysis' button and help section",
        description="The page must load at /tpa/DecisionFlows with the 'New Analysis' button and "
                     "'Description of Analyses' help section visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Analyzer\n2. Verify URL\n"
              "3. Verify 'New Analysis' button and 'Description of Analyses' heading are visible",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, "Verify URL")
    url_ok = "/tpa/DecisionFlows" in page.url

    case.step(3, "Verify 'New Analysis' button and 'Description of Analyses' heading are visible")
    btn_ok = case.verify_visible(analyzer.new_analysis_button, "'New Analysis' button")
    desc_ok = case.verify_visible(analyzer.description_heading, "'Description of Analyses' heading")
    ok = url_ok and btn_ok and desc_ok
    case.check("Analyzer loads with its expected controls", ok,
               expected="url_ok=True, btn_ok=True, desc_ok=True",
               actual=f"url_ok={url_ok}, btn_ok={btn_ok}, desc_ok={desc_ok}")

    actual = f"Analyzer loaded correctly at {page.url}." if ok else \
             f"Analyzer did not load as expected (url_ok={url_ok}, btn_ok={btn_ok}, desc_ok={desc_ok})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaanalyzer_02_new_analysis_modal_shows_both_modes_and_required_fields(page, result):
    case = Case(
        page, "TpaAnalyzer_02", FEATURE, "'New Analysis' opens a modal with both modes and all required fields",
        description="Opening 'New Analysis' must show a 'Create Analysis' modal with 2 mode radios (By "
                     "Jurisdiction, defaulting checked; By Entity), the Name/Tested Party/Related Party text "
                     "inputs, 2 'Select' residence controls, an optional description field, and Cancel/Save.",
        precondition="User is logged in and on Analyzer.",
        test_data="-",
        steps="1. Log in and open Analyzer\n2. Click 'New Analysis'\n"
              "3. Verify the modal's mode radios, required fields, and buttons",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, "Click 'New Analysis'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the modal's mode radios, required fields, and buttons")
    modal_ok = case.verify_visible(analyzer.modal_heading, "'Create Analysis' modal heading")
    modes_ok = analyzer.mode_radios.count() == 2
    default_mode_ok = analyzer.mode_radios.nth(0).is_checked() and not analyzer.mode_radios.nth(1).is_checked()
    fields_ok = (analyzer.name_input.count() > 0 and analyzer.tested_party_input.count() > 0
                 and analyzer.related_party_input.count() > 0)
    buttons_ok = analyzer.modal_save_button.count() > 0 and analyzer.modal_cancel_button.count() > 0

    ok = modal_ok and modes_ok and default_mode_ok and fields_ok and buttons_ok
    case.check("The 'Create Analysis' modal shows its expected modes, fields and buttons", ok,
               expected="modal_ok=True, modes_ok=True, default_mode_ok=True, fields_ok=True, buttons_ok=True",
               actual=f"modal_ok={modal_ok}, modes_ok={modes_ok}, default_mode_ok={default_mode_ok}, "
                      f"fields_ok={fields_ok}, buttons_ok={buttons_ok}")

    actual = "The 'Create Analysis' modal correctly showed both modes and all required fields." if ok else \
             f"The modal did not match expectations (modal_ok={modal_ok}, modes_ok={modes_ok}, " \
             f"default_mode_ok={default_mode_ok}, fields_ok={fields_ok}, buttons_ok={buttons_ok})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaanalyzer_03_submitting_empty_form_shows_inline_required_errors(page, result):
    case = Case(
        page, "TpaAnalyzer_03", FEATURE, "Submitting the empty 'Create Analysis' form shows inline required-field errors",
        description="Confirmed live: 'Save' is NOT disabled for an empty form (no disabled-button gate like "
                     "WTA Tools Projects), but clicking it with every required field empty must keep the "
                     "modal open and show real inline errors ('Please enter analysis name.', 'Please enter "
                     "Tested Party.', 'Please enter Related Party.').",
        precondition="User is logged in and on Analyzer.",
        test_data="-",
        steps="1. Log in and open Analyzer\n2. Click 'New Analysis'\n3. Click 'Save' with every field empty\n"
              "4. Verify the modal stays open with inline required-field errors",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, "Click 'New Analysis'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)

    case.step(3, "Click 'Save' with every field empty")
    case.click(analyzer.modal_save_button, "'Save' button (empty form)")
    page.wait_for_timeout(1000)

    case.step(4, "Verify the modal stays open with inline required-field errors")
    modal_still_open = analyzer.modal.is_visible()
    modal_text = analyzer.modal.inner_text() if modal_still_open else ""
    expected_errors = ["Please enter analysis name.", "Please enter Tested Party.", "Please enter Related Party."]
    missing = [e for e in expected_errors if e not in modal_text]
    ok = modal_still_open and not missing
    case.check("Submitting the empty form showed inline required-field errors and stayed open", ok,
               expected=expected_errors, actual=f"modal_still_open={modal_still_open}, missing={missing}")

    case.click(analyzer.modal_cancel_button, "'Cancel' button (cleanup)")

    actual = "Submitting the empty form correctly showed inline required-field errors without closing." if ok \
        else f"Empty-form validation did not match expectations (modal_still_open={modal_still_open}, " \
             f"missing={missing})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaanalyzer_04_create_new_analysis(page, result):
    name = _unique_name("Create")
    case = Case(
        page, "TpaAnalyzer_04", FEATURE, "Creating a new analysis adds it to the analysis list",
        description=f"Filling the required fields with a unique name ({name}) and clicking Save must add a "
                     f"new analysis with that exact name to the list.",
        precondition="User is logged in and on Analyzer.",
        test_data=f"Analysis name: {name}",
        steps=f"1. Log in and open Analyzer\n2. Create an analysis named '{name}'\n"
              f"3. Verify '{name}' appears in the analysis list\n4. Clean up: delete '{name}'",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, f"Create an analysis named '{name}'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)
    _fill_minimal_form(case, analyzer, name)
    case.click(analyzer.modal_save_button, "'Save' button")
    page.wait_for_timeout(1500)

    case.step(3, f"Verify '{name}' appears in the analysis list")
    created_ok = case.verify_visible(analyzer.analysis_row_title(name), f"'{name}' analysis row")
    case.check(f"New analysis '{name}' appears in the list after Save", created_ok, expected=True, actual=created_ok)

    case.step(4, f"Clean up: delete '{name}'")
    if created_ok:
        _delete_analysis(case, page, analyzer, name)

    ok = created_ok
    actual = (f"Creating an analysis named '{name}' correctly added it to the list." if ok else
              f"The new analysis '{name}' did not appear in the list after Save.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaanalyzer_05_cancel_closes_modal_without_creating(page, result):
    name = _unique_name("Cancel")
    case = Case(
        page, "TpaAnalyzer_05", FEATURE, "'Cancel' closes the 'Create Analysis' modal without creating anything",
        description=f"Filling the form with a unique name ({name}) and clicking 'Cancel' (instead of Save) "
                     f"must close the modal without adding any new row.",
        precondition="User is logged in and on Analyzer.",
        test_data=f"Analysis name: {name}",
        steps=f"1. Log in and open Analyzer\n2. Fill the form with '{name}'\n3. Click 'Cancel'\n"
              f"4. Verify '{name}' does NOT appear in the analysis list",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, f"Fill the form with '{name}'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)
    _fill_minimal_form(case, analyzer, name)

    case.step(3, "Click 'Cancel'")
    case.click(analyzer.modal_cancel_button, "'Cancel' button")
    page.wait_for_timeout(1000)

    case.step(4, f"Verify '{name}' does NOT appear in the analysis list")
    not_created = not analyzer.analysis_exists(name)
    ok = not_created
    case.check(f"'{name}' was correctly NOT created after Cancel", ok, expected=True, actual=not_created)

    actual = f"'Cancel' correctly created no new analysis for '{name}'." if ok else \
             f"'{name}' unexpectedly appeared in the list despite clicking Cancel."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaanalyzer_06_edit_renames_an_analysis(page, result):
    original = _unique_name("Rename")
    renamed = original + "_RENAMED"
    case = Case(
        page, "TpaAnalyzer_06", FEATURE, "Editing an analysis renames it",
        description=f"Creating an analysis ({original}), then using its hover-revealed 'Edit' action to "
                     f"change the name to {renamed} and saving must replace the title in the list.",
        precondition="User is logged in and on Analyzer.",
        test_data=f"Original: {original} -> Renamed: {renamed}",
        steps=f"1. Log in and open Analyzer\n2. Create an analysis named '{original}'\n"
              f"3. Hover its row, click 'Edit', change the name to '{renamed}', Save\n"
              f"4. Verify '{renamed}' appears and '{original}' no longer does\n"
              f"5. Clean up: delete '{renamed}'",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, f"Create an analysis named '{original}'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)
    _fill_minimal_form(case, analyzer, original)
    case.click(analyzer.modal_save_button, "'Save' button")
    page.wait_for_timeout(1500)
    setup_ok = analyzer.analysis_exists(original)

    case.step(3, f"Hover its row, click 'Edit', change the name to '{renamed}', Save")
    if setup_ok:
        edit_link = analyzer.row_action(original, "Edit")
        case.click(edit_link, f"'Edit' action for '{original}'")
        wait_for_content(analyzer.edit_modal_heading, timeout=15000)
        case.fill(analyzer.name_input, renamed, "'Analysis name' field (rename)")
        case.click(analyzer.modal_save_button, "'Save' button (rename)")
        page.wait_for_timeout(1500)

    case.step(4, f"Verify '{renamed}' appears and '{original}' no longer does")
    renamed_ok = setup_ok and analyzer.analysis_exists(renamed)
    old_gone_ok = setup_ok and not analyzer.analysis_exists(original)
    ok = setup_ok and renamed_ok and old_gone_ok
    case.check("Renaming an analysis updates its title in the list", ok,
               expected=f"'{renamed}' present, '{original}' absent",
               actual=f"setup_ok={setup_ok}, renamed_present={renamed_ok}, original_absent={old_gone_ok}")

    case.step(5, f"Clean up: delete '{renamed}'")
    cleanup_name = renamed if renamed_ok else original
    if analyzer.analysis_exists(cleanup_name):
        _delete_analysis(case, page, analyzer, cleanup_name)

    actual = (f"Renaming '{original}' to '{renamed}' correctly updated the analysis list." if ok else
              f"Renaming did not behave as expected (setup_ok={setup_ok}, renamed_ok={renamed_ok}, "
              f"old_gone_ok={old_gone_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaanalyzer_07_delete_removes_an_analysis(page, result):
    name = _unique_name("Delete")
    case = Case(
        page, "TpaAnalyzer_07", FEATURE, "Deleting an analysis removes it from the list",
        description=f"Creating an analysis ({name}) and then using its hover-revealed 'Delete' action "
                     f"(with confirmation) must remove it from the list.",
        precondition="User is logged in and on Analyzer.",
        test_data=f"Analysis name: {name}",
        steps=f"1. Log in and open Analyzer\n2. Create an analysis named '{name}'\n"
              f"3. Delete it\n4. Verify '{name}' no longer appears in the list",
    )
    analyzer = _login_and_open(case, page)
    case.step(2, f"Create an analysis named '{name}'")
    case.click(analyzer.new_analysis_button, "'New Analysis' button")
    page.wait_for_timeout(1000)
    _fill_minimal_form(case, analyzer, name)
    case.click(analyzer.modal_save_button, "'Save' button")
    page.wait_for_timeout(1500)
    setup_ok = analyzer.analysis_exists(name)

    case.step(3, f"Delete '{name}'")
    if setup_ok:
        _delete_analysis(case, page, analyzer, name)

    case.step(4, f"Verify '{name}' no longer appears in the list")
    removed_ok = setup_ok and not analyzer.analysis_exists(name)
    ok = setup_ok and removed_ok
    case.check(f"'{name}' was removed after Delete", ok, expected=True, actual=removed_ok)

    actual = f"Deleting '{name}' correctly removed it from the analysis list." if ok else \
             f"'{name}' was not correctly removed (setup_ok={setup_ok}, removed_ok={removed_ok})."
    result(case, actual, ok)
    assert ok, actual
