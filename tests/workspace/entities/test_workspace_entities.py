"""Workspace > Entities (`/companydata/entities/information/data/`). See
pages/workspace/workspace_entities_page.py for the full confirmed-live
layout: the Entity Information/TP View/Tax Risk panels, the real sortable
Data table, and the Add Entity wizard modal (opened/validated, never
submitted, per this project's production-safety rule)."""
import pytest

from pages.workspace.workspace_entities_page import WorkspaceEntitiesPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "Workspace Entities"


def _login_and_open(case, page):
    perform_login(case, page)
    entities = WorkspaceEntitiesPage(page)
    case.action("Navigating to Workspace > Entities", kind="navigate")
    entities.goto()
    return entities


@pytest.mark.smoke
def test_workspaceentities_01_page_loads_with_data_grid(page, result):
    case = Case(
        page, "WorkspaceEntities_01", FEATURE, "Entities loads with the Entity Information data grid",
        description="The Entities table must load with at least one real entity row.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Entities\n2. Verify the table is visible with >0 rows",
    )
    entities = _login_and_open(case, page)
    case.step(2, "Verify the table is visible with at least one row")
    table_ok = wait_for_content(entities.table, timeout=20000)
    row_count = entities.entity_row_count() if table_ok else 0
    ok = table_ok and row_count > 0
    case.check("Entities table loads with at least one real row", ok, expected="> 0 rows", actual=str(row_count))

    actual = f"Entities table loaded with {row_count} row(s)." if ok else "Entities table did not load with any rows."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_workspaceentities_02_add_entity_opens_wizard(page, result):
    case = Case(
        page, "WorkspaceEntities_02", FEATURE, "'Add Entity' opens the entity-creation wizard",
        description="Clicking 'Add Entity' must open a modal with the 'Legal Information' step and its "
                     "required fields (ID, Name, Incorporation Jurisdiction, Business Type, Business SIC Code).",
        precondition="User is logged in and on Workspace > Entities.",
        test_data="-",
        steps="1. Log in and open Workspace > Entities\n2. Click 'Add Entity'\n"
              "3. Verify the wizard modal and its required fields are visible\n4. Close the modal via Cancel",
    )
    entities = _login_and_open(case, page)
    case.step(2, "Click 'Add Entity'")
    case.click(entities.add_entity_button, "'Add Entity' button")

    case.step(3, "Verify the wizard modal's Legal Information fields are visible")
    heading_ok = wait_for_content(entities.modal_heading, timeout=10000)
    id_ok = entities.modal_id_input.is_visible()
    name_ok = entities.modal_name_input.is_visible()
    ok = heading_ok and id_ok and name_ok
    case.check("Add Entity wizard shows its Legal Information step (ID/Name fields)", ok,
               expected="modal + ID + Name fields visible",
               actual=f"heading={heading_ok}, id_field={id_ok}, name_field={name_ok}")

    case.step(4, "Close the modal without creating an entity")
    entities.close_add_entity_modal()

    actual = "Add Entity wizard opened with its required fields, then closed without creating anything." if ok else \
        "Add Entity wizard did not open as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspaceentities_03_add_entity_next_disabled_until_required_fields_filled(page, result):
    case = Case(
        page, "WorkspaceEntities_03", FEATURE, "Add Entity wizard's 'Next' stays disabled with an empty form",
        description="With the Legal Information step's required fields still empty, the 'Next' button must "
                     "be disabled (confirmed live via the real `disabled` attribute).",
        precondition="User is logged in and the Add Entity wizard is open.",
        test_data="-",
        steps="1. Log in and open Workspace > Entities\n2. Open 'Add Entity'\n"
              "3. Verify 'Next' is disabled with the form empty\n4. Close the modal via Cancel",
    )
    entities = _login_and_open(case, page)
    case.step(2, "Open 'Add Entity'")
    case.click(entities.add_entity_button, "'Add Entity' button")
    wait_for_content(entities.modal_heading, timeout=10000)

    case.step(3, "Verify 'Next' is disabled while the required fields are empty")
    disabled = entities.is_next_button_disabled()
    ok = disabled
    case.check("'Next' button is disabled until required fields are filled", ok,
               expected="disabled=True", actual=f"disabled={disabled}")

    case.step(4, "Close the modal without creating an entity")
    entities.close_add_entity_modal()

    actual = "'Next' stayed disabled with an empty required form, as expected." if ok else \
        "'Next' was unexpectedly enabled with the required fields still empty."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspaceentities_04_search_narrows_the_grid(page, result):
    case = Case(
        page, "WorkspaceEntities_04", FEATURE, "Searching the Entities grid filters to matching entities",
        description="Searching for an entity name read live from the grid must return at least one row, "
                     "and every remaining row's Entity Name must contain the search term.",
        precondition="User is logged in.",
        test_data="Search term: the last row's Entity Name, read at runtime (no hardcoded entity)",
        steps="1. Log in and open Workspace > Entities\n2. Read the baseline rows and pick a real entity name\n"
              "3. Type it into the search box\n4. Verify >=1 row remains and every row matches the term",
    )
    entities = _login_and_open(case, page)
    wait_for_content(entities.table_rows, timeout=20000)
    case.step(2, "Read the baseline rows and pick a real entity name")
    names = [n for n in entities.entity_names() if n]
    baseline = len(names)
    term = names[-1] if names else ""
    case.check("Grid has at least one named entity to search for", bool(term),
               expected="non-empty entity name", actual=repr(term))

    case.step(3, f"Type '{term}' into the search box")
    case.click(entities.search_input, "Entities search box")
    case.action(f"Typing '{term}' key-by-key (the grid filters on keystrokes, not fill())", kind="type")
    entities.type_search(term)
    page.wait_for_timeout(800)

    case.step(4, "Verify >=1 row remains and every row matches the term")
    filtered = [n for n in entities.entity_names() if n]
    mismatches = [n for n in filtered if term.lower() not in n.lower()]
    ok = bool(term) and len(filtered) >= 1 and not mismatches and len(filtered) <= baseline
    case.check("Search returns only entities matching the term", ok,
               expected=f">=1 row, all containing '{term}', <= {baseline}",
               actual=f"{len(filtered)} row(s), non-matching={mismatches}")

    actual = (f"Searching '{term}' filtered {baseline} rows down to {len(filtered)}, all matching." if ok else
              f"Search for '{term}' did not filter correctly: {len(filtered)} row(s), non-matching={mismatches}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspaceentities_05_entity_name_column_sorted_ascending_by_default(page, result):
    case = Case(
        page, "WorkspaceEntities_05", FEATURE, "'Entity Name' column is sorted ascending by default",
        description="Confirmed live the grid's default URL carries `?sort=entityName:asc`; the 'Entity Name' "
                     "column header's `aria-sort` attribute must reflect that real sorted state.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Entities\n2. Verify the 'Entity Name' header's aria-sort is 'ascending'",
    )
    entities = _login_and_open(case, page)
    wait_for_content(entities.table, timeout=20000)
    case.step(2, "Verify the 'Entity Name' header's aria-sort state")
    sort_state = entities.column_sort_state("Entity Name")
    ok = sort_state == "ascending"
    case.check("'Entity Name' column defaults to ascending sort", ok,
               expected="ascending", actual=sort_state)

    actual = "'Entity Name' column defaulted to ascending sort, as expected." if ok else \
        f"'Entity Name' column's aria-sort was '{sort_state}', not 'ascending'."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspaceentities_06_tp_view_panel_switches_the_grid(page, result):
    case = Case(
        page, "WorkspaceEntities_06", FEATURE, "'TP View' panel's Data link navigates to its own route",
        description="Clicking the 'TP View' panel's 'Data' link must navigate to "
                     "/companydata/entities/transferpricing/data/ and still show a real table.",
        precondition="User is logged in and on Workspace > Entities.",
        test_data="-",
        steps="1. Log in and open Workspace > Entities\n2. Click the 'TP View' panel's Data link\n"
              "3. Verify the URL changed and a table is visible",
    )
    entities = _login_and_open(case, page)
    case.step(2, "Click the 'TP View' panel's Data link")
    case.click(entities.link_tp_view_data, "'TP View' > Data link")
    page.wait_for_load_state("domcontentloaded")

    case.step(3, "Verify the URL changed and a table is visible")
    url_ok = "/companydata/entities/transferpricing/data/" in page.url
    table_ok = wait_for_content(entities.table, timeout=20000)
    ok = url_ok and table_ok
    case.check("TP View navigates to its own route and shows a table", ok,
               expected="transferpricing/data/ URL + table visible",
               actual=f"url={page.url}, table={table_ok}")

    actual = "TP View panel correctly navigated to its own Data grid." if ok else \
        "TP View panel did not navigate/render as expected."
    result(case, actual, ok)
    assert ok, actual
