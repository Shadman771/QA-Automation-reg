"""TPA > Tools > Projects (/tpa/Project). See
pages/tpa/tpa_tools_projects_page.py for the full confirmed-live layout
(hover-only Export/Edit/Delete links, 3-tab detail pane).

Every test that creates a project uses a unique, clearly-tagged title
(`ToolsQA_TPAProj_<timestamp>`) and deletes it again before the test ends,
so this suite does not add to this shared live account's existing
projects (confirmed live: at least one pre-existing "TEST QA" project)."""
import time

import pytest

from pages.tpa.tpa_tools_projects_page import TpaProjectsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Tools Projects"


def _unique_title(tag: str) -> str:
    return f"ToolsQA_TPAProj_{tag}_{int(time.time() * 1000)}"


def _login_and_open(case, page):
    perform_login(case, page)
    projects = TpaProjectsPage(page)
    case.action("Navigating to /tpa/Project", kind="navigate")
    projects.goto()
    return projects


def _create_project(case, page, projects: TpaProjectsPage, title: str):
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(600)
    case.fill(projects.modal_name_input, title, "'Project Name' field")
    case.click(projects.modal_save_button, "'Save' button")
    page.wait_for_timeout(1200)


def _delete_project(case, page, projects: TpaProjectsPage, title: str):
    delete_link = projects.row_action(title, "Delete")
    case.click(delete_link, f"'Delete' action for '{title}'")
    page.wait_for_timeout(600)
    confirm = page.get_by_role("button", name="Delete")
    if confirm.count() > 0:
        case.click(confirm.first, "'Delete' confirm button")
    page.wait_for_timeout(1000)


