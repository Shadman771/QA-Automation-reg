"""RegBriefings > Tax Treaty Brief (/regbrief/home/taxTreaties).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). See
pages/regbriefings/brief_detail_common.py for the shared shape this page
reuses - **unlike World Tax Brief/Transfer Pricing Brief, entries here
are organized one per COUNTRY PAIR** (e.g. "Armenia and Japan"), not a
single country - but the DOM shape is otherwise identical (confirmed
live: entries still use the same `.brief-country-name` class, so
`BriefDetailPage.entries`/`entry_heading()` work unmodified)."""
from playwright.sync_api import Page

from pages.regbriefings.brief_detail_common import BriefDetailPage


class TaxTreatyBriefPage(BriefDetailPage):
    def __init__(self, page: Page):
        super().__init__(page, "Tax Treaty Brief")
