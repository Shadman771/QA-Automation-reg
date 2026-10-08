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
    applicable. No pagination observed.

    Links/downloads (confirmed live, Australia - identical pattern to
    Treaties > Other Articles, see pages/treaties_other_articles_page.py for
    the full write-up): article-reference cells are clickable
    `span.reg-link-button` elements that open an `.rs-modal-wrapper` article
    detail modal (title "Treaty between <selected> and <row jurisdiction>",
    Export: PDF/Word/Print, a "Full DTA" link, OK/X to close). The table's
    own "Export as Excel" icon button downloads the whole table."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
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

        self.export_excel_button = page.locator("button.reg-icon-button").filter(
            has=page.locator("img[alt='Export as Excel']")
        )
        self.article_modal_wrapper = page.locator(".rs-modal-wrapper")
        self.article_modal_title = page.locator(".rs-modal-header h4")
        self.article_modal_export_pdf = page.locator("span.reg-icon-button").filter(has_text="PDF")
        self.article_modal_ok_button = page.get_by_role("button", name="OK")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/PEClauses", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()

    def row_for(self, jurisdiction_name: str):
        return self.table_rows.filter(has_text=jurisdiction_name)

    def article_link_in_row(self, jurisdiction_name: str, column_index: int = 1):
        row = self.row_for(jurisdiction_name)
        return row.locator("td").nth(column_index).locator("span.reg-link-button")
