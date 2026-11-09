"""TPA > Tools > Analyzer (/tpa/DecisionFlows, on-page heading "Please
click the 'New Analysis' button to run an Analysis."). Confirmed live via
scratchpad discovery scripts (not part of the suite): the Tools submenu's
label reads "Analyzer" but the route is `/tpa/DecisionFlows` - an
intentional, confirmed-live naming mismatch, not a bug to "fix" into
matching strings.

The list view shows one row (`<li>`) per saved analysis, with two PLAIN
TEXT `Edit`/`Delete` `<a>` links per row - NOT a kebab menu like Templates/
FAR Questionnaire. Confirmed live via a full DOM-ancestry dump: these
links are HOVER-ONLY (`opacity-0 group-hover:opacity-100`, same pattern as
WTA's own Tools Projects rows, see pages/wta/tools_projects_page.py) - a
row must be `.hover()`-ed before Edit/Delete become clickable. Also a
"New Analysis" button and a "Description of Analyses" help section.

**Real, live-confirmed gotcha**: the "Analysis name" field's `placeholder`
attribute is CASED DIFFERENTLY between the two flows - `"Analysis name"`
(lowercase 'n') in the "Create Analysis" modal (`name="Name"`) vs.
`"Analysis Name"` (capital 'N') in the "Edit Analysis" modal, confirmed
live via a full `<input>` attribute dump of both modals. `name_input`
below matches either casing so callers don't need to special-case it per
flow. The "Edit Analysis" modal also has NO mode radios (By Jurisdiction/
By Entity) - those only appear in "Create Analysis".

"New Analysis" opens a `.rs-modal-wrapper` titled "Create Analysis" with:
  - a `mode` radio pair: "By Jurisdiction" / "By Entity" (same two-mode
    shape as WTA's own Repatriation/WHT Router/Loss Relief calculators -
    confirmed live these are real `input[name='mode']` radios, index [0]
    = By Jurisdiction, [1] = By Entity)
  - `Name` (placeholder "Analysis name", required)
  - `RelatedParty1` (placeholder "Tested Party", required)
  - `RelatedParty2` (placeholder "Related Party", required)
  - two more required `<select>`-style controls: "Tax Residence Tested
    Party" / "Tax Residence Related Party" (each shows a "Select"
    placeholder)
  - `TransactionData` (placeholder "Analysis description...", optional,
    "Maximum 50 characters" hint)
  - Cancel / Save

Supports a direct deep link (`/tpa/DecisionFlows`, confirmed live, same
pattern as every other TPA page - see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto


class TpaAnalyzerPage:
    def __init__(self, page: Page):
        self.page = page
        self.new_analysis_button = page.get_by_role("button", name="New Analysis")
        self.description_heading = page.get_by_text("Description of Analyses", exact=True)

        self.modal = page.locator(".rs-modal-wrapper").first
        self.modal_heading = self.modal.get_by_text("Create Analysis", exact=True)
        # "Edit" opens the SAME modal shape under a different heading ("Edit
        # Analysis", no mode radios) and no mode radios - confirmed live.
        self.edit_modal_heading = self.modal.get_by_text("Edit Analysis", exact=True)
        self.mode_radios = self.modal.locator("input[name='mode']")
        self.name_input = self.modal.locator("input[placeholder='Analysis name'], input[placeholder='Analysis Name']")
        self.tested_party_input = self.modal.locator("input[placeholder='Tested Party']")
        self.related_party_input = self.modal.locator("input[placeholder='Related Party']")
        # Both "Tax Residence Tested Party"/"Tax Residence Related Party"
        # are required rsuite SelectPickers, each showing a "Select"
        # placeholder until a value is chosen - confirmed live via a full
        # option-count dump (100+ countries each).
        self.tax_residence_selects = self.modal.get_by_text("Select", exact=True)
        self.select_options = page.locator("[role='option']:visible, li.rs-picker-select-menu-item:visible")
        self.description_input = self.modal.locator("input[placeholder='Analysis description...'], textarea[placeholder='Analysis description...']")
        self.modal_save_button = self.modal.get_by_role("button", name="Save")
        self.modal_cancel_button = self.modal.get_by_role("button", name="Cancel")

    def goto(self):
        tpa_goto(self.page, "/tpa/DecisionFlows")

    def pick_first_tax_residence_option(self):
        """Opens whichever 'Tax Residence ...' select still shows its
        'Select' placeholder and picks its first real option - both
        residence pickers are required (confirmed live: Save silently
        re-shows inline errors and does not submit if either is left as
        'Select'), so this is called twice to fill both."""
        self.tax_residence_selects.first.click()
        self.page.wait_for_timeout(600)
        self.select_options.first.click()
        self.page.wait_for_timeout(300)

    def analysis_row_title(self, name: str):
        return self.page.get_by_text(name, exact=True)

    def analysis_exists(self, name: str) -> bool:
        return self.analysis_row_title(name).count() > 0

    def analysis_row(self, name: str):
        """The row `<li>` for the analysis named `name` - confirmed live
        via DOM-ancestry inspection (the title text's 3rd ancestor)."""
        return self.analysis_row_title(name).locator("xpath=ancestor::li[1]")

    def row_action(self, name: str, action: str):
        """action one of 'Edit'/'Delete' - HOVER-ONLY plain `<a>` links
        scoped to this analysis's own row (see module docstring)."""
        row = self.analysis_row(name)
        row.hover()
        return row.get_by_text(action, exact=True)
