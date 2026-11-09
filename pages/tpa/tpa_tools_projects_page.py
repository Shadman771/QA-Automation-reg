"""TPA > Tools > Projects (/tpa/Project). Confirmed live via scratchpad
discovery scripts (not part of the suite): a real project-management
workspace - same business idea as WTA's own Tools Projects
(pages/wta/tools_projects_page.py) but a DIFFERENT, richer DOM shape,
confirmed live rather than assumed to match:

  - "New Project" opens a `.rs-modal-wrapper` with a single `Project Name
    *` input (name='name') and Cancel/Save.
  - Each project row's "Export" / "Edit" / "Delete" `<a>` links are
    HOVER-ONLY (`opacity-0 group-hover:opacity-100`, confirmed live via a
    full row HTML dump - same pattern as WTA's own Tools Projects rows,
    see pages/wta/tools_projects_page.py). A row must be `.hover()`-ed
    first.
  - Clicking a project's own title switches the right-hand detail pane to
    that project, which shows 3 tabs - "Regulatory Reports" / "Research" /
    "Documents" - each backed by its own table with columns ['#', 'Title',
    'Description', 'Path', 'Type'] (confirmed live for the shared
    pre-existing "TEST QA" project; items land in these tables via other
    in-app flows, e.g. Templates/FAR Questionnaire/Analyzer's own
    "Add to Project").

Supports a direct deep link (`/tpa/Project`, confirmed live, same pattern
as every other TPA page - see pages/tpa/tpa_common.py), unlike WTA's own
`/wta/Project` which redirects any direct `goto()` to `/wta/Information`."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from utils.wait import wait_for_content


class TpaProjectsPage:
    def __init__(self, page: Page):
        self.page = page
        self.new_project_button = page.get_by_role("button", name="New Project")

        self.modal = page.locator(".rs-modal-wrapper").first
        self.modal_name_input = self.modal.locator("input[name='name']")
        self.modal_save_button = self.modal.get_by_role("button", name="Save")
        self.modal_update_button = self.modal.get_by_role("button", name="Update")
        self.modal_cancel_button = self.modal.get_by_role("button", name="Cancel")
        self.delete_confirm_button = self.modal.get_by_role("button", name="Delete")

        self.tab_regulatory_reports = page.get_by_text("Regulatory Reports", exact=True)
        self.tab_research = page.get_by_text("Research", exact=True)
        self.tab_documents = page.get_by_text("Documents", exact=True)
        self.detail_table = page.locator("table")

    def goto(self):
        """Confirmed live: the project list loads asynchronously after the
        'New Project' button renders - same async-render race already
        documented for Templates' own document table - waits for the
        'New Project' button AND gives the list a moment to populate."""
        tpa_goto(self.page, "/tpa/Project")
        wait_for_content(self.new_project_button, timeout=15000)
        self.page.wait_for_timeout(800)

    def open_new_project_modal(self):
        self.new_project_button.click()

    def project_title(self, title: str):
        return self.page.get_by_text(title, exact=True)

    def project_exists(self, title: str) -> bool:
        return self.project_title(title).count() > 0

    def project_row(self, title: str):
        return self.project_title(title).first.locator(
            "xpath=ancestor::div[contains(@class,'flex-col')][1]"
        )

    def row_action(self, title: str, action: str):
        """action one of 'Export'/'Edit'/'Delete' - HOVER-ONLY links
        scoped to this project's own row (see module docstring)."""
        row = self.project_row(title)
        row.hover()
        return row.get_by_text(action, exact=True)
