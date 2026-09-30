"""Tools > Projects (/wta/Project). See pages/tools_projects_page.py for the
full confirmed-live layout notes.

Every test that creates a project here uses a unique, clearly-tagged title
(`ToolsQA_<timestamp>_...`) and deletes it again before the test ends, so
this suite does not add to the dozens of pre-existing projects already in
this shared live account from prior manual/automation use - a repeatable
run must not accumulate garbage in a real, shared application."""
import time

import pytest

from pages.tools_menu import ToolsMenu
from pages.tools_projects_page import ProjectsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Tools Projects"


def _unique_title(tag: str) -> str:
    return f"ToolsQA_{tag}_{int(time.time() * 1000)}"


def _login_and_open(case, page):
    perform_login(case, page)
    menu = ToolsMenu(page)
    case.action("Opening Tools > Projects via the nav dropdown", kind="navigate")
    menu.open_item("Projects")
    return ProjectsPage(page)


def _create_project(case, page, projects: ProjectsPage, title: str):
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)
    case.fill(projects.modal_name_input, title, "'Project Name' field")
    case.click(projects.modal_save_button, "'Save' button")
    page.wait_for_timeout(1200)


def _delete_project(case, page, projects: ProjectsPage, title: str):
    delete_link = projects.row_action(title, "Delete")
    case.click(delete_link, f"'Delete' action for '{title}'")
    page.wait_for_timeout(600)
    case.click(projects.delete_confirm_button, "'Delete' confirm button")
    page.wait_for_timeout(1000)


