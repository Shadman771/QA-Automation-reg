"""Treaties > PE Clause (/wta/PEClauses). Confirmed live
(scripts/discover_treaties*.py, throwaway - not part of the suite):

  - Left panel: single-select "Jurisdictions" (region tabs + "Search
    countries", no "Models" control here). Heading before selection:
    "Select Jurisdiction"; placeholder: "Use the left panel to choose
    jurisdiction."
  - Selecting a country (single-select - it does not gate on any category)
    renders a table with columns ['Jurisdiction', 'Fixed Base',
    'Construction Assembly', 'Dependent Agent', 'Services', 'Exempt PE'] -
    all 43 treaty-partner rows at once (URL gains
    `?sort=jurisdiction:asc`), each Article cell showing the relevant
    treaty article reference (e.g. 'Art. 5(1)') or blank/'None' where not
    applicable. No pagination observed."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel

PE_CLAUSES_HEADERS = ["Jurisdiction", "Fixed Base", "Construction Assembly", "Dependent Agent", "Services", "Exempt PE"]


class PEClausesPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.heading = page.get_by_role("heading", name="Select Jurisdiction")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/PEClauses", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()
