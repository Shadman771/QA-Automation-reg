"""Treaties > Other Articles (/wta/OtherArticles). Confirmed live
(throwaway discovery scripts, not part of the suite): same layout/behavior
as PE Clause - single-select jurisdiction panel, heading "Select
Jurisdiction", placeholder "Use the left panel to choose jurisdiction.".
Selecting a country renders a table with columns ['Jurisdiction', 'Tie
Breaker Corporate', 'Capital Gain', 'Other Income', 'Exchange of
Information'], 43+ rows (row count varies per selected country - e.g. 43 for
Australia, 95 for Canada, 94 for Germany, 98 for India), URL gains
`?sort=jurisdiction:asc`. No pagination observed.

Links/downloads/print (confirmed live across Australia, Canada, Germany -
identical structure each time):
  - Every non-"None" article-reference cell (e.g. "Art. 4(4)") renders as a
    clickable `<span class="reg-link-button reg-link-button--inline">`, NOT
    an `<a>` - there is no href/target to read, only a click handler. A cell
    with no treaty coverage for that article renders as plain
    `<span class="text-14-regular">None</span>` with no click handler at
    all - this is the genuine negative case (confirmed on e.g. Belgium's
    "Other Income" column under Australia).
  - Clicking a link span opens an rsuite modal (`.rs-modal-wrapper` /
    `.rs-modal-content`) titled "Treaty between <selected> and <row
    jurisdiction>", showing the specific article's full text, with:
      - a header "Full DTA" link (`a.reg-link-button` inside
        `.rs-modal-header`, no href/target - client-side only) that swaps
        the modal's content for the full DTA document viewer (a "Contents"
        sidebar listing every article of the treaty, with the article that
        was clicked pre-highlighted in the sidebar).
      - an "Export:" row with three real actions, each a
        `<span class="reg-icon-button">` (not a real `<button>`/`<a>`):
        "PDF" and "Word" both trigger real file downloads (confirmed:
        `<CC>_<CC>_<Article>_Treaty_Article.pdf` / `.doc`, both non-empty,
        `Download.failure()` is None). "Print" opens a NEW browser tab at
        `regpluswta.api.kaz.com.bd/api/Print/Index?fileName=...` - a real
        print-preview page (plain text-ish rendering of the treaty name +
        article text), not the OS print dialog - confirmed safe to open and
        read without ever triggering an actual print.
      - a header X close button and a footer "OK" button, both of which
        close the modal (confirmed: `.rs-modal-wrapper` no longer visible
        after clicking OK).
  - Independently of any row, the table's "Export:" bar (visible once a
    country is selected, before any row is clicked) has one real action: an
    "Export as Excel" icon button (`<button class="reg-icon-button">`
    containing `<img alt="Export as Excel">`) that downloads the whole
    table as `<CC>_OtherArticles.xlsx` (confirmed non-empty,
    `Download.failure()` is None).
"""
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

        # Table-level export (no row/article selected).
        self.export_excel_button = page.locator("button.reg-icon-button").filter(
            has=page.locator("img[alt='Export as Excel']")
        )

        # Article detail modal (opened by clicking a row's article-reference link).
        self.article_modal_wrapper = page.locator(".rs-modal-wrapper")
        self.article_modal_title = page.locator(".rs-modal-header h4")
        self.article_modal_body_text = page.locator(".rs-modal-body")
        self.article_modal_full_dta_link = page.locator(".rs-modal-header a.reg-link-button", has_text="Full DTA")
        self.article_modal_export_pdf = page.locator("span.reg-icon-button").filter(has_text="PDF")
        self.article_modal_export_word = page.locator("span.reg-icon-button").filter(has_text="Word")
        self.article_modal_export_print = page.locator("span.reg-icon-button").filter(has_text="Print")
        self.article_modal_close_x = page.locator(".rs-modal-header button.reg-icon-button")
        self.article_modal_ok_button = page.get_by_role("button", name="OK")

        # Full DTA viewer (swapped in when "Full DTA" is clicked from the article modal).
        self.full_dta_contents_heading = page.get_by_role("heading", name="Contents")
        self.full_dta_contents_list_items = page.locator(".rs-modal-content li")

    def goto(self):
        self.page.goto("https://regplus.kaz.com.bd/wta/OtherArticles", wait_until="networkidle")

    def headers(self):
        return self.table.first.locator("th").all_inner_texts()

    def row_for(self, jurisdiction_name: str):
        """The data row for a partner jurisdiction (e.g. 'Austria') in the
        currently-rendered table."""
        return self.table_rows.filter(has_text=jurisdiction_name)

    def article_link_in_row(self, jurisdiction_name: str, column_index: int = 1):
        """The clickable article-reference link span in the given 1-based
        data column (1=Tie Breaker Corporate .. 4=Exchange of Information)
        of a partner jurisdiction's row. Cells with no linked article
        (rendered as plain 'None' text) are NOT `.reg-link-button` and so
        will not match - callers can check `.count() == 0` to confirm a
        genuine no-link cell."""
        row = self.row_for(jurisdiction_name)
        return row.locator("td").nth(column_index).locator("span.reg-link-button")

    def none_cell_in_row(self, jurisdiction_name: str, column_index: int):
        row = self.row_for(jurisdiction_name)
        return row.locator("td").nth(column_index).get_by_text("None", exact=True)
