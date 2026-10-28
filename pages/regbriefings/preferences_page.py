"""RegBriefings > Preferences (opens as an overlay modal, no dedicated URL).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). Confirmed live: clicking "Preferences"
in the sidebar does NOT navigate to a new URL - it opens an
`.rs-modal-wrapper` overlay on top of whatever RegBriefings page is
currently showing (see `pages/regbriefings/regbriefings_common.py`
docstring). It must be closed (Cancel, to avoid altering the real
account's settings) before any other sidebar item becomes clickable
again.

Two tabs, confirmed live:
  - "Briefs" (default): "Select Product" - 3 checkboxes (World Tax
    Brief / Transfer Pricing Brief / Tax Treaty Brief) controlling which
    brief-type sections appear on My Briefs (see
    `pages/regbriefings/my_briefs_page.py` - this is the real,
    confirmed source of that page's account-specific aggregation).
  - "Jurisdictions": "Select Jurisdiction" - the SAME region-tab +
    country-checklist shape as WTA's `pages/wta/wta_common.py::
    JurisdictionPanel` (Asia Pacific/Americas/Europe/MEA region tabs,
    one country checklist per region).

Both tabs share the same "Reset to Default"/"Cancel"/"Save" action row.
**Real shared-account caution**: this is the SAME real, shared account
used throughout this project (not a disposable test account) - any test
that clicks "Save" after changing a real preference MUST toggle it back
and Save again before the test ends, leaving the account's real
settings unchanged, same self-cleaning discipline as
`pages/wta/tools_projects_page.py`'s test data."""
from playwright.sync_api import Page


class PreferencesPage:
    def __init__(self, page: Page):
        self.page = page
        self.modal = page.locator(".rs-modal-wrapper")
        self.briefs_tab = page.get_by_text("Briefs", exact=True)
        self.jurisdictions_tab = page.get_by_text("Jurisdictions", exact=True)
        self.select_product_heading = page.get_by_text("Select Product", exact=True)
        self.select_jurisdiction_heading = page.get_by_text("Select Jurisdiction", exact=True)
        self.reset_to_default_button = page.get_by_role("button", name="Reset to Default")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.save_button = page.get_by_role("button", name="Save")

    def brief_checkbox(self, label: str):
        """`label` one of "World Tax Brief"/"Transfer Pricing Brief"/
        "Tax Treaty Brief" - the "Briefs" tab's own checkboxes."""
        return self.page.get_by_text(label, exact=True).locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )

    def region_tab(self, name: str):
        return self.page.get_by_role("button", name=name, exact=True)

    def country_checkbox(self, name: str):
        """**Real gotcha confirmed live**: every region's country
        checklist is mounted in the DOM at once (hidden, not removed) -
        same pattern as every top-nav dropdown's `<li class=
        "rs-dropdown-item">` documented elsewhere in this project (e.g.
        `pages/wta/treaties_menu.py`). A country appearing in more than
        one region's list (confirmed live: "Australia" matched 4 times)
        makes an unscoped lookup a strict-mode violation - this picks
        only the currently VISIBLE one."""
        candidates = self.page.get_by_text(name, exact=True).locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )
        for i in range(candidates.count()):
            candidate = candidates.nth(i)
            if candidate.is_visible():
                return candidate
        return candidates.first
