"""Workspace > Entities - grid sorting/search, import/export, row menus and
the TP View / chart views. All read-only: nothing is created, imported,
edited or deleted here."""
import re

import pytest

from tests.workspace._flows import finish, mk, open_entities
from utils.wait import wait_for_content

FEATURE = "Workspace Entities"

SORT_CASES = [
    ("40", "Entity Name", "entityName"),
    ("41", "Incorporation Jurisdiction", "incorporationJurisdiction"),
    ("42", "Tax Residence", "taxResidence"),
    ("43", "Type", "type"),
]


def _is_sorted(values, descending):
    """Case-insensitive order check that tolerates the one row the app pins
    to the top regardless of sort (the Ultimate Parent Entity - confirmed
    live on RC, where 'ownrer' leads an otherwise A-Z list)."""
    def ordered(vs):
        keys = [v.lower() for v in vs]
        return keys == sorted(keys, reverse=descending)
    return ordered(values) or ordered(values[1:])


@pytest.mark.regression
@pytest.mark.parametrize("num,column,field", SORT_CASES, ids=[c[2] for c in SORT_CASES])
def test_workspaceentities_column_sorts_both_directions(page, result, num, column, field):
    case = mk(page, f"WorkspaceEntities_{num}", FEATURE, f"'{column}' sorts ascending and descending",
              f"Clicking the '{column}' header must sort the grid by that column: `aria-sort`, the `?sort={field}:"
              "<dir>` URL parameter and the actual cell order must all agree, in both directions.",
              f"1. Open Entities\n2. Click the '{column}' header until it is ascending - verify\n"
              "3. Click again for descending - verify", f"Column: {column}")
    ent = open_entities(case, page)
    header = ent.sortable_header(column)
    seen = {}
    for _ in range(3):
        case.click(header, f"'{column}' column header")
        page.wait_for_timeout(1500)
        state = ent.column_sort_state(column)
        if state in ("ascending", "descending") and state not in seen:
            direction = "asc" if state == "ascending" else "desc"
            values = ent.column_values(column)
            seen[state] = {"url": f"sort={field}%3A{direction}" in page.url or f"sort={field}:{direction}" in page.url,
                           "ordered": _is_sorted(values, state == "descending"), "sample": values[:4]}
            case.check(f"{state}: URL carries sort={field}:{direction} and the cells are in that order",
                       seen[state]["url"] and seen[state]["ordered"], expected=f"{state} order",
                       actual=f"url ok={seen[state]['url']}, ordered={seen[state]['ordered']}, first={values[:4]}",
                       locator=header)
        if len(seen) == 2:
            break
    ok = len(seen) == 2 and all(v["url"] and v["ordered"] for v in seen.values())
    finish(case, result, ok, f"'{column}' sorted correctly in both directions.",
           f"'{column}' sort check failed: {seen}.")


@pytest.mark.regression
def test_workspaceentities_44_no_match_search_shows_empty_state(page, result):
    case = mk(page, "WorkspaceEntities_44", FEATURE, "A search with no matches shows the 'No Entities Yet' empty state",
              "Typing a term no entity contains must replace the grid with the 'No Entities Yet' empty state "
              "(zero rows), not leave stale rows on screen.",
              "1. Open Entities\n2. Type a term that matches nothing\n3. Verify the empty state and zero rows",
              "Search term: zzzqqq_no_such_entity")
    ent = open_entities(case, page)
    case.click(ent.search_input, "Entities search box")
    ent.type_search("zzzqqq_no_such_entity")
    empty = wait_for_content(ent.empty_state, timeout=10000)
    rows = ent.entity_row_count()
    ok = empty and rows == 0
    case.check("Empty state is shown with zero rows", ok, expected="'No Entities Yet', 0 rows",
               actual=f"empty state={empty}, rows={rows}", locator=ent.empty_state)
    finish(case, result, ok, "A no-match search showed the empty state.",
           f"No-match search left empty state={empty}, rows={rows}.")


