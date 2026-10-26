"""Calculators > CIT Calculator (/wta/CitCalculator) - "Corporate Income
Tax Calculator" per its on-page heading.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). No reference QA-sheet rows exist for
this module - built entirely from live discovery, same as WHT Router and
Loss Relief Calculator.

Same "Select Mode" (By Jurisdiction / By Entity) radio pair as every
other Calculator sub-page. By Jurisdiction flow: Domestic Jurisdiction
(select) -> Tax Year (select, real date-range options like "01 July 2024
- 30 June 2025", same shape as Loss Relief Calculator) -> Taxable Income
(free-text amount). By Entity mode swaps Domestic Jurisdiction for
Corporate Group -> "Entity in Residence states" (confirmed live: this
module's own naming for its company field, NOT "Source Company" like
WHT Router/Loss Relief Calculator's By Entity mode - don't assume the
same label across modules).

**REAL, LIVE-CONFIRMED GOTCHA - fields only recompute on BLUR, not on
every keystroke**: typing into "Taxable Income" alone does NOT update
the downstream computed fields (Taxable domestic income, Taxable amount,
Headline Amount, Total CIT, Total tax due, Nominal ETR) - confirmed live
these all stayed empty immediately after `press_sequentially()`. Only
after the field loses focus (e.g. `.press("Tab")` or clicking elsewhere)
does the whole chain recompute. Always blur the amount field before
asserting on any computed value.

**REAL, LIVE-CONFIRMED DATA-GAP BLOCKING MODAL**: selecting a Tax Year
for a jurisdiction/year with a `null` HeadlineRate (the SAME documented
data gap as `calculator_rate_finder_page.py` - most country/year
combinations) immediately shows an `.rs-modal-wrapper` reading "No data
found for this jurisdiction. You may try for another jurisdiction."
(Cancel-only) - confirmed live for Australia/01 July 2023-30 June 2024.
This module reuses `calculator_rate_finder_page.py::CORPORATE_RATE_API`
(`GET https://regplusnest.api.kaz.com.bd/api/CorporateRate?country=
<CODE>&year=<YEAR>`, confirmed via network capture - note the query
param is `country`, not `countryCodes` like Corporate Rate Finder's own
call) for its headline rate, so it hits the exact same data gap and uses
the SAME confirmed-good anchor: **Bangladesh + tax year 2024
(HeadlineRate=55.00)**.

**CALCULATION-VALIDATION ANCHOR**: Bangladesh / 01 July 2024-30 June
2025 / Taxable Income=100,000 (no exemptions/foreign income/special
rates entered) live-computes (after blur): Taxable domestic income=
100,000, Taxable amount=100,000, Headline Amount=100,000, Total CIT=
55,000, Total tax due=55,000.00, Nominal ETR=55 - exactly
100,000 x 0.55 (the live `CorporateRate` API's HeadlineRate for BD/2024),
independently re-fetchable via `CORPORATE_RATE_API` rather than compared
to the UI itself.

**Action buttons**: Generate Memo/Get Forms/Add to Project are PRESENT
but DISABLED from the start (confirmed live) - same pattern as
Repatriation Calculator, NOT the "absent until a result exists" pattern
WHT Router uses. They become enabled once the calculation chain
completes.

**"Start over"** shows the same "Are you sure to reset all your
selections?" (Cancel/Yes) confirmation dialog as WHT Router/Loss Relief
Calculator.

Same no-deep-link quirk as every other Calculator/Tools page: no
`goto()` here, reach it only via `CalculatorMenu.open_item("CIT
Calculator", ...)`."""
from playwright.sync_api import Page

from pages.wta.calculator_rate_finder_page import CORPORATE_RATE_API  # noqa: F401 - re-exported for tests


