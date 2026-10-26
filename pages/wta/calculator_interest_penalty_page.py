"""Calculators > Interest And Penalties (/wta/InterestAndPenalties) -
"Interest and Penalty Calculator" per its on-page heading.

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). No reference QA-sheet rows exist for
this module - built entirely from live discovery, same as every other
new Calculator sub-page this project.

Same "Select Mode" (By Jurisdiction / By Entity) radio pair as every
other Calculator sub-page. By Jurisdiction flow: Source Jurisdiction
(select) -> Tax Year (select, real date-range options, same shape as
Loss Relief Calculator/CIT Calculator) -> Type of offences (select,
real-data-dependent - see data-gap note below) -> Tax due (amount) ->
Final tax due date / Overdue tax paid (both rsuite `DatePicker`s) ->
computed Total days overdue / Total penalty amount / Total interest and
penalty.

**REAL, LIVE-CONFIRMED DATA GAP - "Type of offences" is DISABLED showing
"No offenses available" for most jurisdiction/year combinations**
(confirmed for Australia/2023 and Bangladesh/2024 - same spirit as
Corporate Rate Finder's/CIT Calculator's null-`HeadlineRate` gap, but
this module's own `GET https://regplusnest.api.kaz.com.bd/api/
InterestPenalty?countryCode=<CODE>&year=<YEAR>` returns `AllOffense:
null` instead). **Confirmed-good anchor for this module specifically**:
Bangladesh + tax year 2023 (01 July 2023-30 June 2024) has one real
seeded offence - "Late payment", with one penalty "Per day penalty"
(`PenaltyPerDay=100000`, `PenaltyPercentage=10`, footnote "Test" -
evidently seeded test data, same pattern as Corporate Rate Finder's
"This for the testingg.." Bangladesh/2024 anchor). This is a DIFFERENT
Bangladesh tax year than Corporate Rate Finder's/CIT Calculator's own
anchor (2024, not 2023) - don't assume the same year works across
modules just because they're all Bangladesh.

**REAL, LIVE-CONFIRMED APPLICATION CRASH - DO NOT TYPE A LITERAL COMMA
INTO EITHER DATE FIELD**: both "Final tax due date" and "Overdue tax
paid" are rsuite `DatePicker` text inputs with a "MMMM, dd, yyyy"
placeholder that LOOKS like a literal format to type, but typing a
comma-containing string (e.g. `"October, 01, 2026"`) via
`press_sequentially()` crashes the entire React app to a generic "Oops!
Something went wrong - We're unable to load the application." error
screen (confirmed live, reproducible) - a real application defect, not
an automation bug. The placeholder is a FORMAT HINT for the picker's
internal masked-input behavior, not literal text to type. Always use the
calendar GUI instead: click the input to open the picker, then click the
target day's `role="gridcell"` element (see `pick_date()` below) - never
type into these fields directly.

**REAL calendar gridcell shape, confirmed via HTML dump**: each day cell
is `<div role="gridcell" aria-label="DD Mon YYYY" ...>` - the day number
is ALWAYS ZERO-PADDED to 2 digits in `aria-label` (e.g. `"01 Oct 2026"`,
not `"1 Oct 2026"` - confirmed live via direct `aria-label` enumeration,
don't assume unpadded single-digit days work).

**CALCULATION-VALIDATION ANCHOR** (purely arithmetic, independently
reproducible in Python - no further API call needed beyond the
`InterestPenalty` fetch that already supplied `PenaltyPerDay`): Bangladesh
/ 01 July 2023-30 June 2024 / "Late payment" offence / Tax due=1,000 /
Final tax due date=01 Oct 2026 / Overdue tax paid=11 Oct 2026
live-computes: Total days overdue=10 (simple calendar day difference),
Total penalty amount=1,000,000 (= `PenaltyPerDay` 100,000 x 10 days,
confirmed live - the "Per day penalty" PenaltyTypeId "1" semantics),
Total interest and penalty=1,000,000 (equals the penalty amount alone
here since this offence's `InterestList` is empty - no separate interest
component to add), Outstanding tax due=1,000 (equals Tax due since no
advance payment was entered).

Same no-deep-link quirk as every other Calculator/Tools page: no
`goto()` here, reach it only via `CalculatorMenu.open_item("Interest And
Penalties", ...)`."""
from playwright.sync_api import Page

INTEREST_PENALTY_API = "https://regplusnest.api.kaz.com.bd/api/InterestPenalty"


class InterestPenaltyPage:
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
        self.payment_type_one_time = page.get_by_text("One time payment", exact=True)
        self.payment_type_installment = page.get_by_text("Installment", exact=True)

    def source_jurisdiction_combobox(self):
        return self.page.get_by_text("Source Jurisdiction", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def tax_year_combobox(self):
        return self.page.get_by_text("Tax Year", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def offence_type_combobox(self):
        return self.page.get_by_text("Type of offences", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def corporate_group_combobox(self):
        return self.page.get_by_text("Corporate Group", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def tax_due_input(self):
        return self.page.get_by_text("Tax due (amount)", exact=True).locator("xpath=following::input[1]")

    def tax_paid_in_advance_input(self):
        return self.page.get_by_text("Tax paid in advance", exact=False).locator("xpath=following::input[1]")

    def final_tax_due_date_input(self):
        return self.page.get_by_text("Final tax due date", exact=True).locator("xpath=following::input[1]")

    def overdue_tax_paid_input(self):
        return self.page.get_by_text("Overdue tax paid", exact=True).locator("xpath=following::input[1]")

    def field(self, label: str):
        """Generic "value next to label" accessor - `label` must be
        unique on the page."""
        return self.page.get_by_text(label, exact=True).locator("xpath=following::input[1]")

    def pick_date(self, date_input, day: int, month_abbr: str, year: int):
        """Opens `date_input`'s calendar and clicks the target day cell -
        NEVER type into these fields, see module docstring's real
        app-crash warning. `day` is zero-padded automatically to match
        the live-confirmed `aria-label="DD Mon YYYY"` format."""
        date_input.click()
        self.page.wait_for_timeout(500)
        label = f"{day:02d} {month_abbr} {year}"
        self.page.get_by_role("gridcell", name=label, exact=True).click()
        self.page.wait_for_timeout(300)
        ok_button = self.page.get_by_role("button", name="OK")
        if ok_button.count() and ok_button.first.is_visible():
            ok_button.first.click()
        self.page.wait_for_timeout(500)

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
