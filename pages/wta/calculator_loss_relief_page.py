"""Calculators > Loss Relief Calculator (/wta/LossCalculator).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). No reference QA-sheet rows exist for
this module - built entirely from live discovery, same as WHT Router.

Same "Select Mode" (By Jurisdiction / By Entity) radio pair as every
other Calculator sub-page, but a DIFFERENT downstream shape: no
Income Stream/second jurisdiction - just one Source Jurisdiction (or, in
By Entity mode, one Corporate Group -> Source Company), then a Tax Year
select (confirmed live: real date-range options like "01 July 2023 - 30
June 2024", not plain years), then a second "Mode" radio pair specific to
this page - "Ordinary loss relief" (default) / "Capital loss relief" -
each rendering a COMPLETELY DIFFERENT set of input fields. There is NO
"Calculate" button and NO Generate Memo/Get Forms/Add to Project action
row anywhere on this page (confirmed live, unlike every other Calculator
sub-page) - every field recalculates live as you type, client-side, with
no backend call involved in the arithmetic itself.

**"Start over" shows the SAME confirmation dialog as WHT Router**: "Are
you sure to reset all your selections?" (Cancel/Yes) - confirmed live via
a modal-presence check immediately after the click (its text is NOT
visible in a plain `body.inner_text()` snapshot taken without first
waiting for the modal, which can make it look like nothing happened if
you don't check for it explicitly).

Real gotcha confirmed via live radio-index probing: the page's 4
`input[type='radio']` elements are, in DOM order, `[0]` By Jurisdiction
(checked), `[1]` By Entity, `[2]` Ordinary loss relief (checked), `[3]`
Capital loss relief - the two radio GROUPS are NOT interleaved by visual
row position the way a naive top-to-bottom reading might suggest.

**ORDINARY LOSS RELIEF fields** (13 total - 8 user-editable `input[
placeholder="Enter input amount"]`, 5 computed/`disabled`), in on-page
order:
  1. Losses brought forward (editable)
  2. Restriction on losses brought forward (editable)
  3. Brought forward losses available for offset in current period
     (DISABLED/computed = 1 - 2)
  4. Tax losses in current period (editable)
  5. Total Losses available in current year (DISABLED/computed = 3 + 4)
  6. Losses surrendered under group relief/consolidation provisions
     (editable)
  7. Losses carried back (editable)
  8. Restriction on offset of losses in the current year (editable)
  9. Losses available for offset in current year
     (DISABLED/computed = 5 - 6 - 7 - 8)
  10. Losses actually offset in current year (editable)
  11. Losses available for carry forward (DISABLED/computed = 9 - 10)
  12. Restriction on losses carried forward (editable)
  13. Total losses carried forward (DISABLED/computed = 11 - 12)

**REAL, LIVE-CONFIRMED CALCULATION-VALIDATION ANCHOR** (purely
arithmetic, independently reproducible in Python - no API involved):
entering Losses brought forward=1000, Tax losses in current period=500,
Losses actually offset in current year=300 (all other editable fields
left blank/0, Australia/01 July 2023-30 June 2024) live-computed: field 3
(Brought forward losses available)=1,000, field 5 (Total Losses
available)=1,500, field 9 (Losses available for offset)=1,500, field 11
(Losses available for carry forward)=1,200, field 13 (Total losses
carried forward)=1,200 - each exactly matching the formulas above.

**CAPITAL LOSS RELIEF fields** (9 total - 5 editable, 4 disabled/computed),
in on-page order:
  1. Capital losses brought forward (editable)
  2. Restriction on carry forward of capital losses (editable)
  3. Capital loss brought forward available for offset against current
     year gains (DISABLED/computed)
  4. Capital losses in current year (editable)
  5. Capital losses available for offset against gains in the current
     year (DISABLED/computed)
  6. Capital losses in current year (editable - **a real, live-confirmed
     app quirk**: this field has the EXACT SAME visible label text as
     field 4, so a text-based lookup is ambiguous between them; use
     `capital_field(n)`'s 1-based ordinal position instead, not a label
     string, when targeting field 4 or 6 specifically)
  7. Excess capital losses to carry forward (DISABLED/computed)
  8. Restriction on carrying forward capital losses (editable)
  9. Capital losses carried forward (DISABLED/computed)

**BY ENTITY mode** swaps Source Jurisdiction for Corporate Group (plus a
"Create Group or Entity" link) -> Source Company - simpler than WHT
Router's/Repatriation Calculator's By Entity mode since there's no second
company/jurisdiction here (loss relief is computed within one entity, not
between two).

Same no-deep-link quirk as every other Calculator/Tools page: no `goto()`
here, reach it only via `CalculatorMenu.open_item("Loss Relief
Calculator", ...)`."""
from playwright.sync_api import Page

ORDINARY_FIELD_LABELS = [
    "Losses brought forward",
    "Restriction on losses brought forward",
    "Brought forward losses available for offset in current period",
    "Tax losses in current period",
    "Total Losses available in current year",
    "Losses surrendered under group relief/consolidation provisions",
    "Losses carried back",
    "Restriction on offset of losses in the current year",
    "Losses available for offset in current year",
    "Losses actually offset in current year",
    "Losses available for carry forward",
    "Restriction on losses carried forward",
    "Total losses carried forward",
]


class LossReliefPage:
    def __init__(self, page: Page):
        self.page = page
        self.instructions_heading = page.get_by_role("heading", name="How to complete this calculation")
        self.mode_by_jurisdiction = page.get_by_text("By Jurisdiction", exact=True)
        self.mode_by_entity = page.get_by_text("By Entity", exact=True)
        self.start_over_button = page.get_by_role("button", name="Start over")
        self.start_over_confirm_heading = page.get_by_text("Are you sure to reset all your selections?", exact=True)
        self.start_over_confirm_yes = page.get_by_role("button", name="Yes")
        self.start_over_confirm_cancel = page.get_by_role("button", name="Cancel")
        self.ordinary_loss_radio = page.get_by_text("Ordinary loss relief", exact=True)
        self.capital_loss_radio = page.get_by_text("Capital loss relief", exact=True)

    def source_jurisdiction_combobox(self):
        return self.page.get_by_text("Source Jurisdiction", exact=True).locator(
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

    def source_company_combobox(self):
        return self.page.get_by_text("Source Company", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def ordinary_field(self, label: str):
        """`label` must be one of ORDINARY_FIELD_LABELS - every one of
        those labels is unique within Ordinary mode (unlike Capital
        mode's duplicate, see `capital_field`)."""
        return self.page.get_by_text(label, exact=True).locator("xpath=following::input[1]")

    def capital_field(self, n: int):
        """1-based position among Capital mode's 9 visible inputs (both
        editable and disabled, in on-page order - see module docstring's
        numbered list). Positional, not label-based, because fields 4 and
        6 share the exact same visible label text ("Capital losses in
        current year") - a real, live-confirmed app quirk."""
        return self.page.locator("input[class*='reg-input']").nth(n - 1)

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

    def start_over_and_confirm(self):
        self.start_over_button.click()
        self.page.wait_for_timeout(500)
        self.start_over_confirm_yes.click()
        self.page.wait_for_timeout(800)
