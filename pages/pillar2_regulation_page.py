"""Pillar 2 > Regulation (/wta/PillarTwoRegulation). Confirmed live: a left
"Jurisdictions" panel plus a plain "Search" text box (filters the rendered
regulations, distinct from "Search countries"); selecting a jurisdiction
alone renders a "Showing regulations of <Country>" table with columns
Title / Description / Entry into Force / Download / Project and per-row
"Add to Project" buttons.

The "Download" column's "English" link is a `<span class="reg-link-button
reg-link-button--inline">` (same pattern as top-level Forms/Regulations and
Treaties > Other Articles) - clicking it triggers a genuine file
download."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel


class PillarTwoRegulationPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.search_regulations = page.get_by_placeholder("Search", exact=True)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.showing_text = page.get_by_text("Showing regulations of", exact=False)
        self.table = page.locator("table")
        self.col_entry_into_force = page.get_by_role("columnheader", name="Entry into Force")
        self.add_to_project_buttons = page.get_by_role("button", name="Add to Project")
        self.download_links = page.get_by_text("English", exact=True)

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/PillarTwoRegulation", wait_until="networkidle")
