"""RegBriefings > Transfer Pricing Brief (/regbrief/home/tpaBriefings).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). See
pages/regbriefings/brief_detail_common.py for the shared shape this page
reuses - entries here are organized one per COUNTRY (e.g. "Australia"),
each with transfer-pricing-specific news items (e.g. "CbC reporting
requirement-Deadlines:", "Application to intra-group services:")."""
from playwright.sync_api import Page

from pages.regbriefings.brief_detail_common import BriefDetailPage


class TransferPricingBriefPage(BriefDetailPage):
    def __init__(self, page: Page):
        super().__init__(page, "Transfer Pricing Brief")