@pytest.mark.smoke
def test_projects_01_page_loads_with_existing_projects(page, result):
    case = Case(
        page, "Projects_01", FEATURE, "Projects page loads with the project list and 'New Project' control",
        description="The page must load at /wta/Project with the 'New Project' button visible and at "
                     "least one existing project listed (this account has prior saved projects).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Tools > Projects\n2. Verify URL and 'New Project' button\n"
              "3. Verify at least one existing project row is visible",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Verify URL and 'New Project' button")
    url_ok = "/wta/Project" in page.url
    new_btn_ok = case.verify_visible(projects.new_project_button, "'New Project' button")

    case.step(3, "Verify at least one existing project row is visible")
    rows_ok = projects.page.get_by_text("Edit", exact=True).count() > 0
    ok = url_ok and new_btn_ok and rows_ok
    case.check("Projects page loads with 'New Project' and an existing project list", ok,
               expected="url_ok=True, new_btn_ok=True, rows_ok=True",
               actual=f"url_ok={url_ok}, new_btn_ok={new_btn_ok}, rows_ok={rows_ok}")

    actual = (f"Projects loaded correctly at {page.url} with existing projects listed." if ok else
              f"Projects did not load as expected (url_ok={url_ok}, new_btn_ok={new_btn_ok}, "
              f"rows_ok={rows_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_02_new_project_save_disabled_until_name_entered(page, result):
    case = Case(
        page, "Projects_02", FEATURE, "'New Project' Save is disabled until a project name is entered",
        description="Opening 'New Project' with a blank 'Project Name' field must leave the Save button "
                     "disabled (the app's client-side validation for a required field), and Cancel must "
                     "close the modal without creating any project.",
        precondition="User is logged in and on Tools > Projects.",
        test_data="-",
        steps="1. Log in and open Tools > Projects\n2. Open 'New Project'\n"
              "3. Verify Save is disabled with an empty name\n4. Click Cancel and verify the modal closes",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Open 'New Project'")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)

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
def test_projects_03_create_new_project(page, result):
    title = _unique_title("Create")
    case = Case(
        page, "Projects_03", FEATURE, "Creating a new project adds it to the project list",
        description=f"Filling 'Project Name' with a unique title ({title}) and clicking Save must add a "
                     f"new project with that exact title to the list.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{title}'\n"
              f"3. Verify '{title}' appears in the project list\n4. Clean up: delete '{title}'",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)

    case.step(3, f"Verify '{title}' appears in the project list")
    created_ok = case.verify_visible(projects.project_title(title), f"'{title}' project row")
    case.check(f"New project '{title}' appears in the list after Save", created_ok,
               expected=True, actual=created_ok)

    case.step(4, f"Clean up: delete '{title}'")
    if created_ok:
        _delete_project(case, page, projects, title)
        cleanup_ok = not projects.project_exists(title)
    else:
        cleanup_ok = True  # nothing to clean up

    ok = created_ok
    actual = (f"Creating a project with name '{title}' correctly added it to the list "
              f"(cleanup delete succeeded={cleanup_ok})." if ok else
              f"The new project '{title}' did not appear in the list after Save.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_projects_04_rename_project(page, result):
    original = _unique_title("Rename")
    renamed = original + "_RENAMED"
    case = Case(
        page, "Projects_04", FEATURE, "Editing a project renames it (Update)",
        description=f"Creating a project ({original}), then using its 'Edit' action to change the name to "
                     f"{renamed} and clicking Update must replace the title in the list.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Original: {original} -> Renamed: {renamed}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{original}'\n"
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
        page.wait_for_timeout(600)
        case.fill(projects.modal_name_input, renamed, "'Project Name' field (rename)")
        case.click(projects.modal_update_button, "'Update' button")
        page.wait_for_timeout(1200)

    case.step(4, f"Verify '{renamed}' appears and '{original}' no longer does")
    renamed_ok = setup_ok and projects.project_exists(renamed)
    old_gone_ok = setup_ok and not projects.project_exists(original)
    ok = setup_ok and renamed_ok and old_gone_ok
    case.check("Renaming a project updates its title in the list", ok,
                expected=f"'{renamed}' present, '{original}' absent",
                actual=f"renamed_present={renamed_ok}, original_absent={old_gone_ok}, setup_ok={setup_ok}")

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
def test_projects_05_delete_confirmation_cancel_keeps_project(page, result):
    title = _unique_title("CancelDelete")
    case = Case(
        page, "Projects_05", FEATURE, "Cancelling the delete confirmation keeps the project",
        description=f"Creating a project ({title}), clicking its 'Delete' action, then clicking 'Cancel' "
                     f"on the 'Confirm Delete' dialog must leave the project in the list untouched.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{title}'\n"
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
    case.check("Cancelling the delete confirmation left the project in place", ok,
               expected=True, actual=still_exists)

    case.step(5, f"Clean up: delete '{title}' for real")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"Cancelling the delete confirmation for '{title}' correctly left it in the project list."
              if ok else f"The project was unexpectedly removed after cancelling delete (setup_ok="
              f"{setup_ok}, still_exists={still_exists}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_06_selecting_project_shows_item_table(page, result):
    case = Case(
        page, "Projects_06", FEATURE, "Selecting an existing project shows its item table",
        description="Clicking an existing project's title must switch the detail pane to a table with the "
                     "confirmed columns: '#', 'Title', 'Description', 'Jurisdiction', 'Type'.",
        precondition="User is logged in and on Tools > Projects, with at least one existing project.",
        test_data="-",
        steps="1. Log in and open Tools > Projects\n2. Click the first existing project's title\n"
              "3. Verify the detail table shows the expected columns",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Click the first existing project's title")
    edit_links = page.get_by_text("Edit", exact=True)
    has_existing = edit_links.count() > 0
    if has_existing:
        # The row title is the sibling <span> right before the Export/Edit/Delete action group.
        first_row = edit_links.first.locator(
            "xpath=ancestor::div[contains(@class,'flex-col')][1]"
        )
        title_span = first_row.locator("span.text-14-medium").first
        case.click(title_span, "First existing project's title")
        page.wait_for_timeout(1200)

    case.step(3, "Verify the detail table shows the expected columns")
    table_visible = has_existing and case.verify_visible(projects.table.first, "project item table")
    headers = projects.table.first.locator("th").all_inner_texts() if table_visible else []
    expected_cols = ["#", "Title", "Description", "Jurisdiction", "Type"]
    headers_ok = table_visible and all(col in headers for col in expected_cols)
    ok = has_existing and table_visible and headers_ok
    case.check("Project detail table shows the expected columns", ok,
               expected=expected_cols, actual=headers, locator=projects.table.first if table_visible else None)

    actual = (f"Selecting a project correctly showed its item table with headers {headers}." if ok else
              f"The project detail table did not match expectations (has_existing={has_existing}, "
              f"table_visible={table_visible}, headers={headers}).")
    result(case, actual, ok)
    assert ok, actual
