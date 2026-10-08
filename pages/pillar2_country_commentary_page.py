"""Pillar 2 > Country Commentary (/wta/CountryCommentary). Confirmed live:
a left "Jurisdictions" panel (no categories); selecting a jurisdiction alone
renders "Commentary on <Country>, last updated <date>" plus an "Export:"
control and lettered/sectioned rich-text commentary (e.g. "A. Legislative
Framework").

The "Export:" control is a real `<button aria-label="Export commentary as
PDF">` (confirmed live, Australia) - clicking it triggers a genuine file
download (confirmed: `<CC>_<Country>_Commentary.pdf`, non-empty,
`Download.failure()` is None), not just a visible label as previously
tested."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel


class CountryCommentaryPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.commentary_on_text = page.get_by_text("Commentary on", exact=False)
        self.export_label = page.get_by_text("Export:", exact=False)
        self.legislative_framework_heading = page.get_by_text("A. Legislative Framework", exact=False)
        self.export_pdf_button = page.get_by_role("button", name="Export commentary as PDF")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/CountryCommentary", wait_until="networkidle")
