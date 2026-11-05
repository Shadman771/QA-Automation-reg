"""TPA > Regulations (/tpa/Regulations). Confirmed live via scratchpad
discovery scripts (not part of the suite): the simplest of the 7 TPA
pages - `JurisdictionPanel` only, no category list.

Selecting a jurisdiction alone renders a "Showing regulations of
<Country>" table with columns Title, Description, "Entry into Force",
Download, Project - each real row has an "Add to Project" button and
(for most rows) a real download link. Confirmed live: 63 "Add to
Project" rows for Australia, a mix of real regulation titles (e.g.
"OECD Transfer Pricing Guidelines 2022", "TR 2020/4") and obvious
Lorem-style seed/test rows ("Reiciendis quas repr") - the same
account-specific seed-noise pattern already confirmed on Forms/National
Rules, not a defect.

Supports a direct deep link (`/tpa/Regulations`, see
pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel


class TpaRegulationsPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.showing_regulations_text = page.get_by_text("Showing regulations of", exact=False)
        self.col_title = page.get_by_text("Title", exact=True)
        self.col_description = page.get_by_text("Description", exact=True)
        self.col_entry_into_force = page.get_by_text("Entry into Force", exact=True)
        self.col_download = page.get_by_text("Download", exact=True)
        self.add_to_project_buttons = page.get_by_text("Add to Project", exact=True)

    def goto(self):
        tpa_goto(self.page, "/tpa/Regulations")

    def row_count(self) -> int:
        return self.add_to_project_buttons.count()
