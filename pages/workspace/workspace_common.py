"""Shared top-nav for the Workspace parent module (Dashboard/Entities/
Calendar/TP Documenter - see pages/landing_page.py's `tab_workspace`).

Confirmed live (scratchpad discovery, not part of the suite): Workspace is
a top-level product tab, not a WTA-style dropdown, and renders correctly at
the project's default 1440x900 viewport - no viewport-defect override
needed (same conclusion as TPA/RegBriefings, unlike WTA's Treaties/
Calculators/Tools/BEPS).

Clicking "Workspace" (or navigating straight to a route below) lands on
`/companydata/dashboard/`. The left sidebar then offers 4 real items,
confirmed via `<a href="...">` with real hrefs (NOT the no-href `<span>`
pattern RegBriefings' sidebar uses): "Dashboard" (`/companydata/dashboard/`),
"Entities" (`/companydata/entities/information/data/`), "Calendar"
(`/companydata/calendar/`), "TP Documenter" (`/companydata/Documenter/`,
confirmed present but OUT OF SCOPE for this build - only Dashboard/
Entities/Calendar were requested).

**Every Workspace sub-page supports a direct full-page deep link**
(confirmed live for all 3 in-scope routes) - same pattern as TPA/
RegBriefings/Treaties, not WTA's Tools/Calculator menu-only restriction -
so every Workspace page object below has its own `goto()`."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN

WORKSPACE_DASHBOARD_URL = APP_ORIGIN + "/companydata/dashboard/"
WORKSPACE_ENTITIES_URL = APP_ORIGIN + "/companydata/entities/information/data/"
WORKSPACE_CALENDAR_URL = APP_ORIGIN + "/companydata/calendar/"


class WorkspaceNav:
    def __init__(self, page: Page):
        self.page = page
        self.tab_workspace = page.get_by_role("button", name="Workspace", exact=True)
        self.nav_dashboard = page.get_by_role("link", name="Dashboard", exact=True)
        self.nav_entities = page.get_by_role("link", name="Entities", exact=True)
        self.nav_calendar = page.get_by_role("link", name="Calendar", exact=True)
        self.nav_tp_documenter = page.get_by_role("link", name="TP Documenter", exact=True)

    def open_tab(self):
        self.tab_workspace.click()
        self.page.wait_for_load_state("domcontentloaded")


def workspace_goto(page: Page, url: str):
    """Every Workspace page supports a direct deep link (confirmed live),
    the same pattern as TPA/RegBriefings."""
    page.goto(url, wait_until="domcontentloaded")
