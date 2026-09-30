"""Tools > Projects (/wta/Project). See pages/tools_projects_page.py for the
full confirmed-live layout notes.

Every test that creates a project here uses a unique, clearly-tagged title
(`ToolsQA_<timestamp>_...`) and deletes it again before the test ends, so
this suite does not add to the dozens of pre-existing projects already in
this shared live account from prior manual/automation use - a repeatable
run must not accumulate garbage in a real, shared application.

Projects_07 onward add the deeper coverage requested on top of the
create/rename/delete/select-project basics above: real network-level
validation of the Create/Rename/Delete calls, more thorough required-field
behavior (whitespace-only, padded, very-long names), duplicate-name
handling, special-character/XSS-adjacent input, and reload persistence -
see pages/tools_projects_page.py's module docstring for the confirmed-live
API shapes and gaps these tests assert against."""
import time

import pytest

from pages.tools_menu import ToolsMenu
from pages.tools_projects_page import ProjectsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "Tools Projects"

PROJECT_API = "https://regpluswta.api.kaz.com.bd/api/Project"


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


@pytest.mark.regression
def test_projects_07_create_network_request_and_response(page, result):
    title = _unique_title("CreateNet")
    case = Case(
        page, "Projects_07", FEATURE, "Creating a project sends the real CreateProject API call and response",
        description=f"Clicking Save for a new project ({title}) must fire a "
                     f"'POST {PROJECT_API}/CreateProject' request with the typed name, and the response "
                     f"must be HTTP 200 with a JSON body of the confirmed-live shape "
                     f"'{{\"id\":<newId>,\"hasError\":false}}' - a real, non-zero id and hasError=false.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Open 'New Project', fill '{title}'\n"
              f"3. Click Save while capturing the CreateProject network call\n"
              f"4. Verify method, endpoint, status 200 and response body shape\n"
              f"5. Clean up: delete '{title}'",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Open 'New Project', fill '{title}'")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)
    case.fill(projects.modal_name_input, title, "'Project Name' field")

    case.step(3, "Click Save while capturing the CreateProject network call")
    with page.expect_response(lambda r: "CreateProject" in r.url) as resp_info:
        case.click(projects.modal_save_button, "'Save' button")
    response = resp_info.value
    body = response.json()
    page.wait_for_timeout(1000)

    case.step(4, "Verify method, endpoint, status 200 and response body shape")
    method_ok = response.request.method == "POST"
    endpoint_ok = f"{PROJECT_API}/CreateProject" in response.url
    status_ok = response.status == 200
    body_ok = body.get("hasError") is False and isinstance(body.get("id"), int) and body.get("id") > 0
    request_payload = response.request.post_data_json or {}
    payload_ok = request_payload.get("name") == title

    ok = method_ok and endpoint_ok and status_ok and body_ok and payload_ok
    case.check("CreateProject network call and response match the confirmed-live API shape", ok,
               expected="POST .../CreateProject, name in payload, status=200, {hasError:false, id:<int>}",
               actual=f"method={response.request.method}, url={response.url}, status={response.status}, "
                      f"payload={request_payload}, body={body}")

    case.step(5, f"Clean up: delete '{title}'")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"Creating '{title}' fired the expected CreateProject POST and returned "
              f"{{'id': {body.get('id')}, 'hasError': {body.get('hasError')}}}." if ok else
              f"The CreateProject network call/response did not match expectations (method_ok={method_ok}, "
              f"endpoint_ok={endpoint_ok}, status_ok={status_ok}, body_ok={body_ok}, payload_ok={payload_ok}, "
              f"body={body}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_08_rename_network_request_and_response(page, result):
    original = _unique_title("RenameNet")
    renamed = original + "_UPD"
    case = Case(
        page, "Projects_08", FEATURE, "Renaming a project sends the real RenameProject API call and response",
        description=f"Editing a project ({original} -> {renamed}) and clicking Update must fire a "
                     f"'POST {PROJECT_API}/RenameProject' request with the new name, and the response "
                     f"must be HTTP 200 with the confirmed-live shape '{{\"id\":<sameId>,\"hasError\":false}}'.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Original: {original} -> Renamed: {renamed}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{original}'\n"
              f"3. Edit it, change the name to '{renamed}', click Update while capturing the network call\n"
              f"4. Verify method, endpoint, status 200 and response body shape\n"
              f"5. Clean up: delete '{renamed}'",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{original}'")
    _create_project(case, page, projects, original)
    setup_ok = projects.project_exists(original)

    case.step(3, f"Edit it, rename to '{renamed}', click Update while capturing the network call")
    body, request_payload, response = {}, {}, None
    if setup_ok:
        edit_link = projects.row_action(original, "Edit")
        case.click(edit_link, f"'Edit' action for '{original}'")
        page.wait_for_timeout(600)
        case.fill(projects.modal_name_input, renamed, "'Project Name' field (rename)")
        with page.expect_response(lambda r: "RenameProject" in r.url) as resp_info:
            case.click(projects.modal_update_button, "'Update' button")
        response = resp_info.value
        body = response.json()
        request_payload = response.request.post_data_json or {}
        page.wait_for_timeout(1000)

    case.step(4, "Verify method, endpoint, status 200 and response body shape")
    method_ok = setup_ok and response.request.method == "POST"
    endpoint_ok = setup_ok and f"{PROJECT_API}/RenameProject" in response.url
    status_ok = setup_ok and response.status == 200
    body_ok = setup_ok and body.get("hasError") is False and isinstance(body.get("id"), int)
    payload_ok = setup_ok and request_payload.get("name") == renamed

    ok = setup_ok and method_ok and endpoint_ok and status_ok and body_ok and payload_ok
    case.check("RenameProject network call and response match the confirmed-live API shape", ok,
               expected="POST .../RenameProject, new name in payload, status=200, {hasError:false, id:<int>}",
               actual=f"setup_ok={setup_ok}, payload={request_payload}, "
                      f"status={getattr(response, 'status', None)}, body={body}")

    case.step(5, f"Clean up: delete '{renamed}'")
    cleanup_title = renamed if body_ok else original
    if projects.project_exists(cleanup_title):
        _delete_project(case, page, projects, cleanup_title)

    actual = (f"Renaming '{original}' to '{renamed}' fired the expected RenameProject POST and returned "
              f"{{'id': {body.get('id')}, 'hasError': {body.get('hasError')}}}." if ok else
              f"The RenameProject network call/response did not match expectations (setup_ok={setup_ok}, "
              f"method_ok={method_ok}, endpoint_ok={endpoint_ok}, status_ok={status_ok}, body_ok={body_ok}, "
              f"payload_ok={payload_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_09_delete_network_request_and_authoritative_removal(page, result):
    title = _unique_title("DeleteNet")
    case = Case(
        page, "Projects_09", FEATURE, "Deleting a project sends the real Delete API call and actually removes it",
        description=f"Deleting a project ({title}) must fire a 'POST {PROJECT_API}/Delete' request with "
                     f"HTTP 200, and the project must be genuinely gone from the account afterwards "
                     f"(re-fetched via the app's own follow-up GetProjects call, not just the UI's "
                     f"optimistic removal). NOTE (confirmed live - see pages/tools_projects_page.py): "
                     f"the Delete response body shape differs from Create/Rename "
                     f"('{{\"isSuccess\":<bool>,\"error\":...}}'), and 'isSuccess' has been observed to "
                     f"intermittently report false (an EF Core DbContext-threading error) even when the "
                     f"project was in fact removed - so this test treats HTTP 200 plus the project's real "
                     f"absence from the next GetProjects response as the authoritative pass condition, "
                     f"not the possibly-flaky 'isSuccess' field alone.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{title}'\n"
              f"3. Delete it while capturing the Delete request and the follow-up GetProjects response\n"
              f"4. Verify status 200 and the project's real absence from GetProjects",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)
    setup_ok = projects.project_exists(title)

    case.step(3, "Delete it while capturing the Delete request and the follow-up GetProjects response")
    delete_response, projects_after = None, []
    if setup_ok:
        delete_link = projects.row_action(title, "Delete")
        case.click(delete_link, f"'Delete' action for '{title}'")
        page.wait_for_timeout(600)
        with page.expect_response(lambda r: r.url.rstrip("/").endswith("/Project/Delete")) as delete_info, \
             page.expect_response(lambda r: "GetProjects" in r.url) as list_info:
            case.click(projects.delete_confirm_button, "'Delete' confirm button")
        delete_response = delete_info.value
        projects_after = list_info.value.json()
        page.wait_for_timeout(1000)

    case.step(4, "Verify status 200 and the project's real absence from GetProjects")
    method_ok = setup_ok and delete_response.request.method == "POST"
    status_ok = setup_ok and delete_response.status == 200
    removed_ok = setup_ok and not any(p.get("name") == title for p in projects_after)
    is_success_reported = delete_response.json().get("isSuccess") if setup_ok else None

    ok = setup_ok and method_ok and status_ok and removed_ok
    case.check("Delete fired a 200 POST and the project is genuinely absent from GetProjects", ok,
               expected="status=200, project absent from GetProjects",
               actual=f"setup_ok={setup_ok}, status={getattr(delete_response, 'status', None)}, "
                      f"removed_ok={removed_ok}, isSuccess_reported={is_success_reported}")

    case.step(5, "Clean up: confirm no leftover row for a non-2xx/edge case")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"Deleting '{title}' correctly returned HTTP 200 and the project was genuinely gone from "
              f"GetProjects afterwards (isSuccess reported as {is_success_reported})." if ok else
              f"The Delete network call/outcome did not match expectations (setup_ok={setup_ok}, "
              f"method_ok={method_ok}, status_ok={status_ok}, removed_ok={removed_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_10_whitespace_only_name_is_not_treated_as_empty(page, result):
    case = Case(
        page, "Projects_10", FEATURE, "A whitespace-only project name is NOT treated as empty by Save's validation",
        description="Filling 'Project Name' with only spaces ('   ') is confirmed live to leave Save "
                     "ENABLED (only a fully empty string disables it), and the backend accepts it, "
                     "creating a project with a literally blank-looking title. This is documented here as "
                     "a real, live-confirmed gap - the disabled-Save validation signal is not "
                     "whitespace-aware - not silently treated as a pass.",
        precondition="User is logged in and on Tools > Projects.",
        test_data="Project name: '   ' (3 spaces)",
        steps="1. Log in and open Tools > Projects\n2. Open 'New Project', fill '   ' (whitespace only)\n"
              "3. Verify Save is enabled for whitespace-only input\n"
              "4. Save it and verify a project was actually created\n5. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Open 'New Project', fill '   ' (whitespace only)")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)
    case.fill(projects.modal_name_input, "   ", "'Project Name' field (whitespace only)")

    case.step(3, "Verify Save is enabled for whitespace-only input (confirmed-live gap)")
    save_enabled = projects.modal_save_button.is_enabled()
    case.check("Save is enabled for a whitespace-only name (not treated as empty - documented gap)",
               save_enabled, expected=True, actual=save_enabled, locator=projects.modal_save_button)

    case.step(4, "Save it and verify a project was actually created")
    with page.expect_response(lambda r: "CreateProject" in r.url) as resp_info:
        case.click(projects.modal_save_button, "'Save' button")
    body = resp_info.value.json()
    page.wait_for_timeout(1000)
    created_ok = body.get("hasError") is False
    row = projects.blank_or_whitespace_title_row()
    row_found = row is not None

    ok = save_enabled and created_ok and row_found
    case.check("A whitespace-only name was accepted end-to-end (backend + list) - documented gap, not a pass "
               "we're papering over", ok,
               expected="save_enabled=True, created_ok=True, row_found=True",
               actual=f"save_enabled={save_enabled}, created_ok={created_ok}, row_found={row_found}, "
                      f"response={body}")

    case.step(5, "Clean up: delete the whitespace-only project")
    if row_found:
        row.hover()
        page.wait_for_timeout(200)
        case.click(row.get_by_text("Delete", exact=True), "'Delete' action for the whitespace-only project")
        page.wait_for_timeout(600)
        case.click(projects.delete_confirm_button, "'Delete' confirm button")
        page.wait_for_timeout(1000)

    actual = ("Whitespace-only ('   ') was correctly documented as NOT blocked: Save stayed enabled and the "
              "backend created the project - a real, live-confirmed validation gap." if ok else
              f"Whitespace-only handling differed from what was confirmed live (save_enabled={save_enabled}, "
              f"created_ok={created_ok}, row_found={row_found}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_11_leading_trailing_whitespace_is_preserved_verbatim(page, result):
    core = _unique_title("Whitespace")
    padded = f"  {core}  "
    case = Case(
        page, "Projects_11", FEATURE, "Leading/trailing whitespace on an otherwise-valid name is preserved verbatim",
        description=f"Creating a project with a name padded with leading/trailing spaces ('{padded}') is "
                     f"confirmed live to be saved EXACTLY as typed - the app does not trim it client-side "
                     f"before enabling Save, nor server-side in storage. Documented as an observation about "
                     f"real app behavior, not asserted as right or wrong.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name (with padding): {padded!r}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named {padded!r}\n"
              f"3. Verify the CreateProject payload/response preserved the padding verbatim\n"
              f"4. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named {padded!r}")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)
    case.fill(projects.modal_name_input, padded, "'Project Name' field (padded)")
    with page.expect_response(lambda r: "CreateProject" in r.url) as resp_info:
        case.click(projects.modal_save_button, "'Save' button")
    response = resp_info.value
    request_payload = response.request.post_data_json or {}
    page.wait_for_timeout(1000)

    case.step(3, "Verify the CreateProject payload/response preserved the padding verbatim")
    payload_preserved = request_payload.get("name") == padded
    row_visible = case.verify_visible(projects.project_row(padded), "padded-title project row")
    ok = payload_preserved and row_visible
    case.check("Leading/trailing whitespace in the name was preserved verbatim (not trimmed)", ok,
               expected=f"payload name == {padded!r}", actual=f"payload name == {request_payload.get('name')!r}")

    case.step(4, "Clean up: delete it")
    if row_visible:
        _delete_project(case, page, projects, padded)

    actual = (f"The padded name {padded!r} was saved and listed exactly as typed, with no trimming applied."
              if ok else f"Whitespace preservation did not match what was confirmed live (payload_preserved="
              f"{payload_preserved}, row_visible={row_visible}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_12_very_long_name_has_no_enforced_length_limit(page, result):
    long_name = f"ToolsQA_Long_{int(time.time() * 1000)}_" + ("A" * 260)
    case = Case(
        page, "Projects_12", FEATURE, "A very long (300-char class) project name has no enforced client/server limit",
        description="Confirmed live: the 'Project Name' input has no HTML 'maxlength' attribute, and a "
                     "300-character name is accepted verbatim by both the input and the backend "
                     "(CreateProject responds hasError=false, no truncation/rejection). Documented as a "
                     "real, live-confirmed gap - no length limit is enforced anywhere in this flow.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name length: {len(long_name)} chars",
        steps="1. Log in and open Tools > Projects\n2. Open 'New Project'\n"
              "3. Verify the name input has no 'maxlength' attribute\n"
              f"4. Fill a {len(long_name)}-char name and Save; verify it's accepted untruncated\n"
              "5. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, "Open 'New Project'")
    case.click(projects.new_project_button, "'New Project' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify the name input has no 'maxlength' attribute")
    maxlength_attr = projects.modal_name_input.get_attribute("maxlength")
    no_maxlength = maxlength_attr is None
    case.check("The 'Project Name' input has no 'maxlength' attribute (documented gap)", no_maxlength,
               expected=None, actual=maxlength_attr, locator=projects.modal_name_input)

    case.step(4, f"Fill a {len(long_name)}-char name and Save; verify it's accepted untruncated")
    case.fill(projects.modal_name_input, long_name, "'Project Name' field (very long)")
    input_len = len(projects.modal_name_input.input_value())
    with page.expect_response(lambda r: "CreateProject" in r.url) as resp_info:
        case.click(projects.modal_save_button, "'Save' button")
    body = resp_info.value.json()
    page.wait_for_timeout(1000)
    created_ok = body.get("hasError") is False
    not_truncated = input_len == len(long_name)
    row_visible = case.verify_visible(projects.project_title(long_name), "very-long-name project row")

    ok = no_maxlength and not_truncated and created_ok and row_visible
    case.check("A 300-char-class name was accepted untruncated, client and server side", ok,
               expected=f"input_len=={len(long_name)}, created_ok=True, row_visible=True",
               actual=f"input_len={input_len}, created_ok={created_ok}, row_visible={row_visible}")

    case.step(5, "Clean up: delete it")
    if projects.project_exists(long_name):
        _delete_project(case, page, projects, long_name)

    actual = (f"A {len(long_name)}-char name was correctly accepted with no length limit enforced "
              f"anywhere in the flow." if ok else
              f"Long-name handling did not match what was confirmed live (no_maxlength={no_maxlength}, "
              f"not_truncated={not_truncated}, created_ok={created_ok}, row_visible={row_visible}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_13_duplicate_name_is_blocked_server_side_but_silently(page, result):
    title = _unique_title("Dup")
    case = Case(
        page, "Projects_13", FEATURE, "A true duplicate project name is blocked server-side, but with no visible user feedback",
        description=f"Creating a second project with the exact same name as an existing one ('{title}') is "
                     f"confirmed live to be blocked at the data level - CreateProject responds "
                     f"'{{\"id\":0,\"hasError\":true,\"errorMessage\":\"Please choose another name\"}}' and "
                     f"no duplicate row is created. However, this is ALSO confirmed live to be a real UX "
                     f"gap: the modal simply closes with zero visible feedback to the user (no toast, no "
                     f"inline error) - the rejection is silent. Both are documented and asserted: the app "
                     f"correctly prevents duplicate DATA, but gives the user no correct signal that their "
                     f"second attempt failed.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name (used twice): {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{title}'\n"
              f"3. Attempt to create a second project with the exact same name\n"
              f"4. Verify the backend rejected the duplicate (hasError=true) and no visible error feedback "
              f"is shown to the user\n5. Verify only one row with this title exists\n6. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)
    setup_ok = projects.project_exists(title)

    case.step(3, "Attempt to create a second project with the exact same name")
    dup_body = {}
    if setup_ok:
        case.click(projects.new_project_button, "'New Project' button")
        page.wait_for_timeout(500)
        case.fill(projects.modal_name_input, title, "'Project Name' field (duplicate)")
        with page.expect_response(lambda r: "CreateProject" in r.url) as resp_info:
            case.click(projects.modal_save_button, "'Save' button (duplicate attempt)")
        dup_body = resp_info.value.json()
        page.wait_for_timeout(1000)

    case.step(4, "Verify the backend rejected the duplicate and no visible error feedback is shown")
    rejected_ok = setup_ok and dup_body.get("hasError") is True and dup_body.get("id") == 0
    toast_candidates = page.locator(".Toastify__toast, .rs-message, [role='alert'], .toast, .notification")
    no_visible_feedback = toast_candidates.count() == 0
    case.check("CreateProject correctly rejected the exact-duplicate name (data-level protection)",
               rejected_ok, expected='{"id":0,"hasError":true,...}', actual=dup_body)
    case.check("No toast/inline error is shown to the user for the rejected duplicate (documented UX gap)",
               no_visible_feedback, expected="0 visible feedback elements",
               actual=f"{toast_candidates.count()} candidate elements")

    case.step(5, "Verify only one row with this title exists (no duplicate data created)")
    single_row_ok = setup_ok and projects.project_title(title).count() == 1
    case.check("No duplicate row was actually created despite the silent UI failure", single_row_ok,
               expected=1, actual=projects.project_title(title).count() if setup_ok else "n/a")

    ok = setup_ok and rejected_ok and no_visible_feedback and single_row_ok

    case.step(6, "Clean up: delete it")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"Duplicate creation of '{title}' was correctly blocked at the data level "
              f"(hasError=true, no duplicate row), but the UI gave the user no visible feedback that the "
              f"attempt failed - a real, documented UX gap." if ok else
              f"Duplicate-name handling did not match what was confirmed live (setup_ok={setup_ok}, "
              f"rejected_ok={rejected_ok}, no_visible_feedback={no_visible_feedback}, "
              f"single_row_ok={single_row_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_projects_14_special_character_name_saves_and_renders_safely(page, result):
    tag = int(time.time() * 1000)
    xss_title = f"<script>alert('ToolsQA_{tag}')</script>"
    case = Case(
        page, "Projects_14", FEATURE, "A special-character/XSS-style project name saves and renders safely",
        description=f"Creating a project named literally '{xss_title}' is confirmed live to save and list "
                     f"successfully (the backend does not reject special characters), and to render back as "
                     f"plain escaped text - NOT as a live '<script>' element in the page (0 matches for the "
                     f"raw tag in page HTML). This is a documented XSS-safety PASS for this field, verified "
                     f"live rather than assumed.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {xss_title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{xss_title}'\n"
              f"3. Verify it was saved and is displayed as visible text\n"
              f"4. Verify no live '<script>' tag was injected into the page HTML\n5. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{xss_title}'")
    _create_project(case, page, projects, xss_title)

    case.step(3, "Verify it was saved and is displayed as visible text")
    displayed_ok = case.verify_visible(projects.project_title(xss_title), "special-character project row")
    case.check("The special-character name is saved and rendered as visible text", displayed_ok,
               expected=True, actual=displayed_ok)

    case.step(4, "Verify no live '<script>' tag was injected into the page HTML")
    raw_injected = xss_title in page.content()
    safe_rendering = not raw_injected
    case.check("No live '<script>' tag was injected (safe/escaped rendering, not a real XSS)", safe_rendering,
               expected=False, actual=raw_injected)

    ok = displayed_ok and safe_rendering

    case.step(5, "Clean up: delete it")
    if projects.project_exists(xss_title):
        _delete_project(case, page, projects, xss_title)

    actual = (f"'{xss_title}' saved successfully and rendered as safe, escaped text with no live script "
              f"injection." if ok else
              f"Special-character handling did not match what was confirmed live (displayed_ok={displayed_ok}, "
              f"safe_rendering={safe_rendering}, raw_injected={raw_injected}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_projects_15_created_project_survives_a_page_reload(page, result):
    title = _unique_title("Persist")
    case = Case(
        page, "Projects_15", FEATURE, "A newly created project survives a page reload (real server persistence)",
        description=f"After creating a project ('{title}'), reloading the page must still show it - proving "
                     f"the save is real server-side persistence, not just an optimistic client-side UI "
                     f"update. Confirmed live: unlike a fresh external 'page.goto(\"/wta/Project\")' (which "
                     f"redirects to /wta/Information per the documented Tools deep-link gotcha), "
                     f"'page.reload()' from an already-open /wta/Project page stays on /wta/Project and "
                     f"re-fetches the list from the server, so this test uses reload() rather than "
                     f"re-navigating through the Tools menu.",
        precondition="User is logged in and on Tools > Projects.",
        test_data=f"Project name: {title}",
        steps=f"1. Log in and open Tools > Projects\n2. Create a project named '{title}'\n"
              f"3. Reload the page\n4. Verify the URL is still /wta/Project and '{title}' is still listed\n"
              f"5. Clean up: delete it",
    )
    projects = _login_and_open(case, page)
    case.step(2, f"Create a project named '{title}'")
    _create_project(case, page, projects, title)
    setup_ok = projects.project_exists(title)

    case.step(3, "Reload the page")
    case.action("Reloading /wta/Project", kind="navigate")
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(1000)

    case.step(4, f"Verify the URL is still /wta/Project and '{title}' is still listed")
    url_ok = "/wta/Project" in page.url
    still_listed = case.verify_visible(projects.project_title(title), f"'{title}' after reload")
    ok = setup_ok and url_ok and still_listed
    case.check("The created project survived a reload (real server persistence, no redirect-away)", ok,
               expected="url_ok=True, still_listed=True",
               actual=f"setup_ok={setup_ok}, url={page.url}, still_listed={still_listed}")

    case.step(5, "Clean up: delete it")
    if projects.project_exists(title):
        _delete_project(case, page, projects, title)

    actual = (f"'{title}' correctly survived a page reload, staying on {page.url} - proving real "
              f"server-side persistence." if ok else
              f"Reload persistence did not match expectations (setup_ok={setup_ok}, url_ok={url_ok}, "
              f"still_listed={still_listed}).")
    result(case, actual, ok)
    assert ok, actual
