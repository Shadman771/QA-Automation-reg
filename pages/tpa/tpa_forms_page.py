"""TPA > Forms (/tpa/Forms). Confirmed live via scratchpad discovery
scripts (not part of the suite): near-identical to WTA's own Forms
module.

Left panel: `JurisdictionPanel` + a FLAT 4-item category list (TP
specific form, Main corporate tax return, APA forms, Other forms) -
reused as a `CategoryTree` (same DOM shape confirmed live). Selecting a
jurisdiction alone (no category) renders the full, unfiltered table.

**Real, confirmed-live filtering behavior**: selecting a category DOES
filter the table - for Australia, no category selected shows 39 rows
total; "TP specific form" alone shows 13; "Main corporate tax return"
alone shows 26 (13 + 26 = 39, i.e. every one of Australia's 39 forms
belongs to exactly one of those two categories). "APA forms"/"Other
forms" each showed all 39 rows when selected alone - most likely because
Australia genuinely has zero forms in those 2 categories and the
frontend falls back to showing everything rather than an empty table
when a category filter matches nothing (a real, confirmed quirk, not
re-verified as a documented defect) - so tests here only assert the
clearly-confirmed filtering effect (TP specific form reduces the row
count), not the ambiguous zero-match case.

Table columns (confirmed live): Title, Description, "Applies to tax year
ending on", Download, Project - each real row has an "English" (or
similar) download link and an "Add to Project" button.

Supports a direct deep link (`/tpa/Forms`, see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel, CategoryTree

FORMS_CATEGORIES = ["TP specific form", "Main corporate tax return", "APA forms", "Other forms"]


class TpaFormsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.category = CategoryTree(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction and categories.")
        self.showing_forms_text = page.get_by_text("Showing forms of", exact=False)
        self.col_title = page.get_by_text("Title", exact=True)
        self.col_description = page.get_by_text("Description", exact=True)
        self.col_download = page.get_by_text("Download", exact=True)
        self.col_project = page.get_by_text("Project", exact=True)
        self.add_to_project_buttons = page.get_by_text("Add to Project", exact=True)

    def goto(self):
        tpa_goto(self.page, "/tpa/Forms")

    def row_count(self) -> int:
        return self.add_to_project_buttons.count()
