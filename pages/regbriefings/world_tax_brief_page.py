"""RegBriefings > World Tax Brief (/regbrief/home/wtaBriefings).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). See
pages/regbriefings/brief_detail_common.py for the shared shape this page
reuses - entries here are organized one per COUNTRY (e.g. "Algeria",
"Australia"), each with multiple topical news items (e.g. "Submission of
returns:", "Global Minimum Tax (GMT):", "Rates:")."""
from playwright.sync_api import Page

from pages.regbriefings.brief_detail_common import BriefDetailPage


class WorldTaxBriefPage(BriefDetailPage):
    def __init__(self, page: Page):
        super().__init__(page, "World Tax Brief")
