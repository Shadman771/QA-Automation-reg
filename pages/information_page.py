"""World Tax Analyzer > Information workspace (/wta/Information) - the main
nav's first item (distinct from the post-login "landing" page object, which
only checks the shell loaded). Confirmed live: a left "Jurisdictions and
Categories" panel (region tabs, country search/checklist, a "Check All"
countries checkbox, a "Search categories" box, a "Depth-" 1/2/3/4 control,
and an expandable category tree e.g. "Liability to Tax" -> "Residence" ->
"Treaty rules for residence" -> ...), and a right panel that shows
"Select Jurisdictions and Categories" until both a jurisdiction and a
category are chosen."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel, CategoryTree


class InformationPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.category = CategoryTree(page)
        self.heading = page.get_by_role("heading", name="Select Jurisdictions and Categories")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions and categories.")
        self.ask_ai = page.get_by_text("Ask AI", exact=True)
        self.depth_button = lambda n: page.get_by_role("button", name=str(n), exact=True)

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/Information", wait_until="networkidle")

    def is_loaded(self) -> bool:
        return "/wta/Information" in self.page.url and self.heading.is_visible()
