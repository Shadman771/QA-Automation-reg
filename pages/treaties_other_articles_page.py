"""Treaties > Other Articles (/wta/OtherArticles). Confirmed live
(scripts/discover_treaties*.py, throwaway - not part of the suite): same
layout/behavior as PE Clause - single-select jurisdiction panel, heading
"Select Jurisdiction", placeholder "Use the left panel to choose
jurisdiction.". Selecting a country renders a table with columns
['Jurisdiction', 'Tie Breaker Corporate', 'Capital Gain', 'Other Income',
'Exchange of Information'], 43 rows, URL gains `?sort=jurisdiction:asc`.
No pagination observed."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel

OTHER_ARTICLES_HEADERS = ["Jurisdiction", "Tie Breaker Corporate", "Capital Gain", "Other Income", "Exchange of Information"]


class OtherArticlesPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.heading = page.get_by_role("heading", name="Select Jurisdiction")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/OtherArticles", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()
