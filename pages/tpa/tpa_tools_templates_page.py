"""TPA > Tools > Templates (/tpa/Templates). Confirmed live via scratchpad
discovery scripts (not part of the suite): a document-template workspace,
structurally different from every other TPA Tools sub-page.

The list view shows a sortable `<table>` (columns: Document Title, Type,
Created, Modified - confirmed live via a full `<table>` HTML dump; Document
Title/Created/Modified are each `aria-sort`-enabled, Type is not). Each row's
first cell holds a kebab ("more-menu") `role="button"` dropdown toggle, NOT
per-row Edit/Delete text links like WTA's own Tools Projects - confirmed
live its menu holds exactly 6 items: Preview, Clone Document, Edit Document,
Delete Document, Export to Word, Export to PDF.

"Create Document" opens a `.rs-modal-wrapper` template PICKER (a search box
plus 5 real template cards: Blank Template, Commissionaire Agreement,
Contract Manufacturing Agreement, Intercompany services agreement, Local
File), each with its own "Use this Template" button. Confirmed live:
selecting "Blank Template" then "Use this Template" navigates to
`/tpa/Templates/Editor/Blank_Template`, which immediately shows a second,
smaller step - "Document Title *" plus Cancel/"Create Document" - before
any document is actually created; navigating to that editor route and
clicking its own "Cancel" (rather than filling a title and submitting)
creates no new row, confirmed live by re-checking the Templates table row
count unchanged - used here to safely verify the picker flow without
creating unwanted real documents, since actually completing "Create
Document" opens a full rich-text editor (out of this build's required
depth) that this suite's self-cleaning Delete-Document kebab action can
still clean up when a real document IS created.

Supports a direct deep link (`/tpa/Templates`, confirmed live, same
pattern as every other TPA page - see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from utils.wait import wait_for_content


class TpaTemplatesPage:
    def __init__(self, page: Page):
        self.page = page
        self.create_document_button = page.get_by_role("button", name="Create Document")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.col_document_title = page.locator("table thead th").filter(has_text="Document Title")
        self.col_type = page.locator("table thead th").filter(has_text="Type")
        self.col_created = page.locator("table thead th").filter(has_text="Created")
        self.col_modified = page.locator("table thead th").filter(has_text="Modified")

        # "Create Document" template-picker modal.
        self.picker_modal = page.locator(".rs-modal-wrapper").first
        self.picker_search = self.picker_modal.locator("input[placeholder='Search']")
        self.use_template_button = self.picker_modal.get_by_role("button", name="Use this Template")

    def goto(self):
        """Confirmed live: the document table loads asynchronously after
        the button/heading render, same async-render race already
        documented for National Rules' Commentary buttons/News' Add-to-
        Project buttons. Waiting only for the table CONTAINER (the
        earlier fix) is not enough - the table can render empty before
        its rows populate a beat later, confirmed live via a repeatable
        before=4/after=0 race in a full-suite run - so this waits for an
        actual row before returning control."""
        tpa_goto(self.page, "/tpa/Templates")
        wait_for_content(self.table, timeout=15000)
        wait_for_content(self.table_rows, timeout=10000)

    def template_card(self, name: str):
        return self.picker_modal.get_by_text(name, exact=True)

    def row_by_title(self, title: str):
        """The data row (`<tr>`) whose Document Title cell matches `title`
        exactly - scoped with `.first` since this is a real, shared
        account that can in principle hold same-titled rows, same
        defensive pattern as every other row-lookup helper in this
        project."""
        return self.table_rows.filter(has_text=title).first

    def row_kebab_menu(self, title: str):
        return self.row_by_title(title).locator(".more-menu[role='button'], a[role='button']").first

    def open_row_menu(self, title: str):
        self.row_kebab_menu(title).click()
        return self.page.locator("ul[role='menu']:visible li[role='menuitem']")

    def row_exists(self, title: str) -> bool:
        return self.table_rows.filter(has_text=title).count() > 0