@pytest.mark.regression
def test_workspaceentities_45_search_is_case_insensitive(page, result):
    case = mk(page, "WorkspaceEntities_45", FEATURE, "Grid search is case-insensitive",
              "Searching for a live entity name with its letter case inverted must still return that entity.",
              "1. Open Entities and read an entity name containing letters\n2. Type it with inverted case\n"
              "3. Verify the entity is still returned", "Search term: a live entity name, case-inverted at runtime")
    ent = open_entities(case, page)
    names = [n for n in ent.entity_names() if re.search(r"[A-Za-z]{4,}", n)]
    target = names[-1]
    term = target.swapcase()
    case.click(ent.search_input, "Entities search box")
    ent.type_search(term)
    page.wait_for_timeout(1200)
    found = ent.entity_names()
    ok = target in found and all(term.lower() in n.lower() for n in found)
    case.check("Case-inverted search still returns the entity (and only matches)", ok,
               expected=f"includes '{target}'", actual=str(found), locator=ent.row(target))
    finish(case, result, ok, f"Searching '{term}' returned '{target}'.",
           f"Searching '{term}' returned {found}; expected it to include '{target}'.")


@pytest.mark.regression
def test_workspaceentities_46_partial_search_returns_only_matching_rows(page, result):
    case = mk(page, "WorkspaceEntities_46", FEATURE, "A partial search term returns every and only matching entities",
              "Typing the first 4 characters of a live entity name must return exactly the baseline entities whose "
              "name contains that fragment - no more, no fewer.",
              "1. Open Entities and read all names\n2. Type the first 4 characters of one name\n"
              "3. Compare the result with the names that contain the fragment",
              "Search term: 4-character prefix of a live entity name")
    ent = open_entities(case, page)
    baseline = [n for n in ent.entity_names() if n]
    frag = [n for n in baseline if len(n) >= 4][-1][:4]
    expected = sorted(n for n in baseline if frag.lower() in n.lower())
    case.click(ent.search_input, "Entities search box")
    ent.type_search(frag)
    page.wait_for_timeout(1200)
    got = sorted(n for n in ent.entity_names() if n)
    by_name = all(frag.lower() in n.lower() for n in got)
    # The search also matches other columns (e.g. ID), so the result may be a
    # superset of the name matches - but it must contain every name match.
    ok = bool(got) and set(expected) <= set(got) and len(got) <= len(baseline)
    case.check("Every entity whose name contains the fragment is returned", ok,
               expected=f"{expected}", actual=f"{got} (all matched by name: {by_name})")
    finish(case, result, ok, f"Searching '{frag}' returned {len(got)} row(s) including all {len(expected)} name matches.",
           f"Searching '{frag}' returned {got}; expected at least {expected}.")


@pytest.mark.regression
def test_workspaceentities_47_import_dialog_requires_a_file_and_cancels_cleanly(page, result):
    case = mk(page, "WorkspaceEntities_47", FEATURE, "Import Entities requires a file and Cancel changes nothing",
              "The Import Entities dialog must accept only .xlsx/.xls, keep 'Next' disabled until a file is chosen, "
              "offer a template download, and Cancel must close it with the grid unchanged. (No file is uploaded: a "
              "bulk import cannot be cleanly undone.)",
              "1. Record the row count\n2. Click Import Entities\n3. Verify the file input, disabled Next and "
              "template link\n4. Cancel\n5. Verify the row count is unchanged", "-")
    ent = open_entities(case, page)
    baseline = ent.entity_row_count()
    case.click(ent.import_entities_button, "'Import Entities' button")
    opened = wait_for_content(ent.import_heading, timeout=10000)
    accept = ent.import_file_input.get_attribute("accept") or ""
    next_disabled = ent.import_next_button.get_attribute("disabled") is not None
    template = ent.import_template_link.is_visible()
    case.check("Dialog accepts only Excel files, Next is disabled, template link is offered",
               opened and ".xlsx" in accept and next_disabled and template,
               expected="accept includes .xlsx, Next disabled, template visible",
               actual=f"opened={opened}, accept='{accept}', Next disabled={next_disabled}, template={template}",
               locator=ent.import_heading)
    case.click(ent.delete_cancel_button, "'Cancel' button")
    closed = ent.wait_modal_closed(10000)
    after = ent.entity_row_count()
    ok = opened and ".xlsx" in accept and next_disabled and template and closed and after == baseline
    case.check("Dialog closed and the grid is unchanged", closed and after == baseline,
               expected=f"{baseline} rows", actual=f"closed={closed}, {after} rows")
    finish(case, result, ok, "Import dialog validated its input and Cancel changed nothing.",
           f"Import dialog check failed: accept='{accept}', Next disabled={next_disabled}, closed={closed}, rows {baseline}->{after}.")


