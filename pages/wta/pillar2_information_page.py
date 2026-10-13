"""Pillar 2 > Information (/wta/PillarTwoInformation). Confirmed live: a
left "Jurisdictions and Categories" panel (jurisdiction list + a FLAT list
of 9 GMT categories: Scope of GMT, Income Inclusion Rule (IIR), Undertaxed
Profits Rule (UTPR), Qualified Domestic Minimum Top-up Tax (QDMTT), Safe
Harbours under GloBE Rule, Filing obligations of GMT, Penalties under GMT,
Payment obligations of GMT, Qualified Refundable Tax Credits under GMT).
Selecting a jurisdiction AND a category renders a "Showing information of
<Country>" content header - the same "select both" gating as the main
Information page, but without a nested tree (flat categories only)."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta.wta_common import JurisdictionPanel, CategoryTree
from utils.wait import goto_and_wait_ready

GMT_CATEGORIES = [
    "Scope of GMT", "Income Inclusion Rule (IIR)", "Undertaxed Profits Rule (UTPR)",
    "Qualified Domestic Minimum Top-up Tax (QDMTT)", "Safe Harbours under GloBE Rule",
    "Filing obligations of GMT", "Penalties under GMT", "Payment obligations of GMT",
    "Qualified Refundable Tax Credits under GMT",
]


class PillarTwoInformationPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.category = CategoryTree(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions and categories.")
        self.showing_heading = lambda country: page.get_by_text(f"Showing information of", exact=False)

    def goto(self):
        goto_and_wait_ready(self.page, f"{APP_ORIGIN}/wta/PillarTwoInformation", self.placeholder_text)
