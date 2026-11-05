"""TPA > News (/tpa/News). Confirmed live via scratchpad discovery
scripts (not part of the suite): near-identical to WTA's own News module.

Left panel: `JurisdictionPanel` only (no categories) - "Jurisdictions"
heading (plural, no "and Categories"). 3 tabs: "Treaty Related News",
"News Timeline", "Saved Search" (this shared account already has one
real saved search, "dessfff", from prior manual/automation use - same
caution as WTA Tools Projects/News). Selecting a jurisdiction alone (no
category gate, unlike National Rules/International Guidelines) renders
real content immediately: a "News of <Country> between <DateA> and
<DateB>" header - confirmed live this is a REAL, account-local rolling
date window (not a fixed literal date), so tests match the format
pattern rather than asserting exact dates - a real article list, "Save
Searches"/"Start Over" buttons, and an "Add to Project" button per
article.

**Real gotcha confirmed live**: clicking the "News Timeline"/"Saved
Search" tab text did not visibly change the rendered content in this
exploration pass (same article/date-window text stayed on screen) - not
yet confirmed whether this is because "Treaty Related News" was already
the effectively active view for this exact query, or a genuine
no-op/same-data coincidence. Tests here only assert the 3 tabs are
present and clickable, not that each one shows provably DIFFERENT
content, since that distinct-content difference has not been directly
confirmed.

Supports a direct deep link (`/tpa/News`, see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel


class TpaNewsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions.")
        self.tab_treaty_related_news = page.get_by_text("Treaty Related News", exact=True)
        self.tab_news_timeline = page.get_by_text("News Timeline", exact=True)
        self.tab_saved_search = page.get_by_text("Saved Search", exact=True)
        self.save_searches_button = page.get_by_role("button", name="Save Searches")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        # Matches "News of Australia between September 30, 2026 and
        # October 30, 2026" - confirmed live the exact dates are a real,
        # account-local rolling window, so this only pins the FORMAT.
        self.news_of_heading = page.get_by_text("News of", exact=False)

    def goto(self):
        tpa_goto(self.page, "/tpa/News")
