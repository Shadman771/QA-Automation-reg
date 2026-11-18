"""Workspace > Entities - create / read / update / delete lifecycles.

Every test creates its own `WorkspaceQA_<tag>_<timestamp>` entity and
deletes it in a `finally` block; no pre-existing entity is ever edited or
deleted. See pages/workspace/workspace_entities_page.py for the confirmed
live behaviour these assertions encode."""
import pytest

from pages.workspace.workspace_calendar_page import WorkspaceCalendarPage
from pages.workspace.workspace_dashboard_page import WorkspaceDashboardPage
from tests.workspace._flows import (
    ENTITY_COUNTRY, code_for, create_entity, fill_legal_step, finish, go_to_ownership_step, go_to_tax_step, mk,
    open_add_entity, open_entities, open_row_action, uid,
)
from utils.wait import wait_for_content

FEATURE = "Workspace Entities"
PRE = "User is logged in. The test creates its own WorkspaceQA_ entity and deletes it afterwards."


@pytest.mark.smoke
def test_workspaceentities_07_create_entity_appears_in_grid_with_saved_values(page, result):
    name = uid("create")
    case = mk(page, "WorkspaceEntities_07", FEATURE, "Creating an entity adds a grid row with the saved values",
              "Completing the Add Entity wizard (unassigned owner) must add a row whose ID, name, jurisdiction, "
              "tax residence, ownership, type and tax characterization equal what was entered.",
              "1. Open Entities\n2. Run the Add Entity wizard and Save\n3. Verify every cell of the new row",
              f"Name: {name}; Country: {ENTITY_COUNTRY}; Owner: unassigned; TCT: Private Limited Company", PRE)
    ent = open_entities(case, page)
    try:
        case.step(2, "Create the entity through the 3-step wizard")
        created = create_entity(case, ent, name)
        case.check("Wizard closed and the new row is visible", created, expected="row visible", actual=created)
        case.step(3, "Verify the new row's cells")
        cells = ent.row_cells(name)
        expected = {"ID": code_for(name), "Entity Name": name, "Incorporation Jurisdiction": ENTITY_COUNTRY,
                    "Tax Residence": ENTITY_COUNTRY, "Type": "Company",
                    "Tax Characterization": "Private Limited Company"}
        wrong = {k: cells.get(k) for k, v in expected.items() if cells.get(k) != v}
        unassigned = "Unassigned" in cells.get("Ownership", "")
        ok = created and not wrong and unassigned
        case.check("Row cells equal the entered values and Ownership shows 'Unassigned'", ok,
                   expected=str(expected), actual=str(cells), locator=ent.row(name))
        finish(case, result, ok, f"Entity '{name}' was created with the correct values.",
               f"Created row is wrong: mismatches={wrong}, ownership='{cells.get('Ownership')}', created={created}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_08_created_entity_persists_after_reload(page, result):
    name = uid("persist")
    case = mk(page, "WorkspaceEntities_08", FEATURE, "A created entity persists after a page reload",
              "After creating an entity, reloading the Entities page must still list it (server-side persistence).",
              "1. Open Entities\n2. Create an entity\n3. Reload the page\n4. Verify the row is still listed",
              f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        case.step(2, "Create the entity")
        created = create_entity(case, ent, name)
        case.step(3, "Reload the Entities page")
        ent.goto()
        case.step(4, "Verify the row is still listed")
        ok = created and ent.wait_row(name, 20000)
        case.check("Entity is still listed after reload", ok, expected="1 row", actual=ent.row(name).count(),
                   locator=ent.row(name))
        finish(case, result, ok, "The created entity persisted across a reload.",
               "The created entity was not listed after a reload.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_09_create_and_delete_change_row_count_by_exactly_one(page, result):
    name = uid("count")
    case = mk(page, "WorkspaceEntities_09", FEATURE, "Create adds exactly one row; delete removes exactly one",
              "The grid's row count must be baseline+1 after a create and return to the baseline after the delete.",
              "1. Open Entities and record the row count\n2. Create an entity and re-count\n"
              "3. Delete it and re-count", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        case.step(1, "Record the baseline row count")
        baseline = ent.wait_rows_settled()
        case.step(2, "Create an entity and re-count")
        created = create_entity(case, ent, name)
        after_create = ent.wait_rows_settled()
        case.check("Row count is baseline + 1 after create", after_create == baseline + 1,
                   expected=baseline + 1, actual=after_create)
        case.step(3, "Delete it and re-count")
        open_row_action(case, ent, name, "Delete")
        case.click(ent.delete_confirm_button, "'Delete' confirm button")
        ent.wait_modal_closed(15000)
        gone = ent.wait_row_gone(name)
        after_delete = ent.wait_rows_settled()
        ok = created and after_create == baseline + 1 and gone and after_delete == baseline
        case.check("Row count is back to the baseline after delete", after_delete == baseline,
                   expected=baseline, actual=after_delete)
        finish(case, result, ok, f"Row count went {baseline} -> {after_create} -> {after_delete}.",
               f"Row count sequence was {baseline} -> {after_create} -> {after_delete} (gone={gone}).")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.smoke
def test_workspaceentities_10_edit_entity_name_updates_row_and_persists(page, result):
    name = uid("edit")
    new_name = name + "_edited"
    case = mk(page, "WorkspaceEntities_10", FEATURE, "Editing an entity's name updates the row and persists",
              "Renaming an entity via Edit > Save must replace the old name in the grid, keep its ID, and survive a reload.",
              "1. Open Entities and create an entity\n2. Row menu > Edit, change the name, Save\n"
              "3. Verify the row shows the new name and the same ID\n4. Reload and verify again",
              f"Name: {name} -> {new_name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Edit the entity's name")
        open_row_action(case, ent, name, "Edit")
        opened = wait_for_content(ent.modal_edit_heading, timeout=15000) and ent.wait_edit_loaded()
        case.fill(ent.modal_name_input, new_name, "Name field")
        case.click(ent.modal_save_button, "'Save' button")
        closed = ent.wait_modal_closed(20000)
        case.step(3, "Verify the row shows the new name and the same ID")
        shown = ent.wait_row(new_name, 20000)
        cells = ent.row_cells(new_name)
        exact_old = [n for n in ent.entity_names() if n == name]
        case.check("Row shows the new name, the unchanged ID, and the old name is gone",
                   shown and cells.get("ID") == code_for(name) and not exact_old,
                   expected=f"name={new_name}, ID={code_for(name)}, old name absent",
                   actual=f"cells={cells}, old rows={exact_old}", locator=ent.row(new_name))
        case.step(4, "Reload and verify the edit persisted")
        ent.goto()
        persisted = ent.wait_row(new_name, 20000)
        ok = (created and opened and closed and shown and cells.get("ID") == code_for(name)
              and not exact_old and persisted)
        case.check("Edited name is still shown after reload", persisted, expected="visible", actual=persisted)
        finish(case, result, ok, f"Entity renamed to '{new_name}' and the change persisted.",
               f"Edit failed: opened={opened}, closed={closed}, shown={shown}, persisted={persisted}, cells={cells}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_11_edit_wizard_is_prefilled_with_saved_values(page, result):
    name = uid("prefill")
    case = mk(page, "WorkspaceEntities_11", FEATURE, "The Edit Entity wizard is pre-filled with the saved values",
              "Opening Edit for an entity must show its saved ID, name and incorporation jurisdiction, and offer Save "
              "on the first step.",
              "1. Open Entities and create an entity\n2. Row menu > Edit\n3. Verify the pre-filled fields\n"
              "4. Close without saving", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Open Edit from the row menu")
        open_row_action(case, ent, name, "Edit")
        opened = wait_for_content(ent.modal_edit_heading, timeout=15000) and ent.wait_edit_loaded()
        case.step(3, "Verify the pre-filled fields")
        got = {"id": ent.modal_id_input.input_value(), "name": ent.modal_name_input.input_value(),
               "jurisdiction": ent.jurisdiction_combo.inner_text().strip(),
               "save_visible": ent.modal_save_button.is_visible()}
        want = {"id": code_for(name), "name": name, "jurisdiction": ENTITY_COUNTRY, "save_visible": True}
        ok = created and opened and got == want
        case.check("Edit wizard shows the saved ID, name, jurisdiction and a Save button", ok,
                   expected=str(want), actual=str(got), locator=ent.modal_name_input)
        case.step(4, "Close without saving")
        ent.dismiss_any_modal()
        finish(case, result, ok, "Edit wizard was pre-filled with the saved values.",
               f"Edit wizard pre-fill was wrong: {got} (expected {want}).")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_12_edit_tax_characterization_updates_grid(page, result):
    name = uid("tct")
    case = mk(page, "WorkspaceEntities_12", FEATURE, "Changing the tax characterization in Edit updates the grid",
              "Editing an entity and choosing a different Tax Characterization on the Tax step must update the "
              "grid's Tax Characterization column.",
              "1. Create an entity as 'Private Limited Company'\n2. Edit > Next > Next > choose 'Holding Company' > Save\n"
              "3. Verify the Tax Characterization cell", f"Name: {name}; TCT: Private Limited Company -> Holding Company",
              PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name, tct="Private Limited Company")
        case.step(2, "Edit the entity and change the tax characterization on the Tax step")
        open_row_action(case, ent, name, "Edit")
        wait_for_content(ent.modal_edit_heading, timeout=15000)
        ent.wait_edit_loaded()
        case.click(ent.modal_next_button, "'Next' (to Ownership)")
        wait_for_content(ent.step_ownership_heading, timeout=10000)
        case.click(ent.modal_next_button, "'Next' (to Tax)")
        wait_for_content(ent.step_tax_heading, timeout=10000)
        case.click(ent.tax_characterization("Holding Company"), "'Holding Company' tax characterization")
        case.click(ent.modal_save_button, "'Save' button")
        closed = ent.wait_modal_closed(20000)
        case.step(3, "Verify the Tax Characterization cell")
        wait_for_content(ent.row(name).filter(has_text="Holding Company"), timeout=15000)
        tct = ent.row_cells(name).get("Tax Characterization")
        ok = created and closed and tct == "Holding Company"
        case.check("Grid shows the new tax characterization", ok, expected="Holding Company", actual=tct,
                   locator=ent.row(name))
        finish(case, result, ok, "Tax characterization was updated to 'Holding Company'.",
               f"Tax characterization cell was '{tct}' after the edit (closed={closed}).")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_13_delete_dialog_names_entity_and_cancel_keeps_it(page, result):
    name = uid("delcancel")
    case = mk(page, "WorkspaceEntities_13", FEATURE, "Delete asks for confirmation and Cancel keeps the entity",
              "Row menu > Delete must open a 'Delete Entity' dialog naming the entity; Cancel must close it and "
              "leave the row in place.",
              "1. Create an entity\n2. Row menu > Delete\n3. Verify the dialog text\n4. Click Cancel\n"
              "5. Verify the row is still listed", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Open Delete from the row menu")
        open_row_action(case, ent, name, "Delete")
        shown = wait_for_content(ent.delete_dialog_text, timeout=10000)
        text = ent.delete_dialog_text.first.inner_text() if shown else ""
        case.check("Dialog asks to confirm deleting this exact entity", shown and name in text,
                   expected=f"Are you sure you want to delete {name}?", actual=text, locator=ent.delete_dialog_text)
        case.step(4, "Click Cancel")
        case.click(ent.delete_cancel_button, "'Cancel' button")
        closed = ent.wait_modal_closed(10000)
        still = ent.row(name).count() == 1
        ok = created and shown and name in text and closed and still
        case.check("Row is still listed after Cancel", still, expected="1 row", actual=ent.row(name).count())
        finish(case, result, ok, "Delete asked for confirmation and Cancel kept the entity.",
               f"Cancel flow wrong: dialog='{text}', closed={closed}, row still listed={still}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.smoke
def test_workspaceentities_14_delete_entity_removes_it_permanently(page, result):
    name = uid("delete")
    case = mk(page, "WorkspaceEntities_14", FEATURE, "Confirming Delete removes the entity permanently",
              "Row menu > Delete > Delete must remove the row immediately and it must stay gone after a reload.",
              "1. Create an entity\n2. Row menu > Delete > confirm\n3. Verify the row is gone\n"
              "4. Reload and verify it is still gone", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Delete the entity and confirm")
        open_row_action(case, ent, name, "Delete")
        case.click(ent.delete_confirm_button, "'Delete' confirm button")
        ent.wait_modal_closed(15000)
        gone = ent.wait_row_gone(name)
        case.check("Row disappears right after confirming", gone, expected="0 rows", actual=ent.row(name).count())
        case.step(4, "Reload and verify it is still gone")
        ent.goto()
        wait_for_content(ent.table_rows, timeout=20000)
        gone_after = ent.row(name).count() == 0
        ok = created and gone and gone_after
        case.check("Row is still absent after reload", gone_after, expected="0 rows", actual=ent.row(name).count())
        finish(case, result, ok, "The entity was deleted and stayed deleted after a reload.",
               f"Delete failed: created={created}, gone={gone}, gone after reload={gone_after}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_15_create_entity_owned_by_existing_entity(page, result):
    name = uid("owned")
    case = mk(page, "WorkspaceEntities_15", FEATURE, "An entity created with an owner shows that owner at 100%",
              "Choosing an existing entity as the single owner must store it: the new row's Ownership column shows "
              "the owner's name and Ownership % shows 100.",
              "1. Open Entities and read an existing entity name to use as owner\n"
              "2. Create an entity owned by it\n3. Verify the Ownership and Ownership % cells",
              f"Name: {name}; Owner: first pre-existing entity, read at runtime (it is not modified)", PRE)
    ent = open_entities(case, page)
    try:
        owner = [n for n in ent.entity_names() if n and not n.startswith("WorkspaceQA_")][0]
        case.step(2, f"Create an entity owned by '{owner}'")
        created = create_entity(case, ent, name, owner=owner)
        case.step(3, "Verify the Ownership cells")
        cells = ent.row_cells(name)
        ok = created and cells.get("Ownership") == owner and cells.get("Ownership %") == "100"
        case.check("Ownership shows the chosen owner at 100%", ok, expected=f"{owner} / 100",
                   actual=f"{cells.get('Ownership')} / {cells.get('Ownership %')}", locator=ent.row(name))
        finish(case, result, ok, f"Entity was created as 100% owned by '{owner}'.",
               f"Ownership cells were '{cells.get('Ownership')}' / '{cells.get('Ownership %')}' (created={created}).")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_16_special_characters_in_name_are_stored_intact(page, result):
    key = uid("special")
    name = key + " <b>&\"'% ñ中文 #@!"
    case = mk(page, "WorkspaceEntities_16", FEATURE, "Special characters in an entity name are stored intact",
              "A name containing HTML-like markup, quotes, an ampersand, accents and CJK characters must be saved "
              "and displayed exactly as typed (not stripped, escaped twice or rendered as markup).",
              "1. Create an entity with a special-character name\n2. Verify the Entity Name cell is identical",
              f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        stored = ent.row_cells(key).get("Entity Name")
        ok = created and stored == name
        case.check("Stored name equals the typed name character for character", ok, expected=name, actual=stored,
                   locator=ent.row(key))
        finish(case, result, ok, "The special-character name was stored exactly as typed.",
               f"Stored name differed: '{stored}' (created={created}).")
    finally:
        ent.delete_all_matching(key)


@pytest.mark.regression
def test_workspaceentities_17_long_name_is_stored_without_truncation(page, result):
    key = uid("long")
    name = key + "_" + "L" * 220
    case = mk(page, "WorkspaceEntities_17", FEATURE, "A 250+ character entity name is stored without truncation",
              "The Name field has no maxlength (confirmed live); a very long name must be saved and shown in full.",
              "1. Create an entity with a 250+ character name\n2. Verify the stored name's length and value",
              f"Name length: {len(name)}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        stored = ent.row_cells(key).get("Entity Name") or ""
        ok = created and stored == name
        case.check("Stored name has the full length and value", ok, expected=f"{len(name)} chars",
                   actual=f"{len(stored)} chars", locator=ent.row(key))
        finish(case, result, ok, f"The {len(name)}-character name was stored in full.",
               f"Stored name had {len(stored)} characters, expected {len(name)} (created={created}).")
    finally:
        ent.delete_all_matching(key)


@pytest.mark.regression
def test_workspaceentities_18_created_entity_is_found_by_search(page, result):
    name = uid("search")
    case = mk(page, "WorkspaceEntities_18", FEATURE, "A created entity is found by the grid search",
              "Typing the new entity's unique name into the search box must leave exactly that one row.",
              "1. Create an entity\n2. Type its name in the search box\n3. Verify exactly one matching row remains",
              f"Search term: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Type the entity's name into the search box")
        case.click(ent.search_input, "Entities search box")
        ent.type_search(name)
        wait_for_content(ent.row(name), timeout=10000)
        page.wait_for_timeout(800)
        names = ent.entity_names()
        ok = created and names == [name]
        case.check("Search leaves exactly the created entity", ok, expected=[name], actual=names,
                   locator=ent.row(name))
        finish(case, result, ok, "Search returned exactly the created entity.",
               f"Search returned {names} instead of only '{name}'.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_19_business_type_is_saved_to_type_column(page, result):
    name = uid("btype")
    btype = "Branch/Site/Service PE"
    case = mk(page, "WorkspaceEntities_19", FEATURE, "The chosen Business Type is saved to the Type column",
              "Selecting a non-default Business Type in the wizard must be reflected in the new row's Type column.",
              "1. Open Add Entity and fill the Legal step with Business Type 'Branch/Site/Service PE'\n"
              "2. Finish the wizard\n3. Verify the Type cell", f"Name: {name}; Business Type: {btype}", PRE)
    ent = open_entities(case, page)
    try:
        open_add_entity(case, ent)
        fill_legal_step(case, ent, code_for(name), name)
        case.step(1, f"Choose Business Type '{btype}'")
        case.click(ent.business_type_combo, "Business Type picker")
        wait_for_content(ent.options, timeout=10000)
        case.click(ent.option(btype), f"'{btype}' option")
        go_to_ownership_step(case, ent)
        case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
        go_to_tax_step(case, ent)
        case.click(ent.modal_save_button, "'Save' button")
        created = ent.wait_modal_closed(20000) and ent.wait_row(name, 20000)
        got = ent.row_cells(name).get("Type")
        ok = created and got == btype
        case.check("Type column shows the chosen business type", ok, expected=btype, actual=got,
                   locator=ent.row(name))
        finish(case, result, ok, f"Entity was saved with Type '{btype}'.",
               f"Type cell was '{got}' (created={created}).")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_20_created_entity_appears_in_calendar_entity_filter(page, result):
    name = uid("xcal")
    case = mk(page, "WorkspaceEntities_20", FEATURE, "A created entity is offered in the Calendar's entity filter",
              "Cross-module: the Calendar's 'Select Entity(ies)' filter must list a newly created entity, and stop "
              "listing it once the entity is deleted.",
              "1. Create an entity\n2. Open Calendar > Select Entity(ies) and verify it is listed\n"
              "3. Delete the entity\n4. Re-open the Calendar filter and verify it is gone", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Open the Calendar entity filter")
        cal = WorkspaceCalendarPage(page)
        cal.goto()
        case.click(cal.filter_picker.first, "'Select Entity(ies)' picker")
        listed = wait_for_content(cal.picker_option(name), timeout=15000)
        case.check("Calendar entity filter lists the new entity", listed, expected="listed", actual=listed,
                   locator=cal.picker_option(name))
        case.step(3, "Delete the entity")
        deleted = ent.delete_all_matching(name)
        case.step(4, "Re-open the Calendar filter")
        cal.goto()
        case.click(cal.filter_picker.first, "'Select Entity(ies)' picker")
        wait_for_content(cal.picker_popup, timeout=10000)
        page.wait_for_timeout(1000)
        still = cal.picker_option(name).count()
        ok = created and listed and deleted == 1 and still == 0
        case.check("Deleted entity is no longer offered", still == 0, expected=0, actual=still)
        finish(case, result, ok, "The entity appeared in the Calendar filter and disappeared after deletion.",
               f"Cross-module check failed: listed={listed}, deleted={deleted}, still offered={still}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_21_created_entity_appears_on_dashboard_heatmap(page, result):
    name = uid("xdash")
    case = mk(page, "WorkspaceEntities_21", FEATURE, "A created entity appears on the Dashboard Risk Heatmap",
              "Cross-module: the Dashboard's Risk Heatmap must show a node for a newly created entity, and drop it "
              "once the entity is deleted.",
              "1. Create an entity\n2. Open Dashboard and verify its name is on the heatmap\n"
              "3. Delete the entity\n4. Re-open Dashboard and verify it is gone", f"Name: {name}", PRE)
    ent = open_entities(case, page)
    try:
        created = create_entity(case, ent, name)
        case.step(2, "Open the Dashboard")
        dash = WorkspaceDashboardPage(page)
        dash.goto()
        node = page.get_by_text(name, exact=False)
        shown = wait_for_content(node, timeout=30000)
        case.check("Heatmap shows the new entity", shown, expected="visible", actual=shown, locator=node)
        case.step(3, "Delete the entity")
        deleted = ent.delete_all_matching(name)
        case.step(4, "Re-open the Dashboard")
        dash.goto()
        wait_for_content(dash.heatmap_canvas, timeout=20000)
        page.wait_for_timeout(4000)
        still = name in dash.body_text()
        ok = created and shown and deleted == 1 and not still
        case.check("Deleted entity is no longer on the Dashboard", not still, expected="absent", actual=still)
        finish(case, result, ok, "The entity appeared on the heatmap and disappeared after deletion.",
               f"Cross-module check failed: shown={shown}, deleted={deleted}, still on dashboard={still}.")
    finally:
        ent.delete_all_matching(name)
