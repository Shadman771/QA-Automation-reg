"""Top-level News module (/wta/News). Confirmed live: a left "Jurisdictions
and Filters" panel plus "News Timeline"/"Saved Search" tabs and a row of
pre-existing saved-search names (real production data from other users'
sessions, e.g. "MyApp-Build", "test", "test1" - read-only reference here,
never created/deleted by this suite); selecting a jurisdiction alone
renders "News of <Country> between <date range>" with real news articles
(title + date), each with an "Add to Project" button, plus "Save Searches"
and "Start Over" controls."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel


class NewsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.news_timeline_tab = page.get_by_text("News Timeline", exact=True)
        self.saved_search_tab = page.get_by_text("Saved Search", exact=True)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions.")
        self.news_of_text = page.get_by_text("News of", exact=False)
        self.save_searches_button = page.get_by_role("button", name="Save Searches")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.add_to_project_buttons = page.get_by_role("button", name="Add to Project")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/News", wait_until="networkidle")

    def is_loaded(self) -> bool:
        return "/wta/News" in self.page.url
