"""TPA > Commentary (/tpa/Commentary). Confirmed live via scratchpad
discovery scripts (not part of the suite): a single-select `JurisdictionPanel`
(same DOM shape as every other WTA/TPA jurisdiction-only page - the heading
"Select Jurisdiction" and placeholder "Use the left panel to choose
jurisdiction." are confirmed byte-identical), reused unmodified.

Selecting a country (confirmed with Bangladesh) renders:
  - a "Commentary on <Country>" heading - confirmed live the country name
    is a SEPARATE sibling text node from the matched "Commentary on"
    element (same sibling-text-node split already documented for TPA
    Regulations' "Showing regulations of <Country>" heading, see
    pages/tpa/tpa_regulations_page.py) - reading the matched element's own
    `inner_text()` returns just "Commentary on" with the country name
    missing; `heading_text()` below reads the parent container instead.
  - a "last updated <date>" line
  - a `<button>` reading "<N> news since the update", confirmed live to
    render ASYNCHRONOUSLY a beat after the "Commentary on <Country>"
    heading - same async-render race already documented elsewhere in this
    project (National Rules' Commentary buttons, News' Add-to-Project
    buttons) - callers should wait for this button directly rather than
    assuming it exists as soon as the heading does. Clicking it opens an
    `.rs-modal-wrapper` titled "Related News" listing recent article
    summaries, closed via its own "OK" button (NOT the Escape key -
    confirmed live: pressing Escape does NOT close this modal, and the
    modal's own `.rs-modal-wrapper` backdrop then intercepts every
    subsequent click on the page, including a jurisdiction-panel country
    click, which times out silently rather than failing with a clear
    error. Tests must close this modal via its "OK" button, never Escape.)
  - an "Export" control
  - a long commentary article body (multiple lettered sections, A./B./C.../N.)
    which can itself embed a `<table>` whose header row happens to read
    identically to the Treaties page's own table columns (Jurisdiction /
    Competent Authority / Transfer Pricing adjustments / Corresponding
    adjustments / Relief from Double Taxation / Exchange of Information) -
    this is real ARTICLE CONTENT reproduced verbatim from the business
    source, not a separate UI feature table, and not guaranteed present for
    every country - tests must not assert on it as a feature of this page.

Supports a direct deep link (`/tpa/Commentary`, see
pages/tpa/tpa_common.py) - confirmed live, same pattern as every other TPA
page (unlike WTA's own Tools/Calculator sub-pages)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel


class TpaCommentaryPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.commentary_heading = page.get_by_text("Commentary on", exact=False)
        self.last_updated_text = page.get_by_text("last updated", exact=False)
        self.news_since_button = page.get_by_role("button", name="news since the update")
        self.export_control = page.get_by_text("Export", exact=False)
        self.news_modal = page.locator(".rs-modal-wrapper").first
        self.news_modal_heading = self.news_modal.get_by_text("Related News", exact=True)
        self.news_modal_ok_button = self.news_modal.get_by_role("button", name="OK")

    def goto(self):
        tpa_goto(self.page, "/tpa/Commentary")

    def heading_text(self) -> str:
        """The "Commentary on <Country>" heading's PARENT container text -
        see module docstring on why the matched element's own inner_text()
        omits the country name (a separate sibling text node)."""
        return self.commentary_heading.first.locator("xpath=..").inner_text()

    def article_body_text(self) -> str:
        return self.page.locator("body").inner_text()

    def close_news_modal(self):
        """Confirmed live: Escape does NOT close this modal - always use
        its own 'OK' button (see module docstring)."""
        self.news_modal_ok_button.click()