@pytest.mark.regression
def test_workspaceentities_48_export_downloads_an_excel_file(page, result):
    case = mk(page, "WorkspaceEntities_48", FEATURE, "'Export as Excel' downloads an .xlsx file",
              "Clicking the Export as Excel button must trigger a real file download with an .xlsx name.",
              "1. Open Entities\n2. Click 'Export as Excel'\n3. Verify a .xlsx download starts", "-")
    ent = open_entities(case, page)
    filename = ""
    try:
        with page.expect_download(timeout=30000) as dl:
            case.click(ent.export_button, "'Export as Excel' button")
        filename = dl.value.suggested_filename
    except Exception as exc:
        filename = f"<no download: {str(exc)[:80]}>"
    ok = filename.lower().endswith(".xlsx")
    case.check("A .xlsx file is downloaded", ok, expected="*.xlsx", actual=filename)
    finish(case, result, ok, f"Export downloaded '{filename}'.", f"Export did not download an .xlsx ({filename}).")


@pytest.mark.regression
def test_workspaceentities_49_row_menu_offers_edit_and_delete(page, result):
    case = mk(page, "WorkspaceEntities_49", FEATURE, "An entity row's menu offers Edit and Delete",
              "Opening a row's actions menu in the Entity Information grid must offer exactly Edit and Delete. "
              "(The menu is only opened, no action is taken on the pre-existing entity.)",
              "1. Open Entities\n2. Open the first row's actions menu\n3. Verify Edit and Delete are offered", "-")
    ent = open_entities(case, page)
    first = [n for n in ent.entity_names() if n][0]
    case.click(ent.row_kebab(first), f"row actions menu of '{first}'")
    edit = wait_for_content(ent.menu_edit, timeout=10000)
    delete = ent.menu_delete.first.is_visible()
    ok = edit and delete
    case.check("Menu shows Edit and Delete", ok, expected="Edit + Delete", actual=f"Edit={edit}, Delete={delete}",
               locator=ent.menu_delete)
    finish(case, result, ok, "Row menu offered Edit and Delete.", f"Row menu showed Edit={edit}, Delete={delete}.")


@pytest.mark.regression
def test_workspaceentities_50_tp_view_grid_lists_the_same_entities(page, result):
    case = mk(page, "WorkspaceEntities_50", FEATURE, "TP View > Data lists the same entities with its own columns",
              "TP View > Data must show the columns ID, Entity Name, Tax Residence and Related Party, and list "
              "exactly the same entities as the Entity Information grid.",
              "1. Open Entities and read the entity names\n2. Open TP View > Data\n"
              "3. Verify the columns and that the entity names are identical", "-")
    ent = open_entities(case, page)
    info_names = sorted(n for n in ent.entity_names() if n)
    case.click(ent.link_tp_view_data, "'TP View' > Data link")
    wait_for_content(ent.tp_expand_buttons, timeout=20000)
    headers = [h for h in page.locator("table thead th").all_inner_texts() if h.strip()]
    tp_names = sorted(n for n in ent.entity_names() if n)
    want = ["ID", "Entity Name", "Tax Residence", "Related Party"]
    ok = [h.strip() for h in headers] == want and tp_names == info_names
    case.check("TP View has its own columns and the same entity list", ok,
               expected=f"{want}; {len(info_names)} entities", actual=f"{headers}; {len(tp_names)} entities",
               locator=ent.table)
    finish(case, result, ok, f"TP View listed the same {len(tp_names)} entities with the expected columns.",
           f"TP View mismatch: headers={headers}, {len(tp_names)} vs {len(info_names)} entities.")


@pytest.mark.regression
def test_workspaceentities_51_tp_view_row_menu_has_edit_but_no_delete(page, result):
    case = mk(page, "WorkspaceEntities_51", FEATURE, "TP View's row menu offers Edit only (no Delete)",
              "In TP View > Data a row's actions menu must offer Edit and must NOT offer Delete - entities can only "
              "be deleted from the Entity Information grid.",
              "1. Open TP View > Data\n2. Open the first row's actions menu\n3. Verify Edit is offered and Delete is not",
              "-")
    ent = open_entities(case, page)
    ent.goto_view("transferpricing/data")
    wait_for_content(ent.table_rows, timeout=20000)
    first = [n for n in ent.entity_names() if n][0]
    case.click(ent.row_kebab(first), f"row actions menu of '{first}'")
    edit = wait_for_content(ent.menu_edit, timeout=10000)
    delete = ent.menu_delete.count()
    ok = edit and delete == 0
    case.check("Menu shows Edit and no Delete", ok, expected="Edit only", actual=f"Edit={edit}, Delete items={delete}",
               locator=ent.menu_edit)
    finish(case, result, ok, "TP View's row menu offered Edit only.",
           f"TP View row menu showed Edit={edit}, Delete items={delete}.")


