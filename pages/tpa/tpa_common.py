"""Shared top-nav for every Transfer Pricing Analyzer (TPA) sub-page.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). TPA is a top-level product tab (like
Workspace/World Tax Analyzer/RegBriefings - see pages/landing_page.py),
NOT a WTA-style dropdown with a viewport-width defect - confirmed live
every TPA top-nav item is visible/clickable at the project's default
1440x900 viewport, so no directory-local `browser_context_args` override
is needed for any TPA test suite (unlike WTA's Treaties/Calculators/
Tools/BEPS).

Clicking the "Transfer Pricing Analyzer" tab lands on `/tpa/Home`. The top
nav then offers, confirmed live: "Home", "Information" (a dropdown with
"National Rules" and "International Guidelines"), "News", "Forms",
"Regulations", "Case Law", plus "Treaties" and "Commentary" (both
confirmed present but OUT OF SCOPE for this build - see
TPA/TPA_BUSINESS_EXPLORATION.md).

**Unlike WTA's Tools/Calculator sub-pages, every TPA sub-page supports a
direct full-page deep link** (confirmed live for /tpa/NationalRules,
/tpa/Forms, /tpa/Home) - same pattern as WTA's Treaties/RegBriefings, not
Tools/Calculator's menu-only-access restriction - so every TPA page
object below has its own `goto()`.

The "Information" dropdown uses the same rsuite-dropdown gotcha
documented throughout this project (e.g. pages/wta/treaties_menu.py):
every `<li class="rs-dropdown-item">` across every dropdown is mounted in
the DOM at once (hidden, not removed) - filter to `.is_visible()` or
scope tightly by exact visible text rather than an unscoped count/list."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN

TPA_TOP_NAV_ITEMS = ["Home", "News", "Forms", "Regulations", "Case Law"]


class TpaNav:
    def __init__(self, page: Page):
        self.page = page
        self.tab_tpa = page.get_by_role("button", name="Transfer Pricing Analyzer")
        self.nav_home = page.get_by_role("link", name="Home", exact=True)
        self.nav_information = page.get_by_role("button", name="Information", exact=True)
        self.nav_news = page.get_by_role("link", name="News", exact=True)
        self.nav_forms = page.get_by_role("link", name="Forms", exact=True)
        self.nav_regulations = page.get_by_role("link", name="Regulations", exact=True)
        self.nav_case_law = page.get_by_role("link", name="Case Law", exact=True)
        # The unlabeled "more" overflow icon (three-dots SVG, no accessible
        # name) holding Treaties/Commentary/Tools/BEPS submenus - confirmed
        # live via a full nav HTML dump, see pages/tpa/tpa_treaties_page.py's
        # module docstring.
        self.nav_more_menu = page.locator("nav.rs-navbar-default div.custom-nav-menu > a[role='button']")

    def open_tab(self):
        self.tab_tpa.click()
        self.page.wait_for_load_state("domcontentloaded")

    def open_information_item(self, name: str):
        """`name` one of "National Rules"/"International Guidelines" -
        opens the "Information" dropdown and clicks the visible item."""
        self.nav_information.click()
        item = self.page.get_by_text(name, exact=True).first
        item.wait_for(state="visible", timeout=10000)
        item.click()
        self.page.wait_for_load_state("domcontentloaded")

    def open_more_menu(self):
        """Opens the unlabeled "more" overflow menu. Confirmed live this
        reveals visible toggles for "Treaties" (a submenu), "Commentary",
        "Tools" (a submenu), and "BEPS" (a submenu) - only "Treaties" is in
        scope for this project."""
        self.nav_more_menu.click()

    def treaties_submenu_toggle(self):
        """The "Treaties" row inside the "more" menu - a submenu TOGGLE,
        not a direct link (see pages/tpa/tpa_treaties_page.py's module
        docstring for why clicking it to reveal "TP Articles" was not
        reliable in discovery; use TpaTreatiesPage.goto() for real
        navigation)."""
        return self.page.locator("div.rs-dropdown-item-toggle").filter(has_text="Treaties")


def tpa_goto(page: Page, route: str):
    """route e.g. "/tpa/Home" - every TPA page supports a direct deep
    link (confirmed live), unlike WTA's Tools/Calculator sub-pages."""
    page.goto(APP_ORIGIN + route, wait_until="domcontentloaded")
