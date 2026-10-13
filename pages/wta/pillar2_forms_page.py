"""Pillar 2 > Forms (/wta/PillarTwoForms). Confirmed live: a left
"Jurisdictions" panel (no categories); selecting a jurisdiction alone
renders a "Showing forms of <Country>" table with columns Title /
Description / Applies to tax year ending on / Download / Project, an
"English" download link per row, and a per-row "Add to Project" button."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta.wta_common import JurisdictionPanel
from utils.wait import goto_and_wait_ready


class PillarTwoFormsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.showing_text = page.get_by_text("Showing forms of", exact=False)
        self.table = page.locator("table")
        self.col_title = page.get_by_role("columnheader", name="Title")
        self.col_description = page.get_by_role("columnheader", name="Description")
        self.col_download = page.get_by_role("columnheader", name="Download")
        self.col_project = page.get_by_role("columnheader", name="Project")
        self.add_to_project_buttons = page.get_by_role("button", name="Add to Project")
        self.download_links = page.get_by_text("English", exact=True)

    def goto(self):
        goto_and_wait_ready(self.page, f"{APP_ORIGIN}/wta/PillarTwoForms", self.placeholder_text)
