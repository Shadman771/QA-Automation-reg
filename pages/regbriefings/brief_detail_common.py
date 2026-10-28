"""Shared base for the 3 structurally-identical RegBriefings "detail"
pages: World Tax Brief, Transfer Pricing Brief, Tax Treaty Brief.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). Each of the 3 pages shares the exact
same shape: a "`<Type>`: `<Month Year>`" section heading with its own
"Print" button, followed by a list of entries (one per country for
World Tax Brief/Transfer Pricing Brief, one per country PAIR for Tax
Treaty Brief, e.g. "Armenia and Japan"), each entry typically ending in
a "Full Story in Regfollower" link. A "Search" input (placeholder
"Search") is present and genuinely filters the entry list (confirmed
live).

Confirmed live: 2 "Print" buttons exist on each detail page (not just
1) - this is consistent with how `pages/regbriefings/my_briefs_page.py`
already documented multiple Print buttons on the aggregated page;
tests should check ">= 1", not an exact count, since the precise number
isn't a meaningfully-asserted business rule.

**REAL, LIVE-CONFIRMED ENVIRONMENT DIFFERENCE**: the "Full Story in
Regfollower" outbound link is present on RC and Live, but genuinely
ABSENT on Staging (confirmed directly: zero matches via an exhaustive
`<a>` tag dump of the whole page, not a timing/loading issue - polled
for 20s with no change). This is real seeded-data variance between
environments, not a bug - tests must not hardcode its presence as a
universal fact. Each country-entry's name instead has a reliable,
environment-universal CSS class `brief-country-name` (confirmed via a
direct HTML dump: `<p class="brief-country-name ...">`, present on both
RC and Staging regardless of the Full Story link) - use `entries` below
as the environment-agnostic "how many results are showing" proxy for
search/filter tests, not `full_story_links`.

Each concrete subclass (`WorldTaxBriefPage`/`TransferPricingBriefPage`/
`TaxTreatyBriefPage`) just supplies its own `heading_prefix` - kept as
separate files/classes per the project's "separate file per sub-feature"
convention, sharing only this common shape via inheritance, same pattern
as `pages/wta/wta_common.py`'s shared `JurisdictionPanel`."""
from playwright.sync_api import Page


class BriefDetailPage:
    def __init__(self, page: Page, heading_prefix: str):
        self.page = page
        self.heading_prefix = heading_prefix
        self.section_heading = page.get_by_text(f"{heading_prefix}:", exact=False).first
        self.print_buttons = page.get_by_role("button", name="Print")
        self.full_story_links = page.get_by_text("Full Story in Regfollower", exact=True)
        self.entries = page.locator(".brief-country-name")
        self.search_input = page.locator("input[placeholder='Search']")

    def entry_heading(self, name: str):
        """`name` is a country (World Tax Brief/Transfer Pricing Brief)
        or a "`<Country A>` and `<Country B>`" pair (Tax Treaty Brief)."""
        return self.page.get_by_text(name, exact=True).first
