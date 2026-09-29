"""Treaties > WHT Rates (/wta/WHTRates). Confirmed live
(scripts/discover_treaties*.py, throwaway - not part of the suite): same
single-select jurisdiction layout as PE Clause/Other Articles. Selecting a
country renders a table with columns ['Jurisdiction', 'Div-Sub. hold',
'Div-Portfolio', 'INT(GEN)', 'INT(C.B.)', 'INT(Bank)', 'ROY(Patent)',
'ROY(T.M.)', 'ROY(C.R.)', 'ROY(L.P.)', 'Technical Service'] - 44 rows,
where row 0 is always the literal 'Domestic WHT rates' row (the selected
country's own domestic rates, not a treaty partner), followed by 43
treaty-partner rows. URL gains `?sort=jurisdiction:asc`. Rate cells are
numeric (e.g. '15.00') sometimes suffixed with an 'F' footnote marker.
No pagination observed."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel

WHT_RATES_HEADERS = [
    "Jurisdiction", "Div-Sub. hold", "Div-Portfolio", "INT(GEN)", "INT(C.B.)", "INT(Bank)",
    "ROY(Patent)", "ROY(T.M.)", "ROY(C.R.)", "ROY(L.P.)", "Technical Service",
]


class WHTRatesPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.heading = page.get_by_role("heading", name="Select Jurisdiction")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/WHTRates", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()
