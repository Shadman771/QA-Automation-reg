"""The "Tools" top-nav dropdown. Confirmed live (scratchpad discovery
scripts, throwaway - not part of the suite; same rsuite dropdown component
described in pages/treaties_menu.py, which mounts EVERY top-nav dropdown's
<li class="rs-dropdown-item"> in the DOM at once, hidden not removed):
Only 2 items are actually inside the Tools menu (confirmed by filtering to
`.is_visible()` after clicking "Tools"):

    Projects              -> /wta/Project
    Questionnaire Creator -> /wta/QuestionnaireCreator

No 3rd item exists live.

Real, live-confirmed application quirk shared by BOTH Tools pages (and
distinct from every Treaties page): a direct full-page `page.goto()` to
either `/wta/Project` or `/wta/QuestionnaireCreator` does NOT land on that
page - the SPA has no server-side route for a hard/deep link to either URL,
so the app silently redirects to `/wta/Information` instead (confirmed:
both URLs redirect the same way). The only way to actually reach either
Tools page is in-app navigation via this dropdown, exactly like a real user
would. `ToolsMenu.open_item()` below is therefore the ONLY supported way
this suite's page objects reach `/wta/Project` or `/wta/QuestionnaireCreator`
- there is no `goto()` on either Tools page object, unlike every Treaties
page. See tests/tools/test_tools_navigation.py for the test that documents
this redirect as a real, asserted application behavior rather than hiding
it behind a workaround.

Same viewport defect as Treaties/Calculators/BEPS (see
tests/treaties/conftest.py's docstring): "Tools" is entirely ABSENT from
the DOM below ~1600px viewport width (confirmed: 0 matches at 1440/1500,
1 match at 1600/1700) - tests/tools/conftest.py applies the same
directory-local 1680x900 viewport override for this reason."""
from playwright.sync_api import Page

TOOLS_ITEMS = ["Projects", "Questionnaire Creator"]

TOOLS_ITEM_URLS = {
    "Projects": "/wta/Project",
    "Questionnaire Creator": "/wta/QuestionnaireCreator",
}


class ToolsMenu:
    def __init__(self, page: Page):
        self.page = page
        # Confirmed live: like "Pillar 2" and "Treaties", "Tools" is an
        # <a role="button"> that opens a dropdown rather than navigating.
        self.nav_tools = page.get_by_role("button", name="Tools")

    def open(self):
        self.nav_tools.click()

    def item(self, name: str):
        """Scoped to VISIBLE <li> only - see module docstring on why an
        unscoped `li.rs-dropdown-item` lookup would ambiguously match other,
        hidden menus' items."""
        li = self.page.locator("li.rs-dropdown-item").filter(has_text=name)
        anchor = li.locator("a")
        return anchor.first

    def open_item(self, name: str):
        """The only supported way to reach a Tools page - see module
        docstring: direct goto() to either Tools URL redirects away."""
        self.open()
        self.page.wait_for_timeout(400)
        self.item(name).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(600)
