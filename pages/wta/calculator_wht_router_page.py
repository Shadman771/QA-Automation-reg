"""Calculators > WHT Router (/wta/WhtRouter).

Manually verified against the live application (scratchpad discovery
scripts, not part of the suite). Two modes toggled by a radio pair
("Select Mode": By Jurisdiction / By Entity), sharing the same downstream
flow once a source/residence pair is resolved to two countries - same
shape as `calculator_repatriation_page.py`:

  BY JURISDICTION: Source Jurisdiction (select) -> Income Stream (select,
  enabled once a source is picked) -> Residence Jurisdiction (select) ->
  click "Calculate" to render a results table.

  BY ENTITY: Corporate Group (select, lists this account's real entity
  charts, plus a "Create Group or Entity" link) -> Source Company ->
  Income Stream -> Residence Company -> same results flow.

  "Intermediaries 1"/"Intermediaries 2" (both optional) each open an
  "Intermediate Streams and Jurisdictions" modal with two independent
  multi-select checklists - Streams (with "Select All"/"Select None"
  links) and Countries (scrollable) - confirmed via `intermediaries_modal`
  below; closed with "Done". These represent an indirect payment route
  through intermediary jurisdictions for the "Optimized Result Table".

All dropdowns here are rsuite `SelectPicker`s (`role="combobox"`), same
"aria-controls names the portalled listbox, aria-expanded is NOT a
reliable is-it-open signal" gotcha as `calculator_repatriation_page.py` -
`_ensure_open()`/`open_and_pick()` below are copied from that same,
already-confirmed-live pattern rather than re-derived.

**REAL, LIVE-CONFIRMED API + CALCULATION-VALIDATION ANCHOR**: selecting
the 3rd required field (whichever is last between Source/Income
Stream/Residence) fires `POST https://regplusnest.api.kaz.com.bd/api/WhtRouter`
automatically - confirmed via network capture, this is NOT gated behind
the "Calculate" button click (clicking "Calculate" afterward just
re-renders/confirms the already-fetched result). Request body shape:
`{"HostCountry": "AU", "TargetCountry": "SG", "Stream": "Portfolio
Dividend", "BaseIncome": 100, "IntermediateCountryStreams": [{"Countries":
[], "Streams": []}, {"Countries": [], "Streams": []}]}`. Response shape:
`{"bestRate": 15.0, "domesticRate": 30.0, "treatyRate": 15.0,
"whtRoutes": []}`. For Australia (source) -> Singapore (residence) ->
Portfolio Dividend, the live API returned bestRate=15.0, domesticRate=
30.0, treatyRate=15.0 - exactly matching the UI's rendered "Best
Rate"/"Domestic Rate"/"Treaty Rate" table (confirmed via direct HTML dump:
a real `<table>` with one row per rate, not a div-based layout). This
matches `calculator_repatriation_page.py`'s already-documented AU->SG
Portfolio Dividend Treaty Rate=15.00% anchor (same underlying treaty
article, cross-checked there against `GET /api/Treaty?hostCountryCode=
AU&partnerCountryCode=SG`) - used here as this module's own independent,
live-reproducible calculation-validation anchor via
`page.expect_response()` around the triggering combobox selection (NOT a
bare `page.request.*` call - see the project's documented JWT/localStorage
auth constraint).

**REAL, LIVE-CONFIRMED NEGATIVE BEHAVIOR**: selecting the SAME country for
both Source and Residence Jurisdiction triggers an `.rs-modal-wrapper`
reading "Please select different Source Jurisdiction and Residence
Jurisdiction." with only a "Cancel" button (no API call fires, no results
table renders) - the SAME family of blocking validation already documented
for Repatriation Calculator, different exact wording.

**"Start Over"** opens a confirm dialog reading "Are you sure to reset all
your selections?" (Cancel/Yes) - same confirm-before-reset pattern as
Questionnaire Creator's "Start Over", different exact wording.

Same no-deep-link quirk as every other Calculator/Tools page: no `goto()`
here, reach it only via `CalculatorMenu.open_item("WHT Router", ...)`."""
from playwright.sync_api import Page

WHT_ROUTER_API = "https://regplusnest.api.kaz.com.bd/api/WhtRouter"


class WhtRouterPage:
    def __init__(self, page: Page):
        self.page = page
        self.instructions_heading = page.get_by_role("heading", name="How to complete this calculation")
        self.mode_by_jurisdiction = page.get_by_text("By Jurisdiction", exact=True)
        self.mode_by_entity = page.get_by_text("By Entity", exact=True)
        self.calculate_button = page.get_by_role("button", name="Calculate")
        self.start_over_button = page.get_by_role("button", name="Start over")
        self.start_over_confirm_heading = page.get_by_text("Are you sure to reset all your selections?", exact=True)
        self.start_over_confirm_yes = page.get_by_role("button", name="Yes")
        self.start_over_confirm_cancel = page.get_by_role("button", name="Cancel")
        self.generate_memo_button = page.get_by_role("button", name="Generate Memo")
        self.get_forms_button = page.get_by_role("button", name="Get Forms")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.message_modal = page.locator(".rs-modal-wrapper")
        self.message_modal_cancel = self.message_modal.get_by_role("button", name="Cancel")
        self.results_table = page.locator("table").first
        self.optimized_result_heading = page.get_by_text("Optimized Result Table", exact=True)
        self.intermediaries_select = lambda n: page.get_by_role("button", name="Select").nth(n - 1)
        self.intermediaries_modal_heading = page.get_by_text("Intermediate Streams and Jurisdictions", exact=True)
        self.intermediaries_select_all = page.get_by_text("Select All", exact=True)
        self.intermediaries_select_none = page.get_by_text("Select None", exact=True)
        self.intermediaries_done_button = page.get_by_role("button", name="Done")

    def source_jurisdiction_combobox(self):
        return self.page.get_by_text("Source Jurisdiction", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def income_stream_combobox(self):
        return self.page.get_by_text("Income Stream", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def residence_jurisdiction_combobox(self):
        return self.page.get_by_text("Residence Jurisdiction", exact=True).locator(
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

    def residence_company_combobox(self):
        return self.page.get_by_text("Residence Company", exact=True).locator(
            "xpath=following::*[@role='combobox'][1]"
        )

    def rate_row_value(self, label: str):
        """`label` one of "Best Rate"/"Domestic Rate"/"Treaty Rate" -
        confirmed live these render as real `<table><tr><td>` rows, not a
        div-based layout (see module docstring's HTML dump)."""
        return self.results_table.locator("tr", has_text=label).locator("td").nth(1)

    def results_scenario_heading(self):
        """The results table's own caption, e.g. "Portfolio Dividend paid
        from Australia to Singapore"."""
        return self.page.locator("h3").filter(has_text="paid from")

    def intermediary_stream_checkbox(self, name: str):
        """Confirmed live: `<input id="flexCheckChecked..."><label
        for="...">Name</label>` - the checkbox is the label's PRECEDING
        SIBLING, not a descendant (same shape as
        `pages/landing_page.py::category_checkbox`)."""
        return self.page.get_by_text(name, exact=True).locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )

    def intermediary_country_checkbox(self, name: str):
        return self.page.get_by_text(name, exact=True).locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )

    def _ensure_open(self, combobox):
        """Copied from `calculator_repatriation_page.py::_ensure_open()` -
        same already-confirmed-live rsuite `SelectPicker` gotcha
        (`aria-expanded` unreliable right after a click)."""
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
