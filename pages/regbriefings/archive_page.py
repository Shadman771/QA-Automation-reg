"""RegBriefings > Archive (/regbrief/pastBriefingYearly).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). A year selector (2011-2026, confirmed
live via `<span>` text elements, same no-`href` gotcha as the main
sidebar) sits alongside the main sidebar. Selecting a year with real
archived data shows 3 sections (World Tax Brief / Transfer Pricing
Brief / Tax Treaty Brief), each listing up to 12 monthly cards (JAN-DEC)
- confirmed live each card is a real `<section class="cursor-pointer">`
that, when clicked, navigates to
`/regbrief/pastBriefingDetails?type=<WtaBriefing|TpaBriefing|
TreatyBriefing>&month=<FullMonthName>&year=<YYYY>` (confirmed live for
"DEC" 2025 -> `type=WtaBriefing&month=December&year=2025`).

**Real, live-confirmed default/empty state**: on initial load (before
selecting any year), all 3 sections show "No data found" - this is
real, expected behavior (the default view doesn't auto-select a year),
not a bug - don't treat it as a failure when testing the page's
unmodified initial state."""
from playwright.sync_api import Page


class ArchivePage:
    def __init__(self, page: Page):
        self.page = page
        self.world_tax_brief_heading = page.get_by_text("World Tax Brief", exact=True).first
        self.transfer_pricing_brief_heading = page.get_by_text("Transfer Pricing Brief", exact=True).first
        self.tax_treaty_brief_heading = page.get_by_text("Tax Treaty Brief", exact=True).first
        self.no_data_found = page.get_by_text("No data found", exact=True)
        self.monthly_cards = page.locator("section.cursor-pointer")

    def year_item(self, year: str):
        return self.page.get_by_text(year, exact=True).first

    def monthly_card(self, month_abbr: str, brief_type_label: str):
        """`month_abbr` e.g. "DEC"; `brief_type_label` e.g. "World tax
        brief" (confirmed live: lowercase 'tax'/'pricing'/'treaty' in the
        card's own <h6>, unlike the section heading above it)."""
        return self.page.locator("section.cursor-pointer").filter(
            has_text=month_abbr
        ).filter(has_text=brief_type_label).first
