"""Locators come from scripts/discover.py's dump of the real post-login
page - the World Tax Analyzer "Information" workspace at /wta/Information.

Full live re-verification (2026-09-23) for deep dashboard coverage:
  - The 4 product tabs each navigate OUT of WTA to a different product area
    (confirmed live): Workspace -> /companydata/dashboard/, Transfer Pricing
    Analyzer -> /tpa/Home, RegBriefings -> /regbrief/home/myBriefings. The
    active tab/region gets the CSS class "reg-tab-button-square-selected"
    (confirmed toggling live).
  - Region tabs (Asia Pacific/Americas/Europe/MEA) are real <button>
    elements; switching regions swaps the entire country checklist
    (confirmed distinct country lists per region). Asia Pacific is selected
    by default.
  - Two separate search boxes: "Search countries" and "Search categories"
    (exact placeholder text). No-match states use DIFFERENT wording,
    confirmed live: countries -> 'No countries found matching "<term>"',
    categories -> 'No results found.' (no search term echoed).
  - "Check All" is a <label> for a checkbox that belongs to the CATEGORY
    tree (not countries) - unchecked by default; checking it cascades to
    check every top-level category (confirmed "Liability to Tax" becomes
    checked).
  - Depth-1/2/3/4 changes how many category-tree levels render; clicking
    "4" measurably expands the panel's text content versus the default
    view (confirmed: default/1 ~585 chars vs depth 4 ~3519 chars)."""
from playwright.sync_api import Page


class LandingPage:
    def __init__(self, page: Page):
        self.page = page
        self.cookie_accept = page.get_by_role("button", name="Accept")

        self.nav_information = page.get_by_role("link", name="Information")
        self.nav_pillar2 = page.get_by_role("button", name="Pillar 2")
        self.nav_news = page.get_by_role("link", name="News")
        self.nav_forms = page.get_by_role("link", name="Forms")
        self.nav_regulations = page.get_by_role("link", name="Regulations")

        self.tab_workspace = page.get_by_role("button", name="Workspace")
        self.tab_world_tax_analyzer = page.get_by_role("button", name="World Tax Analyzer")
        self.tab_transfer_pricing_analyzer = page.get_by_role("button", name="Transfer Pricing Analyzer")
        self.tab_regbriefings = page.get_by_role("button", name="RegBriefings")

        self.search_button = page.get_by_role("button", name="Search")
        self.jurisdictions_heading = page.get_by_role("heading", name="Jurisdictions and Categories", exact=True)
        self.region_tab = lambda name: page.get_by_role("button", name=name, exact=True)
        self.country_checkbox_label = lambda name: page.get_by_text(name, exact=True)

        self.search_countries = page.locator('input[placeholder="Search countries"]')
        self.search_categories = page.locator('input[placeholder="Search categories"]')
        self.check_all_label = page.locator("label", has_text="Check All")
        self.category_label = lambda name: page.get_by_text(name, exact=True)
        # Individual category <label> elements have NO `for` attribute linking
        # them to their checkbox <input> sibling (confirmed live), so
        # clicking the label text is a no-op for selection - only "Check
        # All"'s own label has working click-to-toggle behavior. To actually
        # check/uncheck one category, target its checkbox input directly.
        self.category_checkbox = lambda name: page.get_by_text(name, exact=True).locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )
        self.depth_button = lambda level: page.locator(f"text=/^{level}$/").first
        self.placeholder_text = page.get_by_text("Select Jurisdictions and Categories", exact=True)

    def accept_cookies_if_present(self, timeout: int = 3000):
        try:
            self.cookie_accept.wait_for(state="visible", timeout=timeout)
            self.cookie_accept.click()
        except Exception:
            pass

    def is_loaded(self) -> bool:
        return "/wta/Information" in self.page.url and self.jurisdictions_heading.is_visible()

    def is_region_active(self, name: str) -> bool:
        cls = self.region_tab(name).get_attribute("class") or ""
        return "reg-tab-button-square-selected" in cls

    def is_category_checked(self, name: str) -> bool:
        return self.page.evaluate(
            """(name) => {
                const label = [...document.querySelectorAll('label')]
                    .find(l => l.textContent.trim() === name);
                if (!label) return null;
                const forId = label.getAttribute('for');
                const input = forId ? document.getElementById(forId)
                    : label.parentElement.querySelector('input[type=checkbox]');
                return input ? input.checked : null;
            }""",
            name,
        )

    def is_country_checked(self, name: str) -> bool:
        return self.page.evaluate(
            """(name) => {
                const label = [...document.querySelectorAll('label,span,div')]
                    .find(el => el.textContent.trim() === name);
                if (!label) return null;
                const row = label.closest('div');
                const box = row ? row.querySelector('input[type="checkbox"]') : null;
                return box ? box.checked : null;
            }""",
            name,
        )
