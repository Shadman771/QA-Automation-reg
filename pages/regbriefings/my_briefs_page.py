"""RegBriefings > My Briefs (/regbrief/home/myBriefings) - the
RegBriefings landing/dashboard view.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). Aggregates the LATEST section from all
3 brief types on one page (confirmed live: "World Tax Brief:", "Transfer
Pricing Brief:", "Tax Treaty Brief:" headings each appear exactly once,
each with their own country-by-country news cards and a "Print" button),
plus a right-hand "Quick Access" panel (a "Recent Briefs" list with a
"See All" link, and a "News related to your interest" carousel).

Each individual news item within a brief section ends with a "Full Story
in Regfollower" link (confirmed live: 66 such links present across the
3 aggregated sections on a typical load) - these are real outbound
links, not placeholders."""
from playwright.sync_api import Page


class MyBriefsPage:
    def __init__(self, page: Page):
        self.page = page
        self.world_tax_brief_heading = page.get_by_text("World Tax Brief:", exact=False).first
        self.transfer_pricing_brief_heading = page.get_by_text("Transfer Pricing Brief:", exact=False).first
        self.tax_treaty_brief_heading = page.get_by_text("Tax Treaty Brief:", exact=False).first
        self.quick_access_heading = page.get_by_role("heading", name="Quick Access")
        self.recent_briefs_heading = page.get_by_text("Recent Briefs", exact=True)
        self.see_all_link = page.get_by_text("See All", exact=True)
        self.news_related_heading = page.get_by_text("News related to your interest", exact=True)
        self.print_buttons = page.get_by_role("button", name="Print")
        self.full_story_links = page.get_by_text("Full Story in Regfollower", exact=True)

    def country_card(self, country: str):
        return self.page.get_by_text(country, exact=True).first
