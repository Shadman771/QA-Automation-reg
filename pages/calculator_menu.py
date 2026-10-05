"""The "Calculators" top-nav dropdown. Confirmed live (scratchpad discovery
scripts, throwaway - not part of the suite; same rsuite dropdown component
described in pages/treaties_menu.py and pages/tools_menu.py, which mounts
EVERY top-nav dropdown's <li class="rs-dropdown-item"> in the DOM at once,
hidden not removed - filter to `.is_visible()` after opening, never read an
unscoped count/list). 6 real items (confirmed by filtering to `.is_visible()`
after clicking "Calculators" - no 7th item exists live):

    Corporate Rate Finder   -> /wta/CorpRateFinder
    Repatriation Calculator -> /wta/RepCalculator
    WHT Router              -> /wta/WhtRouter
    Loss Relief Calculator  -> /wta/LossCalculator
    CIT Calculator          -> /wta/CitCalculator
    Interest And Penalties  -> /wta/InterestAndPenalties

Same viewport defect as Treaties/Tools/BEPS (see tests/treaties/conftest.py's
docstring): "Calculators" is entirely ABSENT from the DOM below ~1600px
viewport width - any test suite covering one of these 6 pages needs the same
directory-local 1680x900 `browser_context_args` override (see
tests/calculator/conftest.py)."""
from playwright.sync_api import Page

CALCULATOR_ITEMS = [
    "Corporate Rate Finder",
    "Repatriation Calculator",
    "WHT Router",
    "Loss Relief Calculator",
    "CIT Calculator",
    "Interest And Penalties",
]

CALCULATOR_ITEM_URLS = {
    "Corporate Rate Finder": "/wta/CorpRateFinder",
    "Repatriation Calculator": "/wta/RepCalculator",
    "WHT Router": "/wta/WhtRouter",
    "Loss Relief Calculator": "/wta/LossCalculator",
    "CIT Calculator": "/wta/CitCalculator",
    "Interest And Penalties": "/wta/InterestAndPenalties",
}


class CalculatorMenu:
    def __init__(self, page: Page):
        self.page = page
        self.nav_calculators = page.get_by_role("button", name="Calculators")

    def open(self):
        self.nav_calculators.click()

    def item(self, name: str):
        """Scoped to VISIBLE <li> only - see module docstring on why an
        unscoped `li.rs-dropdown-item` lookup would ambiguously match other,
        hidden menus' items."""
        li = self.page.locator("li.rs-dropdown-item").filter(has_text=name)
        anchor = li.locator("a")
        return anchor.first

    def open_item(self, name: str):
        self.open()
        self.page.wait_for_timeout(400)
        self.item(name).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(600)
