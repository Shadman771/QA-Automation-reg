"""Treaties > MLI Data (/wta/MLIData?sort=jurisdiction%3Aasc). Confirmed live
(scripts/discover_treaties*.py, throwaway - not part of the suite): the ONE
Treaties page that is NOT jurisdiction-gated - it has no left "Jurisdictions"
panel at all and no country search box; the table (107 rows, one per
jurisdiction) is server-rendered immediately on load. Columns: ['Jurisdiction',
'Signature', 'Deposit of Instrument of Ratification, Acceptance or Approval',
'Entry into Force', 'Notifications made pursuant to Article 35(7)(b) of the
MLI', 'Notifications made after becoming a Party', 'Arbitration Profile',
'Link to MLI document']. The first 4 column headers carry class
'reg-table-th--sortable' and are genuinely clickable - clicking 'Jurisdiction'
toggles the URL's `sort` query param between `jurisdiction:asc` and
`jurisdiction:desc` and visibly reorders the table (confirmed: asc starts
'Albania', desc starts 'Zambia'). Not every jurisdiction has a 'Link to MLI
document' - it's populated only where the deposit/notification columns are;
several rows (e.g. Albania) have empty trailing cells and no document
link/button in that cell. No pagination observed (all 107 rows render at
once)."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN

MLI_DATA_HEADERS = [
    "Jurisdiction", "Signature",
    "Deposit of Instrument of Ratification, Acceptance or Approval",
    "Entry into Force",
    "Notifications made pursuant to Article 35(7)(b) of the MLI",
    "Notifications made after becoming a Party",
    "Arbitration Profile", "Link to MLI document",
]


class MLIDataPage:
    def __init__(self, page: Page):
        self.page = page
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.jurisdiction_header = page.locator("th").filter(has_text="Jurisdiction")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/MLIData?sort=jurisdiction%3Aasc", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()

    def first_row_text(self) -> str:
        return self.table_rows.first.inner_text()
