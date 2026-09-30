"""Tools > Questionnaire Creator (/wta/QuestionnaireCreator). See
pages/tools_questionnaire_creator_page.py for the full confirmed-live
layout notes.

Fixture question used throughout: "Is [entity] carrying on a business?"
(confirmed live to be a single, unique, always-present leaf node under the
"Incorporation" topic)."""
import time

import pytest

from pages.tools_menu import ToolsMenu
from pages.tools_projects_page import ProjectsPage
from pages.tools_questionnaire_creator_page import QuestionnaireCreatorPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Tools QuestionnaireCreator"

FIXTURE_QUESTION = "Is [entity] carrying on a business?"


def _unique_title(tag: str) -> str:
    return f"ToolsQA_{tag}_{int(time.time() * 1000)}"


def _login_and_open(case, page):
    perform_login(case, page)
    menu = ToolsMenu(page)
    case.action("Opening Tools > Questionnaire Creator via the nav dropdown", kind="navigate")
    menu.open_item("Questionnaire Creator")
    return QuestionnaireCreatorPage(page)


def _start_over_and_confirm(case, page, qc: QuestionnaireCreatorPage):
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(600)
    case.click(qc.start_over_yes, "'Yes' (confirm Start Over)")
    page.wait_for_timeout(1000)


@pytest.mark.smoke
def test_questionnairecreator_01_page_loads(page, result):
    case = Case(
        page, "QuestionnaireCreator_01", FEATURE, "Questionnaire Creator loads with the question tree and editor",
        description="The page must load at /wta/QuestionnaireCreator with the 'Questions' heading, the "
                     "'Start Over' control and the rich-text editor all visible. 'Add to Project' is "
                     "confirmed live to only render once the editor has content (see "
                     "pages/tools_questionnaire_creator_page.py), so this case also inserts a question "
                     "first and then verifies 'Add to Project' appears.",
        precondition="User is logged in.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps="1. Log in and open Tools > Questionnaire Creator\n"
              "2. Verify URL, heading, 'Start Over' button and the editor\n"
              f"3. Click '{FIXTURE_QUESTION}' and verify 'Add to Project' then appears",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Verify URL, heading, 'Start Over' button and editor")
    url_ok = "/wta/QuestionnaireCreator" in page.url
    heading_ok = case.verify_visible(qc.heading, "'Questions' heading")
    start_over_ok = case.verify_visible(qc.start_over_button, "'Start Over' button")
    editor_ok = case.verify_visible(qc.editor, "rich-text editor")

    case.step(3, f"Click '{FIXTURE_QUESTION}' and verify 'Add to Project' then appears")
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)
    add_ok = case.verify_visible(qc.add_to_project_button, "'Add to Project' button")

    ok = url_ok and heading_ok and start_over_ok and editor_ok and add_ok
    case.check("Questionnaire Creator loads with all key controls present", ok,
               expected="url_ok=True, heading_ok=True, start_over_ok=True, editor_ok=True, add_ok=True",
               actual=f"url_ok={url_ok}, heading_ok={heading_ok}, start_over_ok={start_over_ok}, "
                      f"editor_ok={editor_ok}, add_ok={add_ok}")

    actual = (f"Questionnaire Creator loaded correctly at {page.url}, and 'Add to Project' appeared once "
              f"content was inserted." if ok else
              f"Questionnaire Creator did not load as expected (url_ok={url_ok}, heading_ok={heading_ok}, "
              f"start_over_ok={start_over_ok}, editor_ok={editor_ok}, add_ok={add_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_questionnairecreator_02_clicking_question_inserts_into_editor(page, result):
    case = Case(
        page, "QuestionnaireCreator_02", FEATURE, "Clicking a question in the tree inserts it into the editor",
        description=f"Clicking '{FIXTURE_QUESTION}' in the question tree must grow the editor's content "
                     f"(a new 'questionnaireDiv' block is inserted). The editor's content persists across "
                     f"runs (real, documented account-level draft state - see "
                     f"pages/tools_questionnaire_creator_page.py), so this test resets to a known-empty "
                     f"baseline via Start Over first; without that reset, re-clicking a question already "
                     f"present in the editor is correctly a no-op, not a bug.",
        precondition="User is logged in and on Questionnaire Creator.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Questionnaire Creator\n2. Reset via Start Over so the editor is empty\n"
              f"3. Note the editor's current content length\n"
              f"4. Click '{FIXTURE_QUESTION}'\n5. Verify the editor's content grew",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Reset via Start Over so the editor starts empty")
    # The app itself disables 'Start Over' when there's nothing to reset -
    # that's a more reliable signal than independently inferring emptiness
    # from the editor's HTML, which can race the editor's own load/render.
    if qc.start_over_button.is_enabled():
        _start_over_and_confirm(case, page, qc)

    case.step(3, "Note the editor's current content length")
    before_len = len(qc.editor_html())

    case.step(4, f"Click '{FIXTURE_QUESTION}'")
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)

    case.step(5, "Verify the editor's content grew")
    after_len = len(qc.editor_html())
    ok = after_len > before_len
    case.check("Editor content grew after clicking the question", ok,
               expected=f"> {before_len} chars", actual=f"{after_len} chars", locator=qc.editor)

    actual = (f"Clicking '{FIXTURE_QUESTION}' correctly inserted content into the editor "
              f"({before_len} -> {after_len} chars)." if ok else
              f"The editor's content did not grow as expected ({before_len} -> {after_len} chars).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_questionnairecreator_03_start_over_shows_confirmation(page, result):
    case = Case(
        page, "QuestionnaireCreator_03", FEATURE, "'Start Over' shows a confirmation dialog before clearing",
        description="Clicking 'Start Over' must show a 'Confirm Start Over' dialog with 'No' and 'Yes' "
                     "options, rather than clearing the editor immediately.",
        precondition="User is logged in and on Questionnaire Creator, with at least one question "
                     "already inserted ('Start Over' is disabled - by design - when there's nothing "
                     "to reset, so this test ensures that precondition itself rather than assuming it).",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Questionnaire Creator\n2. Ensure the editor has content (insert "
              f"'{FIXTURE_QUESTION}' if empty)\n3. Click 'Start Over'\n"
              f"4. Verify the confirmation dialog and its No/Yes buttons are visible",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Ensure the editor has content so 'Start Over' is enabled")
    if not qc.start_over_button.is_enabled():
        case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
                   force=True, native_js=True)
        page.wait_for_timeout(800)

    case.step(3, "Click 'Start Over'")
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(700)

    case.step(4, "Verify the confirmation dialog and its buttons")
    dialog_ok = case.verify_visible(qc.start_over_dialog, "'Confirm Start Over' dialog")
    yes_ok = case.verify_visible(qc.start_over_yes, "'Yes' button")
    no_ok = case.verify_visible(qc.start_over_no, "'No' button")
    ok = dialog_ok and yes_ok and no_ok
    case.check("'Confirm Start Over' dialog with No/Yes is shown", ok,
               expected="dialog_ok=True, yes_ok=True, no_ok=True",
               actual=f"dialog_ok={dialog_ok}, yes_ok={yes_ok}, no_ok={no_ok}")

    # Dismiss without confirming, to avoid affecting state for later tests.
    if no_ok:
        case.click(qc.start_over_no, "'No' (dismiss confirmation)")
        page.wait_for_timeout(500)

    actual = ("'Start Over' correctly showed a confirmation dialog with No/Yes before clearing anything."
              if ok else f"The confirmation dialog did not behave as expected (dialog_ok={dialog_ok}, "
              f"yes_ok={yes_ok}, no_ok={no_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_questionnairecreator_04_start_over_no_keeps_content(page, result):
    case = Case(
        page, "QuestionnaireCreator_04", FEATURE, "Clicking 'No' on the Start Over confirmation keeps the editor content",
        description=f"After inserting '{FIXTURE_QUESTION}', clicking 'Start Over' then 'No' must leave the "
                     f"editor's content unchanged (the reset must not happen until 'Yes' is confirmed).",
        precondition="User is logged in and on Questionnaire Creator.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Questionnaire Creator\n2. Click '{FIXTURE_QUESTION}' to add content\n"
              f"3. Click 'Start Over', then 'No'\n4. Verify the editor content is unchanged",
    )
    qc = _login_and_open(case, page)
    case.step(2, f"Click '{FIXTURE_QUESTION}' to add content")
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)
    before_len = len(qc.editor_html())

    case.step(3, "Click 'Start Over', then 'No'")
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(600)
    case.click(qc.start_over_no, "'No' (decline Start Over)")
    page.wait_for_timeout(800)

    case.step(4, "Verify the editor content is unchanged")
    after_len = len(qc.editor_html())
    ok = after_len == before_len and after_len > 0
    case.check("Editor content is unchanged after declining Start Over", ok,
               expected=f"{before_len} chars", actual=f"{after_len} chars", locator=qc.editor)

    actual = (f"Declining Start Over correctly left the editor content unchanged ({after_len} chars)."
              if ok else f"Editor content changed unexpectedly after declining Start Over "
              f"({before_len} -> {after_len} chars).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_questionnairecreator_05_start_over_yes_clears_editor(page, result):
    case = Case(
        page, "QuestionnaireCreator_05", FEATURE, "Confirming 'Start Over' clears the editor",
        description=f"After inserting '{FIXTURE_QUESTION}', clicking 'Start Over' then 'Yes' must empty "
                     f"the editor's content.",
        precondition="User is logged in and on Questionnaire Creator.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Questionnaire Creator\n2. Click '{FIXTURE_QUESTION}' to add content\n"
              f"3. Click 'Start Over', then 'Yes'\n4. Verify the editor is empty",
    )
    qc = _login_and_open(case, page)
    case.step(2, f"Click '{FIXTURE_QUESTION}' to add content")
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)

    case.step(3, "Click 'Start Over', then 'Yes'")
    _start_over_and_confirm(case, page, qc)

    case.step(4, "Verify the editor is empty")
    empty_ok = qc.editor_is_empty()
    case.check("Editor is empty after confirming Start Over", empty_ok,
               expected=True, actual=empty_ok, locator=qc.editor)

    ok = empty_ok
    actual = ("Confirming 'Start Over' correctly cleared the editor." if ok else
              f"The editor still had content after confirming Start Over (html={qc.editor_html()[:200]!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_questionnairecreator_06_add_to_project_opens_dialog(page, result):
    case = Case(
        page, "QuestionnaireCreator_06", FEATURE, "'Add to Project' opens a project-target dialog",
        description="'Add to Project' only renders once the editor has content (confirmed live - see "
                     "pages/tools_questionnaire_creator_page.py), so this case inserts a question first. "
                     "Clicking 'Add to Project' must then open a dialog for saving the current "
                     "questionnaire content into a Tools > Projects project.",
        precondition="User is logged in and on Questionnaire Creator.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Questionnaire Creator\n2. Click '{FIXTURE_QUESTION}' to add content\n"
              f"3. Click 'Add to Project'\n4. Verify a dialog/modal opens",
    )
    qc = _login_and_open(case, page)
    case.step(2, f"Click '{FIXTURE_QUESTION}' to add content")
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)

    case.step(3, "Click 'Add to Project'")
    before_dialogs = page.locator("[role='dialog']").count()
    case.click(qc.add_to_project_button, "'Add to Project' button")
    page.wait_for_timeout(800)

    case.step(4, "Verify a dialog/modal opens")
    after_dialogs = page.locator("[role='dialog']").count()
    ok = after_dialogs > before_dialogs
    case.check("A dialog opened after clicking 'Add to Project'", ok,
               expected=f"> {before_dialogs} dialogs", actual=f"{after_dialogs} dialogs")

    page.keyboard.press("Escape")
    page.wait_for_timeout(400)

    actual = (f"'Add to Project' correctly opened a dialog ({before_dialogs} -> {after_dialogs})." if ok else
              f"No new dialog was detected after clicking 'Add to Project' ({before_dialogs} -> "
              f"{after_dialogs}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_questionnairecreator_07_add_to_project_saves_and_appears_in_projects(page, result):
    target_project = _unique_title("A2P")
    item_title = _unique_title("A2PItem")
    case = Case(
        page, "QuestionnaireCreator_07", FEATURE,
        "'Add to Project' end-to-end: content saved via the dialog actually lands in the target project",
        description=f"Closes the gap deliberately left open by QuestionnaireCreator_06 (which only checked "
                     f"the dialog opens): inserts '{FIXTURE_QUESTION}', opens 'Add to Project', switches to "
                     f"'To an Existing Project' (a target project created via Tools > Projects for this "
                     f"test, '{target_project}'), fills the required 'Title' field ('{item_title}'), submits, "
                     f"and then cross-page-verifies on the Projects page that this exact item row was really "
                     f"saved - proving the complete business functionality, not just that a modal opens. "
                     f"Confirmed live via network capture: submitting fires "
                     f"'POST .../api/Project/AddToProject' with the Row/ProjectName/ProjectId payload -> 200 "
                     f"'{{\"isSuccess\":true}}' (see pages/tools_questionnaire_creator_page.py).",
        precondition="User is logged in.",
        test_data=f"Target project: {target_project}; Item title: {item_title}; Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open Tools > Projects; create '{target_project}'\n"
              f"2. Open Questionnaire Creator and insert '{FIXTURE_QUESTION}'\n"
              f"3. Click 'Add to Project', switch to 'To an Existing Project', select '{target_project}', "
              f"fill Title '{item_title}', click Add\n"
              f"4. Verify the AddToProject network call succeeded\n"
              f"5. Open Tools > Projects, select '{target_project}', verify the item row's Title matches\n"
              f"6. Clean up: delete '{target_project}'; reset the editor via Start Over",
    )
    perform_login(case, page)
    menu = ToolsMenu(page)

    case.step(1, f"Open Tools > Projects and create target project '{target_project}'")
    case.action("Opening Tools > Projects via the nav dropdown", kind="navigate")
    menu.open_item("Projects")
    projects = ProjectsPage(page)
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)
    case.fill(projects.modal_name_input, target_project, "'Project Name' field")
    case.click(projects.modal_save_button, "'Save' button")
    page.wait_for_timeout(1200)
    target_created = projects.project_exists(target_project)

    case.step(2, f"Open Questionnaire Creator and insert '{FIXTURE_QUESTION}'")
    case.action("Opening Tools > Questionnaire Creator via the nav dropdown", kind="navigate")
    menu.open_item("Questionnaire Creator")
    qc = QuestionnaireCreatorPage(page)
    case.click(qc.question_node(FIXTURE_QUESTION).first, f"'{FIXTURE_QUESTION}' tree question",
               force=True, native_js=True)
    page.wait_for_timeout(1000)

    case.step(3, f"Add to Project -> existing project '{target_project}', Title '{item_title}'")
    add_to_project_ok = False
    response_body = {}
    if target_created:
        case.click(qc.add_to_project_button, "'Add to Project' button")
        page.wait_for_timeout(800)
        case.click(qc.add_to_project_existing_radio, "'To an Existing Project' option")
        page.wait_for_timeout(500)
        case.click(qc.add_to_project_existing_picker, "'Select Existing Project' picker")
        page.wait_for_timeout(500)
        option = qc.add_to_project_existing_option(target_project)
        add_to_project_ok = option.count() > 0
        if add_to_project_ok:
            case.click(option.first, f"'{target_project}' option")
            page.wait_for_timeout(400)
            case.fill(qc.add_to_project_title_input, item_title, "'Title' field")
            with page.expect_response(lambda r: "AddToProject" in r.url) as resp_info:
                case.click(qc.add_to_project_submit_button, "'Add' button")
            response_body = resp_info.value.json()
            page.wait_for_timeout(1200)

    case.step(4, "Verify the AddToProject network call succeeded")
    api_ok = target_created and add_to_project_ok and response_body.get("isSuccess") is True
    case.check("AddToProject API call returned isSuccess=true", api_ok,
               expected='{"isSuccess": true}', actual=response_body)

    case.step(5, f"Open Tools > Projects, select '{target_project}', verify the item row's Title")
    item_found = False
    if api_ok:
        case.action("Opening Tools > Projects via the nav dropdown", kind="navigate")
        menu.open_item("Projects")
        projects = ProjectsPage(page)
        title_span = projects.project_title(target_project)
        case.click(title_span.first, f"'{target_project}' project title")
        page.wait_for_timeout(1500)
        table_visible = case.verify_visible(projects.table.first, "project item table")
        if table_visible and projects.table_rows.count() > 0:
            row_title = projects.item_table_row_title_value(0)
            item_found = row_title == item_title
            case.check(f"The saved item's Title cell matches '{item_title}'", item_found,
                       expected=item_title, actual=row_title)

    ok = target_created and add_to_project_ok and api_ok and item_found

    case.step(6, f"Clean up: delete '{target_project}'; reset the editor via Start Over")
    if projects.project_exists(target_project):
        delete_link = projects.row_action(target_project, "Delete")
        case.click(delete_link, f"'Delete' action for '{target_project}'")
        page.wait_for_timeout(600)
        case.click(projects.delete_confirm_button, "'Delete' confirm button")
        page.wait_for_timeout(1000)
    case.action("Opening Tools > Questionnaire Creator via the nav dropdown", kind="navigate")
    menu.open_item("Questionnaire Creator")
    qc = QuestionnaireCreatorPage(page)
    if qc.start_over_button.is_enabled():
        _start_over_and_confirm(case, page, qc)

    actual = (f"'Add to Project' correctly saved '{item_title}' into '{target_project}', confirmed by "
              f"cross-page verification on the Projects page's item table." if ok else
              f"The end-to-end Add to Project flow did not complete as expected (target_created="
              f"{target_created}, add_to_project_ok={add_to_project_ok}, api_ok={api_ok}, "
              f"item_found={item_found}).")
    result(case, actual, ok)
    assert ok, actual
