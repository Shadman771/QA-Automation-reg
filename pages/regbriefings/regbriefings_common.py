"""Shared left-sidebar navigation for every RegBriefings sub-page.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). RegBriefings is a top-level product tab
(like Workspace/World Tax Analyzer/Transfer Pricing Analyzer - see
pages/landing_page.py), NOT a top-nav dropdown like WTA's Treaties/
Calculators/Tools/BEPS - confirmed live it has NO viewport-width defect
(visible at the project's default 1440x900, unlike those four dropdowns),
so no directory-local `browser_context_args` override is needed for any
RegBriefings test suite.

Clicking the "RegBriefings" tab lands on `/regbrief/home/myBriefings`
("My Briefs" - the landing/dashboard view). The left sidebar then offers
6 items, confirmed live: "My Briefs", "World Tax Brief", "Transfer
Pricing Brief", "Tax Treaty Brief", "Archive", "Preferences".

**Real gotcha confirmed live**: these ARE wrapped in an `<a>` tag, but
that anchor has no `href` attribute, so it gets no implicit ARIA "link"
role - `get_by_role("link", ...)` never matches and times out silently.
**A second, compounding gotcha**: `get_by_text(name, exact=True)` alone
is AMBIGUOUS (strict-mode violation, confirmed live: 3 matches for "Tax
Treaty Brief" - the sidebar's own `<a>`-wrapped span plus 2 `<h6>`
section headings elsewhere on the aggregated My Briefs page) - the
sidebar's own element is reliably the FIRST match in DOM order, so
`nav_item()` below scopes with `.first`. Don't drop that `.first` even
though a single sub-page (e.g. World Tax Brief itself) might only have
1-2 matches - My Briefs specifically needs it.

**Unlike WTA's Tools/Calculator sub-pages, every RegBriefings sub-page
supports a direct full-page deep link** (confirmed live for all 4 real
routes: `/regbrief/home/wtaBriefings`, `/regbrief/home/tpaBriefings`,
`/regbrief/home/taxTreaties`, `/regbrief/pastBriefingYearly`) - `goto()`
straight to any of them works, same pattern as Treaties, not Tools/
Calculator's menu-only-access restriction. "Preferences" is the one
exception: clicking it does NOT navigate to a new URL - it opens an
overlay panel on top of whatever page is currently showing (confirmed
live: the URL stayed at `/regbrief/pastBriefingYearly` after clicking
"Preferences" from the Archive page) - see
`pages/regbriefings/preferences_page.py` for the real interaction
pattern this implies."""
from playwright.sync_api import Page

REGBRIEFINGS_NAV_ITEMS = [
    "My Briefs",
    "World Tax Brief",
    "Transfer Pricing Brief",
    "Tax Treaty Brief",
    "Archive",
    "Preferences",
]


class RegBriefingsNav:
    def __init__(self, page: Page):
        self.page = page
        self.tab_regbriefings = page.get_by_role("button", name="RegBriefings")
        self.nav_my_briefs = page.get_by_text("My Briefs", exact=True).first
        self.nav_world_tax_brief = page.get_by_text("World Tax Brief", exact=True).first
        self.nav_transfer_pricing_brief = page.get_by_text("Transfer Pricing Brief", exact=True).first
        self.nav_tax_treaty_brief = page.get_by_text("Tax Treaty Brief", exact=True).first
        self.nav_archive = page.get_by_text("Archive", exact=True).first
        self.nav_preferences = page.get_by_text("Preferences", exact=True).first
        self.search_input = page.locator("input[placeholder='Search']")

    def nav_item(self, name: str):
        return self.page.get_by_text(name, exact=True).first

    def open_tab(self):
        self.tab_regbriefings.click()
        self.page.wait_for_load_state("domcontentloaded")
