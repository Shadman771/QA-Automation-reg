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
No pagination observed.

Links/downloads (confirmed live, Australia - identical pattern to Treaties
> Other Articles, see pages/treaties_other_articles_page.py for the full
write-up): rate cells with an 'F' footnote marker are still clickable
`span.reg-link-button` elements that open an `.rs-modal-wrapper` article
detail modal (title "Treaty between <selected> and <row jurisdiction>",
showing the actual treaty article the rate derives from, e.g. "Article 10"
for a dividend rate - Export: PDF/Word/Print, a "Full DTA" link, OK/X to
close). The table's own "Export as Excel" icon button downloads the whole
table."""
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

        self.export_excel_button = page.locator("button.reg-icon-button").filter(
            has=page.locator("img[alt='Export as Excel']")
        )
        self.article_modal_wrapper = page.locator(".rs-modal-wrapper")
        self.article_modal_title = page.locator(".rs-modal-header h4")
        self.article_modal_export_pdf = page.locator("span.reg-icon-button").filter(has_text="PDF")
        self.article_modal_ok_button = page.get_by_role("button", name="OK")

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/WHTRates", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()

    def row_for(self, jurisdiction_name: str):
        return self.table_rows.filter(has_text=jurisdiction_name)

    def article_link_in_row(self, jurisdiction_name: str, column_index: int = 1):
        row = self.row_for(jurisdiction_name)
        return row.locator("td").nth(column_index).locator("span.reg-link-button")