class CitCalculatorPage:
    def __init__(self, page: Page):
        self.page = page
        self.instructions_heading = page.get_by_role("heading", name="How to complete this calculation")
        self.mode_by_jurisdiction = page.get_by_text("By Jurisdiction", exact=True)
        self.mode_by_entity = page.get_by_text("By Entity", exact=True)
        self.generate_memo_button = page.get_by_role("button", name="Generate Memo")
        self.get_forms_button = page.get_by_role("button", name="Get Forms")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.start_over_button = page.get_by_role("button", name="Start over")
        self.start_over_confirm_heading = page.get_by_text("Are you sure to reset all your selections?", exact=True)
        self.start_over_confirm_yes = page.get_by_role("button", name="Yes")
        self.start_over_confirm_cancel = page.get_by_role("button", name="Cancel")
        self.message_modal = page.locator(".rs-modal-wrapper")
        self.message_modal_cancel = self.message_modal.get_by_role("button", name="Cancel")
        self.no_surtax_message = page.get_by_text("No surtax applicable", exact=False)

    def domestic_jurisdiction_combobox(self):
        return self.page.get_by_text("Domestic Jurisdiction", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def tax_year_combobox(self):
        return self.page.get_by_text("Tax Year", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def corporate_group_combobox(self):
        return self.page.get_by_text("Corporate Group", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def entity_combobox(self):
        """Confirmed live: this module's By Entity company field is
        labeled "Entity in Residence states" - NOT "Source Company" like
        WHT Router/Loss Relief Calculator's By Entity mode."""
        return self.page.get_by_text("Entity in Residence states", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def taxable_income_input(self):
        return self.page.get_by_text("Taxable Income", exact=True).first.locator("xpath=following::input[1]")

    def field(self, label: str):
        """Generic "value next to label" accessor for every other
        field - `label` must be unique on the page (unlike Loss Relief
        Calculator's Capital mode, no duplicate labels were found here)."""
        return self.page.get_by_text(label, exact=True).first.locator("xpath=following::input[1]")

    def total_tax_due_input(self):
        return self.page.get_by_text("Total tax due", exact=True).locator("xpath=following::input[1]")

    def nominal_etr_input(self):
        return self.page.get_by_text("Nominal ETR", exact=True).locator("xpath=following::input[1]")

    def _ensure_open(self, combobox):
        """Copied from `calculator_repatriation_page.py::_ensure_open()` -
        same already-confirmed-live rsuite `SelectPicker` gotcha."""
        listbox_id = combobox.get_attribute("aria-controls")
        already_open = bool(listbox_id) and self.page.locator(
            f"[id='{listbox_id}'] [role='option']"
        ).first.is_visible()
        if not already_open:
            combobox.click()
            self.page.wait_for_timeout(500)
            listbox_id = combobox.get_attribute("aria-controls")
            try:
                self.page.locator(f"[id='{listbox_id}'] [role='option']").first.wait_for(
                    state="visible", timeout=5000
                )
            except Exception:
                pass

    def open_and_pick(self, combobox, text: str):
        self._ensure_open(combobox)
        listbox_id = combobox.get_attribute("aria-controls")
        options = self.page.locator(f"[id='{listbox_id}'] [role='option']")
        options.filter(has_text=text).first.click()
        self.page.wait_for_timeout(700)

    def open_listbox_options(self, combobox):
        self._ensure_open(combobox)
        listbox_id = combobox.get_attribute("aria-controls")
        return self.page.locator(f"[id='{listbox_id}'] [role='option']")

    def enter_taxable_income(self, amount: str):
        """Fills Taxable Income AND blurs it - see module docstring: the
        computed fields only recalculate on blur, not on every
        keystroke."""
        field = self.taxable_income_input()
        field.click()
        field.press_sequentially(amount, delay=15)
        field.press("Tab")
        self.page.wait_for_timeout(1000)

    def start_over_and_confirm(self):
        self.start_over_button.click()
        self.page.wait_for_timeout(500)
        self.start_over_confirm_yes.click()
        self.page.wait_for_timeout(800)
