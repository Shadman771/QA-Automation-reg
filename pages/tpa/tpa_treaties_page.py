"""TPA > Treaties ("TP Articles", /tpa/Treaties). Confirmed live via
scratchpad discovery scripts (not part of the suite): unlike WTA's own
5-page "Treaties" dropdown (Full DTA / PE Clause / Other Articles / WHT
Rates / MLI Data), TPA's own top-nav "Treaties" item is a SUBMENU (nested
inside an unlabeled "more" overflow icon in the nav, alongside Commentary/
Tools/BEPS - confirmed live via a full nav HTML dump) holding exactly ONE
real sub-page, labelled "TP Articles", routed at /tpa/Treaties. There is
NO WHT Rates/MLI Data/PE Clause/Other Articles/Full DTA equivalent under
TPA - confirmed live the TPA "Treaties" submenu has exactly one child
link. Automation below covers this single real page, not the 5 WTA-shaped
sub-features the business request assumed, per this project's standing
rule against inventing functionality that doesn't exist (see
TPA/TPA_BUSINESS_EXPLORATION.md for the full writeup).

Single-select `JurisdictionPanel`, heading "Select Jurisdiction" (same DOM
shape as every other WTA/TPA jurisdiction-only page). Selecting a country
renders "Showing treaties of <Country>" and a real `<table>` (columns:
Jurisdiction, Competent Authority, Transfer Pricing adjustments,
Corresponding adjustments, Relief from Double Taxation, Exchange of
Information) - one row per partner country with a real treaty, confirmed
live on Staging/Live.

**Real, live-confirmed RC-only application defect**: selecting ANY
jurisdiction on RC (confirmed across Bangladesh/Singapore/India/China/
Australia) shows a blocking "Unable to Complete Action - Failed to load
Treaties. Please try again later." error instead of ever rendering the
table - a genuine backend failure specific to RC's own TP Articles API,
not a test/locator bug (the identical action succeeds immediately on both
Staging and Live). Documented, not hidden: the table-render test is a
real, asserted FAIL on RC until the underlying RC API issue is fixed - the
assertion is intentionally NOT weakened to paper over this.

The "more" overflow menu's "Treaties" submenu toggle did not reliably
reveal its nested "TP Articles" link via a plain `.click()` in discovery
(the nested `<ul>` stayed `hidden`) - likely a hover-driven reveal, not a
click-driven one, unlike every other rsuite dropdown in this project.
Rather than fight that interaction, navigation tests use the confirmed
reliable direct deep link (see `goto()` below, same pattern as every other
TPA page) and only assert that the submenu toggle itself is discoverable
in the DOM, not that clicking through it completes - documented as a real
gotcha, not silently worked around.

Supports a direct deep link (`/tpa/Treaties`, see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel


class TpaTreatiesPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.showing_treaties_text = page.get_by_text("Showing treaties of", exact=False)
        self.col_jurisdiction = page.locator("table thead th").filter(has_text="Jurisdiction")
        self.col_competent_authority = page.locator("table thead th").filter(has_text="Competent Authority")
        self.col_tp_adjustments = page.locator("table thead th").filter(has_text="Transfer Pricing adjustments")
        self.col_corresponding_adjustments = page.locator("table thead th").filter(has_text="Corresponding adjustments")
        self.col_relief = page.locator("table thead th").filter(has_text="Relief from Double Taxation")
        self.col_exchange_of_info = page.locator("table thead th").filter(has_text="Exchange of Information")
        self.results_table = page.locator("table")
        self.error_heading = page.get_by_text("Unable to Complete Action", exact=True)
        self.error_body = page.get_by_text("Failed to load Treaties", exact=False)

    def goto(self):
        tpa_goto(self.page, "/tpa/Treaties")

    def row_count(self) -> int:
        return self.page.locator("table tbody tr").count()
