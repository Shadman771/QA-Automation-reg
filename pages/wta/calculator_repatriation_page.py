"""Calculators > Repatriation Calculator (/wta/RepCalculator).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). Two modes toggled by a radio pair
("Select Mode": By Jurisdiction / By Entity), sharing the same downstream
flow once a source/residence pair is resolved to two countries:

  BY JURISDICTION: Source Jurisdiction (select) -> Residence Jurisdiction
  (select) -> Repatriation Amount (free-text, becomes available once a
  source jurisdiction sets its currency) -> Select Income Stream -> a
  results table with a "What is the % of holding in the company?" select,
  a computed Withholding tax %/Treaty-or-Domestic-Rate cell, the
  Repatriation amount mirrored, a user-EDITABLE Exchange Rate input, and
  two DISABLED, computed cells (Withholding tax amount, Total Tax Due).

  BY ENTITY: Corporate Group (select, lists this account's real entity
  charts, e.g. "Demo Entity Chart") -> Source Company / Residence Company
  (selects, both scoped to the chosen chart's entity list) -> same
  Repatriation Amount/Income Stream/results-table flow as By Jurisdiction,
  with each company's own tax-residence country driving the Relief/Rates
  panels (confirmed live: a "Demo Entity Chart" company pairing can
  legitimately have NO treaty between their underlying countries, which
  surfaces the real warning modal documented below).

All dropdowns here are rsuite `SelectPicker`s (`role="combobox"`, NOT the
custom checkbox-list `JurisdictionPanel` used elsewhere in this project) -
`row_combobox(label)` locates one by the table row containing its visible
label, matching the real `<table><tr><td>Label</td><td><Select/></td></tr>`
markup. Each one's `aria-controls` attribute names its (portalled) listbox
- `open_and_pick()` reads that attribute per-click rather than assuming a
fixed id, since rsuite auto-generates a fresh one (`rs-:rX:`) per page load.

**REAL, LIVE-CONFIRMED CALCULATION-VALIDATION ANCHOR** (used throughout
this module's tests instead of re-deriving an expected value from the UI
itself): Australia (source) -> Singapore (residence) -> Dividends -> 7%
holding ("Your holding type is Portfolio.") resolves to a Treaty Rate of
15.00% - independently cross-checked against
`GET https://regplusnest.api.kaz.com.bd/api/Treaty?hostCountryCode=AU&
partnerCountryCode=SG` (`WtrDomesticRates[].Rate` for "Portfolio
Dividend"). With Repatriation Amount=100,000 and a user-entered Exchange
Rate of 1.2, the computed Withholding tax amount AND Total Tax Due both
resolved to exactly 18,000 = 100,000 x 0.15 x 1.2 - confirming the
Exchange Rate field is a real, user-supplied multiplier (NOT auto-fetched)
and the computed cells are a pure, independently-reproducible function of
(amount, rate%, exchange rate).

**REAL, LIVE-CONFIRMED NEGATIVE BEHAVIORS** (asserted as real application
behavior, not worked around):
  - Selecting the SAME country for both Source and Residence Jurisdiction
    triggers an `.rs-modal-wrapper` reading "Source and Residence
    Jurisdiction must be different." with only a "Cancel" button (no
    "OK"/proceed action - this is a pure blocking validation message).
  - Selecting an entity pair (By Entity mode) whose underlying countries
    have no treaty triggers a DIFFERENT `.rs-modal-wrapper` reading
    "No treaty rate is available between <A> and <B>. Only domestic rate
    will apply." - also Cancel-only, but informational rather than
    blocking (the calculation proceeds using the domestic rate alone).
  - The Repatriation Amount input has real client-side masking (confirmed
    via actual keystrokes, not `.fill()`, since `.fill()` bypasses the
    masking JS entirely): a leading "-" is stripped (negative amounts are
    rejected, not merely clamped), non-digit characters are stripped,
    "0" is cleared back to empty (zero is treated as no value), decimals
    and large values (confirmed up to 1,000,000,000) are accepted with
    thousands-separator formatting.
  - "Generate Memo"/"Add to Project" stay disabled until the FULL chain
    (both jurisdictions + amount + income stream + holding %) is
    complete; "Get Forms" needs only both jurisdictions selected.

Same no-deep-link quirk as every other Calculator/Tools page: no `goto()`
here, reach it only via `CalculatorMenu.open_item("Repatriation
Calculator")`."""
from playwright.sync_api import Page

REPATRIATION_TREATY_API = "https://regplusnest.api.kaz.com.bd/api/Treaty"


class RepatriationCalculatorPage:
    def __init__(self, page: Page):
        self.page = page
        self.instructions_heading = page.get_by_role("heading", name="How to complete this calculation")
        self.mode_by_jurisdiction = page.get_by_text("By Jurisdiction", exact=True)
        self.mode_by_entity = page.get_by_text("By Entity", exact=True)
        self.generate_memo_button = page.get_by_role("button", name="Generate Memo")
        self.get_forms_button = page.get_by_role("button", name="Get Forms")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.start_over_button = page.get_by_role("button", name="Start over")
        self.start_over_confirm_yes = page.get_by_role("button", name="Yes")
        self.start_over_confirm_cancel = page.get_by_role("button", name="Cancel")
        self.message_modal = page.locator(".rs-modal-wrapper")
        self.message_modal_cancel = page.locator(".rs-modal-wrapper").get_by_role("button", name="Cancel")
        self.results_table = page.locator("table").first

    def row_combobox(self, label: str):
        return self.page.locator("tr", has_text=label).locator("[role='combobox']").first

    def amount_input(self):
        return self.page.locator("tr", has_text="Repatriation Amount").locator("input").first

    def income_stream_combobox(self):
        return self.page.locator("tr", has_text="Select Income Stream").locator("[role='combobox']").first

    def holding_percent_combobox(self):
        return self.page.locator("[role='combobox']").filter(has_text="Select holding").first

    def _ensure_open(self, combobox):
        """Opens the combobox only if it isn't already open - callers
        often already opened it themselves (via a logged `case.click()`
        for evidence/highlighting) before calling this, and a second
        unconditional click would toggle it closed again. Checks the
        listbox's actual rendered options rather than the `aria-expanded`
        attribute: confirmed live this attribute can still read "false"
        for a brief moment right after a successful click (a React
        render-commit race, not a real closed state) - trusting it caused
        `open_and_pick` to re-click and silently re-close an already-open
        picker."""
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

    def open_and_pick(self, combobox, text: str, exact: bool = False):
        self._ensure_open(combobox)
        listbox_id = combobox.get_attribute("aria-controls")
        options = self.page.locator(f"[id='{listbox_id}'] [role='option']")
        options.filter(has_text=text).first.click()
        self.page.wait_for_timeout(600)

    def open_listbox_options(self, combobox):
        self._ensure_open(combobox)
        listbox_id = combobox.get_attribute("aria-controls")
        return self.page.locator(f"[id='{listbox_id}'] [role='option']")

    def exchange_rate_input(self):
        return self.page.get_by_text("Exchange Rate", exact=True).locator(
            "xpath=following::input[1]"
        )

    def computed_wht_amount_input(self):
        return self.exchange_rate_input().locator("xpath=ancestor::div[contains(@class,'flex-col')][1]"
                                                    "/following-sibling::div[1]//input")

    def total_tax_due_input(self):
        return self.page.get_by_text("Total Tax Due:", exact=True).locator("xpath=following::input[1]")

    def start_over_and_confirm(self):
        self.start_over_button.click()
        self.page.wait_for_timeout(500)
        self.start_over_confirm_yes.click()
        self.page.wait_for_timeout(800)
