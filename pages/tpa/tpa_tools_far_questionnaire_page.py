"""TPA > Tools > FAR Questionnaire (/tpa/FARQuestionnaireCreator). Confirmed
live via scratchpad discovery scripts (not part of the suite): a
list-based questionnaire workspace, structurally closer to Templates than
to WTA's own single-editor "Questionnaire Creator"
(pages/wta/tools_questionnaire_creator_page.py).

The list view shows a table (columns: Title, SIC Code, Status, Created,
Updated) with one row per saved questionnaire, each with a kebab
("more-menu") dropdown holding exactly 5 items (confirmed live): Preview,
Edit Questionnaire, Delete Questionnaire, Export to Word, Export to PDF -
same shape as Templates' own per-row kebab menu, a DIFFERENT shape from
Analyzer's plain hover-only Edit/Delete links.

"Add Questionnaire" opens a `.rs-modal-wrapper` titled "Add FAR
Questionnaire" with:
  - `Title*` (placeholder "Enter title", required)
  - `SIC Code*` (a "Select SIC Code" dropdown, required)
  - an optional file-upload "Attachments" drop zone (max 25MB, PDF/DOC/DOCX)
  - Cancel / "Create & Generate"

Confirmed live: this is an AI-driven flow ("The AI uses these files
together with the title and SIC code to generate relevant questions") -
"Create & Generate" is expected to take real backend time to produce
content, so tests that complete this flow allow a generous wait before
asserting the new row exists, and always clean up via its own
"Delete Questionnaire" kebab action afterward.

Supports a direct deep link (`/tpa/FARQuestionnaireCreator`, confirmed
live, same pattern as every other TPA page - see
pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from utils.wait import wait_for_content


class TpaFarQuestionnairePage:
    def __init__(self, page: Page):
        self.page = page
        self.add_questionnaire_button = page.get_by_role("button", name="Add Questionnaire")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")
        self.col_title = page.locator("table thead th").filter(has_text="Title")
        self.col_sic_code = page.locator("table thead th").filter(has_text="SIC Code")
        self.col_status = page.locator("table thead th").filter(has_text="Status")

        self.modal = page.locator(".rs-modal-wrapper").first
        self.modal_heading = self.modal.get_by_text("Add FAR Questionnaire", exact=True)
        self.title_input = self.modal.get_by_placeholder("Enter title")
        self.sic_code_select = self.modal.get_by_text("Select SIC Code", exact=True)
        self.modal_cancel_button = self.modal.get_by_role("button", name="Cancel")
        self.create_and_generate_button = self.modal.get_by_role("button", name="Create & Generate")

    def goto(self):
        """Confirmed live: the questionnaire table loads asynchronously
        after the button/heading render - same async-render race already
        documented for Templates/Projects - waits for the table itself
        before returning control."""
        tpa_goto(self.page, "/tpa/FARQuestionnaireCreator")
        wait_for_content(self.table, timeout=15000)

    def row_by_title(self, title: str):
        return self.table_rows.filter(has_text=title).first

    def row_exists(self, title: str) -> bool:
        return self.table_rows.filter(has_text=title).count() > 0

    def open_row_menu(self, title: str):
        self.row_by_title(title).locator(".more-menu[role='button'], a[role='button']").first.click()
        return self.page.locator("ul[role='menu']:visible li[role='menuitem']")
