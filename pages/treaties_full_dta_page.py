"""Treaties > Full DTA (/wta/FullDta). Confirmed live
(scripts/discover_treaties*.py, throwaway - not part of the suite):

  - Left panel: "Jurisdictions" (region tabs Asia Pacific/Americas/Europe/
    MEA, single-select country list) + a "Models" dropdown button (its own
    menu, not part of the jurisdiction panel) with two items: "OECD" and
    "UN". The jurisdiction search box's placeholder is "Search
    countries/models" here (unlike the plain "Search countries" on the
    other Treaties pages).
  - Heading before any selection: "Select Jurisdiction", placeholder text
    "Use the left panel to choose jurisdiction." (singular - single-select,
    like Compliance Calendar/Pillar 2 Forms, not the multi-select
    Information page).
  - Selecting a country renders a table (no extra "Showing ..." text) with
    columns ['', 'Partner Country', 'Status', 'Signature', 'Entry Into
    Force', 'Effective'] - the first column holds a "View" link per row.
    The URL gains a `?sort=partnerCountryOrTitle:asc` query param.
  - Clicking "Models" opens a small menu; clicking "OECD" (or "UN")
    replaces the table with that Model Convention's own list (columns
    "Model Tax Convention" / "Title" / a "View" link) and the URL's sort
    param changes accordingly - a completely different dataset from the
    per-jurisdiction DTA table.
  - No pagination observed (Australia's DTA list rendered ~53 rows in one
    table)."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel


class FullDtaPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.heading = page.get_by_role("heading", name="Select Jurisdiction")
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.models_button = page.get_by_role("button", name="Models")
        self.model_oecd = page.get_by_text("OECD", exact=True)
        self.model_un = page.get_by_text("UN", exact=True)
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.view_links = page.get_by_text("View", exact=True)

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/FullDta", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()
