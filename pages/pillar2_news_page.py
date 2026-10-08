"""Pillar 2 > News (/wta/PillarTwoNews). Confirmed live: a left
"Jurisdictions and Filters" panel plus "News Timeline" / "Saved Search" tabs
above the jurisdiction list; selecting a jurisdiction alone renders
"Pillar Two news of <Country> between <date range>" with "Save Searches"
and "Start Over" controls. For Australia (current window) the app genuinely
shows "No News Found" - an empty state, not an automation bug. Clicking
"Start Over" does NOT reset immediately - it opens a "Confirm Start Over"
modal ("Start over action will reset all of your selection(s). Do you want
to proceed?") with "No"/"Yes" buttons; only "Yes" performs the reset."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel


class PillarTwoNewsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.news_timeline_tab = page.get_by_text("News Timeline", exact=True)
        self.saved_search_tab = page.get_by_text("Saved Search", exact=True)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions.")
        self.news_of_text = page.get_by_text("Pillar Two news of", exact=False)
        self.save_searches_button = page.get_by_role("button", name="Save Searches")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.no_news_found = page.get_by_text("No News Found", exact=True)
        self.confirm_start_over_heading = page.get_by_text("Confirm Start Over", exact=True)
        self.confirm_yes_button = page.get_by_role("button", name="Yes", exact=True)
        self.confirm_no_button = page.get_by_role("button", name="No", exact=True)

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/PillarTwoNews", wait_until="networkidle")
