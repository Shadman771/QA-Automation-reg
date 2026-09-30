"""Top-level Forms module (/wta/Forms). Confirmed live: a left
"Jurisdictions and Categories" panel with a flat category checklist (CIT
Returns, WHT deduction/Treaty form, Administrative, Other Forms, Pillar
Two) plus a "checkAllFormCategories" master checkbox and its own "Search"
box; unlike the main Information page, content here renders from the
jurisdiction alone - "Showing forms of <Country>" - a table with columns
Title / Description / Applies to tax year ending on / Download / Project;
categories narrow (filter) the same table rather than gating it. Confirmed
live: EVERY category checkbox (and the "checkAllFormCategories" master
checkbox) starts CHECKED by default on page load - clicking one toggles it
OFF, not on.

The "Download" column's "English" link is a `<span class="reg-link-button
reg-link-button--inline">`, not an `<a>` (same pattern as Treaties > Other
Articles) - clicking it triggers a genuine PDF file download (confirmed
live, Australia: a `..._English_pdf.pdf` file over 1MB, `Download.failure()`
is None)."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel

FORM_CATEGORIES = ["CIT Returns", "WHT deduction/Treaty form", "Administrative", "Other Forms", "Pillar Two"]


class FormsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.search_forms = page.get_by_placeholder("Search", exact=True)
        self.check_all_categories = page.locator("#checkAllFormCategories")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction and categories.")
        self.showing_text = page.get_by_text("Showing forms of", exact=False)
        self.table = page.locator("table")
        self.add_to_project_buttons = page.get_by_role("button", name="Add to Project")
        self.download_links = page.get_by_text("English", exact=True)

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/Forms", wait_until="networkidle")

    def category_checkbox(self, label: str):
        return self.page.locator(
            f"xpath=//label[normalize-space(text())='{label}']/preceding-sibling::input[@type='checkbox'][1]"
        )
