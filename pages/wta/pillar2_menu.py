"""The "Pillar 2" top-nav dropdown. Confirmed live (scripts/discover_wta.py)
it contains exactly 7 items, each an `<li class="rs-dropdown-item">`:

    Information         -> /wta/PillarTwoInformation
    Compliance Calendar -> /wta/ComplianceCalendar
    Forms               -> /wta/PillarTwoForms
    Simulator           -> (no href on the <li>; navigates out of the WTA
                            module entirely to /companydata/P2Simulator/,
                            the Transfer Pricing Analyzer's "Master Entity
                            Chart" workspace - a different product area)
    Country Commentary  -> /wta/CountryCommentary
    Regulation          -> /wta/PillarTwoRegulation
    News                -> /wta/PillarTwoNews
"""
from playwright.sync_api import Page

PILLAR2_ITEMS = [
    "Information", "Compliance Calendar", "Forms", "Simulator",
    "Country Commentary", "Regulation", "News",
]


class Pillar2Menu:
    def __init__(self, page: Page):
        self.page = page
        # Confirmed live: unlike the other top-nav items (real <a> links),
        # "Pillar 2" is an <a role="button" ...> (it opens a dropdown
        # instead of navigating), so its accessible role is "button", not
        # "link" - get_by_role("link", ...) matches zero elements here.
        self.nav_pillar2 = page.get_by_role("button", name="Pillar 2")

    def open(self):
        self.nav_pillar2.click()

    def item(self, name: str):
        """Six of the seven dropdown <li> elements wrap an inner <a> that
        also carries the exact item text (get_by_text(exact=True) scoped
        to the <li> would match both - a Playwright strict-mode
        violation), so this targets the anchor. 'Simulator' is the
        exception: its <li> has NO inner <a> at all (confirmed live via
        scripts/discover_wta.py) - click/verify happens on the <li> text
        itself for that one item."""
        li = self.page.locator("li.rs-dropdown-item").filter(has_text=name)
        anchor = li.locator("a")
        if name == "Simulator":
            return li.get_by_text(name, exact=True)
        return anchor.first