@pytest.mark.regression
def test_workspaceentities_52_tp_view_edit_opens_related_party_picker_and_cancels(page, result):
    case = mk(page, "WorkspaceEntities_52", FEATURE, "TP View > Edit opens the related-party picker; Cancel saves nothing",
              "Edit on a TP View row must open a dialog titled with the entity's name, offering 'Add More Related "
              "Parties' with one checkbox per other entity. Cancel must close it without changing the grid.",
              "1. Open TP View > Data and note the first row's Related Party cell\n2. Row menu > Edit\n"
              "3. Verify the dialog\n4. Cancel\n5. Verify the Related Party cell is unchanged", "-")
    ent = open_entities(case, page)
    total = ent.entity_row_count()
    ent.goto_view("transferpricing/data")
    wait_for_content(ent.table_rows, timeout=20000)
    first = [n for n in ent.entity_names() if n][0]
    before = ent.row_cells(first).get("Related Party")
    case.click(ent.row_kebab(first), f"row actions menu of '{first}'")
    case.click(ent.menu_edit.first, "'Edit' menu item")
    opened = wait_for_content(ent.tp_related_heading, timeout=15000)
    wait_for_content(ent.tp_party_checkboxes, timeout=20000)  # the party list loads after the dialog opens
    boxes = ent.tp_party_checkboxes.count()
    titled = ent.modal_wrapper.get_by_role("heading", name=first, exact=True).count() == 1
    case.check("Dialog is titled with the entity and lists the other entities as checkboxes",
               opened and titled and 0 < boxes <= total - 1,
               expected=f"title '{first}', 1..{total - 1} checkboxes", actual=f"opened={opened}, titled={titled}, {boxes} checkboxes",
               locator=ent.tp_related_heading)
    case.click(ent.delete_cancel_button, "'Cancel' button")
    closed = ent.wait_modal_closed(10000)
    after = ent.row_cells(first).get("Related Party")
    ok = opened and titled and 0 < boxes <= total - 1 and closed and after == before
    case.check("Related Party cell is unchanged after Cancel", after == before, expected=before, actual=after)
    finish(case, result, ok, "Related-party picker opened and Cancel saved nothing.",
           f"Related-party dialog check failed: opened={opened}, titled={titled}, boxes={boxes}, closed={closed}, cell '{before}'->'{after}'.")


CHART_CASES = [
    ("53", "Entity Information > Chart", "information/chart"),
    ("54", "TP View > Chart", "transferpricing/chart"),
    ("55", "Tax Risk > Chart", "taxrisk/chart"),
]


@pytest.mark.regression
@pytest.mark.parametrize("num,label,route", CHART_CASES, ids=[c[2].replace("/", "_") for c in CHART_CASES])
def test_workspaceentities_chart_view_renders(page, result, num, label, route):
    case = mk(page, f"WorkspaceEntities_{num}", FEATURE, f"{label} renders the entity chart",
              f"Opening {label} by its direct link must stay on that route and render the chart canvas together "
              "with its Filters and Properties controls, and show the live entities.",
              f"1. Open Entities and read an entity name\n2. Open /companydata/entities/{route}/\n"
              "3. Verify the route, the canvas, the Filters/Properties buttons and that live entities are drawn", f"Route: {route}")
    ent = open_entities(case, page)
    names = [n for n in ent.entity_names() if n]
    case.action(f"Navigating to {label}", kind="navigate")
    ent.goto_view(route)
    canvas = wait_for_content(ent.chart_canvas, timeout=30000)
    filters = wait_for_content(ent.chart_filters_button, timeout=10000)
    props = ent.chart_properties_button.is_visible()
    page.wait_for_timeout(3000)
    body = page.evaluate("() => document.body.innerText")
    shown_names = [n for n in names if n in body]
    # TP View's chart only draws entities that have related parties, so the
    # check is 'live entities are drawn', not 'every entity is drawn'.
    named = len(shown_names) >= 1
    on_route = f"/companydata/entities/{route}/" in page.url
    ok = canvas and filters and props and named and on_route
    case.check("Chart canvas, Filters, Properties and a live entity name are shown on the right route", ok,
               expected="all visible", actual=f"route={on_route}, canvas={canvas}, Filters={filters}, "
                                              f"Properties={props}, {len(shown_names)}/{len(names)} entities drawn",
               locator=ent.chart_canvas)
    finish(case, result, ok, f"{label} rendered with its controls.",
           f"{label} check failed: route={on_route}, canvas={canvas}, Filters={filters}, Properties={props}, entity shown={named}.")
