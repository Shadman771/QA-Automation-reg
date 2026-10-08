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
    table).
  - Each row's "View" is a real `<button class="reg-link-button">` (was
    previously defined as `view_links` but never clicked by any test).
    Confirmed live: clicking it fires a real API call
    (`GetTreatyDtaData/<CC>/<CC>`) and REPLACES the table entirely with the
    full treaty document viewer for that jurisdiction pair - same
    "Contents" sidebar layout as the modal opened from Treaties > Other
    Articles' article links, but rendered inline on the page (not a modal;
    `.rs-modal-wrapper` is NOT used here), titled "<Country> - <Partner>"
    with its own "Export:" button (`<button class="reg-icon-button">`
    containing `<img alt="Export as PDF">`, confirmed to download a real
    `Treaty_<Country> - <Partner>.pdf`) and a "Compare With" control. There
    is no visible "back to table" control - re-selecting the jurisdiction
    (or reloading) is how a test returns to the table view."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
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

        # The full document viewer, opened inline by clicking a row's "View".
        self.viewer_contents_heading = page.get_by_role("heading", name="Contents")
        self.viewer_export_pdf_button = page.locator("button.reg-icon-button").filter(
            has=page.locator("img[alt='Export as PDF']")
        )
        self.viewer_compare_with = page.get_by_text("Compare With", exact=True)

    def view_link_in_row(self, partner_name: str):
        row = self.table_rows.filter(has_text=partner_name)
        return row.locator("button.reg-link-button", has_text="View")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/FullDta", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()