@pytest.mark.smoke
def test_tpaprojects_01_page_loads_with_existing_projects(page, result):
    case = Case(
        page, "TpaProjects_01", FEATURE, "Projects page loads with the project list and 'New Project' control",
        description="The page must load at /tpa/Project with the 'New Project' button visible and at least "
                     "one existing project listed (this shared account has a prior 'TEST QA' project).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Projects\n2. Verify URL and 'New Project' button\n"
              "3. Verify at least one existing project is listed",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Verify URL and 'New Project' button")
    url_ok = "/tpa/Project" in page.url
    new_btn_ok = case.verify_visible(projects.new_project_button, "'New Project' button")

    case.step(3, "Verify at least one existing project is listed")
    rows_ok = projects.project_title("TEST QA").count() > 0
    ok = url_ok and new_btn_ok and rows_ok
    case.check("Projects page loads with 'New Project' and an existing project list", ok,
               expected="url_ok=True, new_btn_ok=True, rows_ok=True",
               actual=f"url_ok={url_ok}, new_btn_ok={new_btn_ok}, rows_ok={rows_ok}")

    actual = (f"Projects loaded correctly at {page.url} with existing projects listed." if ok else
              f"Projects did not load as expected (url_ok={url_ok}, new_btn_ok={new_btn_ok}, rows_ok={rows_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaprojects_02_create_new_project(page, result):
    title = _unique_title("Create")
    case = Case(
        page, "TpaProjects_02", FEATURE, "Creating a new project adds it to the project list",
        description=f"Filling 'Project Name' with a unique title ({title}) and clicking Save must add a new "
                     f"project with that exact title to the list.",
        precondition="User is logged in and on Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Projects\n2. Create a project named '{title}'\n"
              f"3. Verify '{title}' appears in the project list\n4. Clean up: delete '{title}'",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)

    case.step(3, f"Verify '{title}' appears in the project list")
    created_ok = case.verify_visible(projects.project_title(title), f"'{title}' project row")
    case.check(f"New project '{title}' appears in the list after Save", created_ok, expected=True, actual=created_ok)

    case.step(4, f"Clean up: delete '{title}'")
    if created_ok:
        _delete_project(case, page, projects, title)

    ok = created_ok
    actual = (f"Creating a project named '{title}' correctly added it to the list." if ok else
              f"The new project '{title}' did not appear in the list after Save.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaprojects_03_new_project_save_disabled_until_name_entered(page, result):
    case = Case(
        page, "TpaProjects_03", FEATURE, "'New Project' Save is disabled until a project name is entered",
        description="Opening 'New Project' with a blank 'Project Name' field must leave the Save button "
                     "disabled, and Cancel must close the modal without creating any project.",
        precondition="User is logged in and on Projects.",
        test_data="-",
        steps="1. Log in and open Projects\n2. Open 'New Project'\n3. Verify Save is disabled with an empty name\n"
              "4. Click Cancel and verify the modal closes",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Open 'New Project'")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(600)

    case.step(3, "Verify Save is disabled with an empty name")
    save_disabled = projects.modal_save_button.is_disabled()
    case.check("Save button is disabled while the project name is empty", save_disabled,
               expected=True, actual=save_disabled, locator=projects.modal_save_button)

    case.step(4, "Click Cancel and verify the modal closes")
    case.click(projects.modal_cancel_button, "'Cancel' button")
    page.wait_for_timeout(500)
    modal_closed = projects.modal_name_input.count() == 0 or not projects.modal_name_input.is_visible()

    ok = save_disabled and modal_closed
    case.check("Save was disabled for a blank name and Cancel closed the modal", ok,
               expected="save_disabled=True, modal_closed=True",
               actual=f"save_disabled={save_disabled}, modal_closed={modal_closed}")

    actual = ("'New Project' correctly disabled Save for a blank name and Cancel closed the modal." if ok else
              f"Validation behavior differed from expected (save_disabled={save_disabled}, "
              f"modal_closed={modal_closed}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaprojects_04_rename_project(page, result):
    original = _unique_title("Rename")
    renamed = original + "_RENAMED"
    case = Case(
        page, "TpaProjects_04", FEATURE, "Editing a project renames it (Update)",
        description=f"Creating a project ({original}), then using its hover-revealed 'Edit' action to change "
                     f"the name to {renamed} and clicking Update must replace the title in the list.",
        precondition="User is logged in and on Projects.",
        test_data=f"Original: {original} -> Renamed: {renamed}",
        steps=f"1. Log in and open Projects\n2. Create a project named '{original}'\n"
              f"3. Edit it, change the name to '{renamed}', click Update\n"
              f"4. Verify '{renamed}' appears and '{original}' no longer does\n"
              f"5. Clean up: delete '{renamed}'",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{original}'")
    _create_project(case, page, projects, original)
    setup_ok = projects.project_exists(original)

    case.step(3, f"Edit it and rename to '{renamed}'")
    if setup_ok:
        edit_link = projects.row_action(original, "Edit")
        case.click(edit_link, f"'Edit' action for '{original}'")
        page.wait_for_timeout(800)
        case.fill(projects.modal_name_input, renamed, "'Project Name' field (rename)")
        update_btn = projects.modal_update_button if projects.modal_update_button.count() > 0 else projects.modal_save_button
        case.click(update_btn, "'Update'/'Save' button")
        page.wait_for_timeout(1200)

    case.step(4, f"Verify '{renamed}' appears and '{original}' no longer does")
    renamed_ok = setup_ok and projects.project_exists(renamed)
    old_gone_ok = setup_ok and not projects.project_exists(original)
    ok = setup_ok and renamed_ok and old_gone_ok
    case.check("Renaming a project updates its title in the list", ok,
               expected=f"'{renamed}' present, '{original}' absent",
               actual=f"setup_ok={setup_ok}, renamed_present={renamed_ok}, original_absent={old_gone_ok}")

    case.step(5, f"Clean up: delete '{renamed}'")
    cleanup_title = renamed if renamed_ok else original
    if projects.project_exists(cleanup_title):
        _delete_project(case, page, projects, cleanup_title)

    actual = (f"Renaming '{original}' to '{renamed}' correctly updated the project list." if ok else
              f"Renaming did not behave as expected (setup_ok={setup_ok}, renamed_ok={renamed_ok}, "
              f"old_gone_ok={old_gone_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaprojects_05_delete_confirmation_cancel_keeps_project(page, result):
    title = _unique_title("CancelDelete")
    case = Case(
        page, "TpaProjects_05", FEATURE, "Cancelling the delete confirmation keeps the project",
        description=f"Creating a project ({title}), clicking its 'Delete' action, then clicking 'Cancel' on "
                     f"the confirmation dialog must leave the project in the list untouched.",
        precondition="User is logged in and on Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Projects\n2. Create a project named '{title}'\n"
              f"3. Click Delete, then Cancel on the confirmation dialog\n"
              f"4. Verify '{title}' still exists\n5. Clean up: delete '{title}' for real",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)
    setup_ok = projects.project_exists(title)

    case.step(3, "Click Delete, then Cancel on the confirmation dialog")
    if setup_ok:
        delete_link = projects.row_action(title, "Delete")
        case.click(delete_link, f"'Delete' action for '{title}'")
        page.wait_for_timeout(600)
        case.click(projects.modal_cancel_button, "'Cancel' button on the delete confirmation")
        page.wait_for_timeout(800)

    case.step(4, f"Verify '{title}' still exists")
    still_exists = setup_ok and projects.project_exists(title)
    ok = setup_ok and still_exists
    case.check("Cancelling the delete confirmation left the project in place", ok, expected=True, actual=still_exists)

    case.step(5, f"Clean up: delete '{title}' for real")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"Cancelling the delete confirmation for '{title}' correctly left it in the project list." if ok
              else f"The project was unexpectedly removed after cancelling delete (setup_ok={setup_ok}, "
              f"still_exists={still_exists}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpaprojects_06_selecting_project_shows_tabs_and_detail_table(page, result):
    case = Case(
        page, "TpaProjects_06", FEATURE, "Selecting an existing project shows its 3 tabs and detail table",
        description="Clicking the existing 'TEST QA' project's title must switch the detail pane to show the "
                     "3 confirmed tabs (Regulatory Reports, Research, Documents) and a table with the "
                     "confirmed columns: '#', 'Title', 'Description', 'Path', 'Type'.",
        precondition="User is logged in and on Projects, with the shared 'TEST QA' project present.",
        test_data="-",
        steps="1. Log in and open Projects\n2. Click 'TEST QA' project title\n"
              "3. Verify the 3 tabs and the detail table's expected columns",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Click 'TEST QA' project title")
    has_existing = projects.project_title("TEST QA").count() > 0
    if has_existing:
        case.click(projects.project_title("TEST QA").first, "'TEST QA' project title")
        page.wait_for_timeout(1200)

    case.step(3, "Verify the 3 tabs and the detail table's expected columns")
    tabs_ok = (has_existing and case.verify_visible(projects.tab_regulatory_reports, "'Regulatory Reports' tab")
               and projects.tab_research.count() > 0 and projects.tab_documents.count() > 0)
    headers = projects.detail_table.first.locator("th").all_inner_texts() if tabs_ok else []
    expected_cols = ["#", "Title", "Description", "Path", "Type"]
    headers_ok = tabs_ok and all(any(col in h for h in headers) for col in expected_cols)
    ok = has_existing and tabs_ok and headers_ok
    case.check("Selecting the project shows its 3 tabs and expected detail table columns", ok,
               expected=f"tabs present, columns {expected_cols}",
               actual=f"has_existing={has_existing}, tabs_ok={tabs_ok}, headers={headers}")

    actual = (f"Selecting 'TEST QA' correctly showed its 3 tabs and detail table with headers {headers}."
              if ok else f"The project detail view did not match expectations (has_existing={has_existing}, "
              f"tabs_ok={tabs_ok}, headers={headers}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpaprojects_07_delete_removes_the_project(page, result):
    title = _unique_title("Delete")
    case = Case(
        page, "TpaProjects_07", FEATURE, "Deleting a project removes it from the list",
        description=f"Creating a project ({title}) and then using its hover-revealed 'Delete' action (with "
                     f"confirmation) must remove it from the list.",
        precondition="User is logged in and on Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Projects\n2. Create a project named '{title}'\n"
              f"3. Delete it\n4. Verify '{title}' no longer appears in the list",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)
    setup_ok = projects.project_exists(title)

    case.step(3, f"Delete '{title}'")
    if setup_ok:
        _delete_project(case, page, projects, title)

    case.step(4, f"Verify '{title}' no longer appears in the list")
    removed_ok = setup_ok and not projects.project_exists(title)
    ok = setup_ok and removed_ok
    case.check(f"'{title}' was removed after Delete", ok, expected=True, actual=removed_ok)

    actual = f"Deleting '{title}' correctly removed it from the project list." if ok else \
             f"'{title}' was not correctly removed (setup_ok={setup_ok}, removed_ok={removed_ok})."
    result(case, actual, ok)
    assert ok, actual
