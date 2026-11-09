"""TPA > Tools > Templates (/tpa/Templates). See
pages/tpa/tpa_tools_templates_page.py for the full confirmed-live layout
(sortable table, per-row kebab menu, template-picker modal)."""
import pytest

from pages.tpa.tpa_tools_templates_page import TpaTemplatesPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Tools Templates"


def _login_and_open(case, page):
    perform_login(case, page)
    templates = TpaTemplatesPage(page)
    case.action("Navigating to /tpa/Templates", kind="navigate")
    templates.goto()
    return templates


@pytest.mark.smoke
def test_tpatemplates_01_page_loads_with_table_and_create_button(page, result):
    case = Case(
        page, "TpaTemplates_01", FEATURE, "Templates loads with the document table and 'Create Document' button",
        description="The page must load at /tpa/Templates with the 'Create Document' button visible and at "
                     "least one existing template document row (this shared account has prior saved documents).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Verify URL and 'Create Document' button\n"
              "3. Verify at least one existing document row is visible",
    )
    templates = _login_and_open(case, page)
    case.step(2, "Verify URL and 'Create Document' button")
    url_ok = "/tpa/Templates" in page.url
    create_btn_ok = case.verify_visible(templates.create_document_button, "'Create Document' button")

    case.step(3, "Verify at least one existing document row is visible")
    rows_ok = templates.table_rows.count() > 0
    ok = url_ok and create_btn_ok and rows_ok
    case.check("Templates page loads with 'Create Document' and existing rows", ok,
               expected="url_ok=True, create_btn_ok=True, rows_ok=True",
               actual=f"url_ok={url_ok}, create_btn_ok={create_btn_ok}, rows_ok={rows_ok}, "
                      f"row_count={templates.table_rows.count()}")

    actual = (f"Templates loaded correctly at {page.url} with {templates.table_rows.count()} existing rows."
              if ok else f"Templates did not load as expected (url_ok={url_ok}, create_btn_ok={create_btn_ok}, "
              f"rows_ok={rows_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatemplates_02_table_has_expected_sortable_columns(page, result):
    case = Case(
        page, "TpaTemplates_02", FEATURE, "The table shows the 4 expected columns",
        description="Confirmed live via a full table HTML dump: the columns are Document Title, Type, "
                     "Created, Modified - Document Title/Created/Modified are each sortable (aria-sort), "
                     "Type is not.",
        precondition="User is logged in and on Templates.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Verify all 4 expected column headers are present",
    )
    templates = _login_and_open(case, page)
    case.step(2, "Verify all 4 expected column headers are present")
    expected = ["Document Title", "Type", "Created", "Modified"]
    headers = templates.table.first.locator("th").all_inner_texts()
    missing = [c for c in expected if not any(c in h for h in headers)]
    ok = not missing
    case.check("All 4 expected columns are present in the table header", ok,
               expected=expected, actual=f"headers={headers}, missing={missing}")

    actual = f"Templates table correctly shows all 4 expected columns: {expected}." if ok else \
             f"Templates table was missing expected columns: {missing} (headers={headers})."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpatemplates_03_create_document_opens_template_picker(page, result):
    case = Case(
        page, "TpaTemplates_03", FEATURE, "'Create Document' opens a template-picker modal with the 5 known templates",
        description="Clicking 'Create Document' must open a modal with a search box and 5 real template "
                     "cards: Blank Template, Commissionaire Agreement, Contract Manufacturing Agreement, "
                     "Intercompany services agreement, Local File.",
        precondition="User is logged in and on Templates.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Click 'Create Document'\n"
              "3. Verify the picker modal shows the search box and all 5 template cards",
    )
    templates = _login_and_open(case, page)
    case.step(2, "Click 'Create Document'")
    case.click(templates.create_document_button, "'Create Document' button")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the picker modal shows the search box and all 5 template cards")
    search_ok = case.verify_visible(templates.picker_search, "template search box")
    expected_cards = ["Blank Template", "Commissionaire Agreement", "Contract Manufacturing Agreement",
                       "Intercompany services agreement", "Local File"]
    missing = [c for c in expected_cards if templates.template_card(c).count() == 0]
    cards_ok = not missing
    ok = search_ok and cards_ok
    case.check("The template picker shows the search box and all 5 expected template cards", ok,
               expected=f"search_ok=True, all present: {expected_cards}",
               actual=f"search_ok={search_ok}, missing={missing}")

    actual = (f"'Create Document' correctly opened the picker with search and all 5 template cards." if ok
              else f"The template picker did not match expectations (search_ok={search_ok}, missing={missing}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatemplates_04_selecting_blank_template_opens_its_editor_title_step(page, result):
    case = Case(
        page, "TpaTemplates_04", FEATURE, "Selecting 'Blank Template' and 'Use this Template' opens its Document Title step",
        description="Clicking the 'Blank Template' card, then 'Use this Template', must navigate to "
                     "/tpa/Templates/Editor/Blank_Template, which shows a 'Document Title *' field and "
                     "Cancel/'Create Document' buttons before any document is actually created.",
        precondition="User is logged in and on Templates.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Click 'Create Document'\n"
              "3. Select 'Blank Template' and click 'Use this Template'\n"
              "4. Verify the URL and the 'Document Title' step",
    )
    templates = _login_and_open(case, page)
    case.step(2, "Click 'Create Document'")
    case.click(templates.create_document_button, "'Create Document' button")
    page.wait_for_timeout(1000)

    case.step(3, "Select 'Blank Template' and click 'Use this Template'")
    case.click(templates.template_card("Blank Template"), "'Blank Template' card")
    page.wait_for_timeout(400)
    case.click(templates.use_template_button, "'Use this Template' button")
    page.wait_for_timeout(2000)

    case.step(4, "Verify the URL and the 'Document Title' step")
    url_ok = "/tpa/Templates/Editor/Blank_Template" in page.url
    title_field_ok = page.get_by_text("Document Title", exact=False).count() > 0
    cancel_visible = page.get_by_role("button", name="Cancel").count() > 0
    ok = url_ok and title_field_ok and cancel_visible

    case.check("Selecting Blank Template opened its Document Title step", ok,
               expected="url contains Editor/Blank_Template, 'Document Title' field present, Cancel present",
               actual=f"url={page.url}, title_field_ok={title_field_ok}, cancel_visible={cancel_visible}")

    actual = (f"Selecting 'Blank Template' correctly opened its Document Title step at {page.url}." if ok
              else f"The blank-template flow did not match expectations (url={page.url}, "
              f"title_field_ok={title_field_ok}, cancel_visible={cancel_visible}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatemplates_05_cancelling_the_title_step_creates_no_new_document(page, result):
    case = Case(
        page, "TpaTemplates_05", FEATURE, "Cancelling the Document Title step creates no new document row",
        description="Reaching the Document Title step (via Blank Template) and clicking its own 'Cancel' "
                     "(without filling a title) must leave the Templates table's row count unchanged - "
                     "confirmed live, no document is created on Cancel.",
        precondition="User is logged in and on Templates.",
        test_data="-",
        steps="1. Log in and open Templates, note the row count\n"
              "2. Open 'Create Document', select 'Blank Template', 'Use this Template'\n"
              "3. Click 'Cancel' on the Document Title step\n"
              "4. Verify the row count is unchanged",
    )
    templates = _login_and_open(case, page)
    case.step(1, "Note the current row count")
    before_count = templates.table_rows.count()

    case.step(2, "Open 'Create Document', select 'Blank Template', 'Use this Template'")
    case.click(templates.create_document_button, "'Create Document' button")
    page.wait_for_timeout(800)
    case.click(templates.template_card("Blank Template"), "'Blank Template' card")
    page.wait_for_timeout(400)
    case.click(templates.use_template_button, "'Use this Template' button")
    page.wait_for_timeout(2000)

    case.step(3, "Click 'Cancel' on the Document Title step")
    cancel_btn = page.get_by_role("button", name="Cancel")
    if cancel_btn.count() > 0:
        case.click(cancel_btn.first, "'Cancel' button")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

    case.step(4, "Verify the row count is unchanged")
    templates.goto()
    page.wait_for_timeout(1000)
    after_count = templates.table_rows.count()
    ok = after_count == before_count
    case.check("Cancelling the title step created no new document row", ok,
               expected=before_count, actual=after_count)

    actual = (f"Cancelling correctly created no new document (row count stayed at {before_count})." if ok
              else f"Cancelling appears to have changed the row count (before={before_count}, "
              f"after={after_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatemplates_06_existing_row_kebab_menu_has_expected_actions(page, result):
    case = Case(
        page, "TpaTemplates_06", FEATURE, "An existing row's kebab menu shows the 6 expected actions",
        description="Opening the first existing row's kebab ('more-menu') dropdown must show exactly: "
                     "Preview, Clone Document, Edit Document, Delete Document, Export to Word, Export to PDF.",
        precondition="User is logged in and on Templates, with at least one existing row.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Open the first row's kebab menu\n"
              "3. Verify all 6 expected actions are present",
    )
    templates = _login_and_open(case, page)
    has_existing = templates.table_rows.count() > 0

    case.step(2, "Open the first row's kebab menu")
    menu_items = []
    if has_existing:
        kebab = templates.table_rows.first.locator(".more-menu[role='button'], a[role='button']").first
        case.click(kebab, "first row's kebab menu toggle")
        page.wait_for_timeout(600)
        visible_menu = page.locator("ul[role='menu']:visible li[role='menuitem']")
        menu_items = visible_menu.all_inner_texts()

    case.step(3, "Verify all 6 expected actions are present")
    expected = ["Preview", "Clone Document", "Edit Document", "Delete Document", "Export to Word", "Export to PDF"]
    missing = [a for a in expected if a not in menu_items]
    ok = has_existing and not missing
    case.check("The row's kebab menu shows all 6 expected actions", ok,
               expected=expected, actual=f"menu_items={menu_items}, missing={missing}")

    actual = (f"The row's kebab menu correctly showed all 6 expected actions." if ok else
              f"The row's kebab menu did not match expectations (has_existing={has_existing}, "
              f"menu_items={menu_items}, missing={missing}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpatemplates_07_sorting_by_document_title_toggles_aria_sort(page, result):
    case = Case(
        page, "TpaTemplates_07", FEATURE, "Clicking the 'Document Title' column header toggles its aria-sort state",
        description="The 'Document Title' column header is confirmed live to be sortable - clicking it must "
                     "change its 'aria-sort' attribute from its current state.",
        precondition="User is logged in and on Templates.",
        test_data="-",
        steps="1. Log in and open Templates\n2. Note the 'Document Title' header's current aria-sort\n"
              "3. Click it\n4. Verify aria-sort changed",
    )
    templates = _login_and_open(case, page)
    case.step(2, "Note the current aria-sort state")
    header = templates.col_document_title.first
    before_sort = header.get_attribute("aria-sort")

    case.step(3, "Click the 'Document Title' header")
    case.click(header, "'Document Title' column header")
    page.wait_for_timeout(800)

    case.step(4, "Verify aria-sort changed")
    after_sort = header.get_attribute("aria-sort")
    ok = before_sort != after_sort
    case.check("Clicking the 'Document Title' header changed its aria-sort state", ok,
               expected=f"!= {before_sort}", actual=after_sort)

    actual = (f"Clicking 'Document Title' correctly changed aria-sort from {before_sort!r} to {after_sort!r}."
              if ok else f"aria-sort did not change after clicking 'Document Title' (before={before_sort!r}, "
              f"after={after_sort!r}).")
    result(case, actual, ok)
    assert ok, actual
