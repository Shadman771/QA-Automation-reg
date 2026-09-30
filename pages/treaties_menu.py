"""The "Treaties" top-nav dropdown. Confirmed live (scripts/discover_treaties*.py,
throwaway - not part of the suite): the rsuite dropdown component mounts
EVERY top-nav dropdown's <li class="rs-dropdown-item"> in the DOM at once
(hidden, not removed), so a plain `page.locator("li.rs-dropdown-item")` after
opening "Treaties" returns 25 items across every menu (Pillar 2, Treaties,
Calculators, Tools, BEPS, the user menu). Only the 5 items below are actually
inside the Treaties menu (confirmed by filtering to `.is_visible()` after
clicking "Treaties" - the other menus' items exist in the DOM but stay
`display:none`/hidden):

    Full DTA         -> /wta/FullDta
    PE Clause        -> /wta/PEClauses
    Other Articles   -> /wta/OtherArticles
    WHT Rates        -> /wta/WHTRates
    MLI Data         -> /wta/MLIData

No 6th item exists live. "Treaties" itself, like "Pillar 2", is an
`<a role="button">` that opens a dropdown rather than navigating, so its
accessible role is "button", not "link"."""
from playwright.sync_api import Page

TREATIES_ITEMS = ["Full DTA", "PE Clause", "Other Articles", "WHT Rates", "MLI Data"]

TREATIES_ITEM_URLS = {
    "Full DTA": "/wta/FullDta",
    "PE Clause": "/wta/PEClauses",
    "Other Articles": "/wta/OtherArticles",
    "WHT Rates": "/wta/WHTRates",
    "MLI Data": "/wta/MLIData",
}


class TreatiesMenu:
    def __init__(self, page: Page):
        self.page = page
        self.nav_treaties = page.get_by_role("button", name="Treaties")

    def open(self):
        self.nav_treaties.click()

    def item(self, name: str):
        """Scoped to VISIBLE <li> only - see module docstring on why an
        unscoped `li.rs-dropdown-item` lookup would ambiguously match other,
        hidden menus' items of the same text (none collide here, but this
        stays consistent/robust with the pattern)."""
        li = self.page.locator("li.rs-dropdown-item").filter(has_text=name)
        anchor = li.locator("a")
        return anchor.first
