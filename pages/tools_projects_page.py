"""Tools > Projects (/wta/Project). Confirmed live (scratchpad discovery
scripts, throwaway - not part of the suite):

  - The page is a real project-management workspace: a left list of every
    project the logged-in user has ever saved (title + a folder icon),
    and a right-hand detail pane showing the currently-selected project's
    saved items as a table with columns ['#', 'Title', 'Description',
    'Jurisdiction', 'Type'] (items are added to a project from elsewhere in
    the app, e.g. Questionnaire Creator's "Add to Project"). On first load
    the detail pane shows whichever project was most recently active - not
    a fixed placeholder like the Treaties pages' left panel.
  - "New Project" opens a modal (`Project Name *` text input, Cancel/Save).
    Save is a real HTML `disabled` button while the name field is empty -
    confirmed live via `Locator.is_disabled()` (the app never lets you
    submit a blank name; there is no separate inline error message, the
    disabled Save button IS the validation).
  - Each row in the project list only reveals its `Export` / `Edit` /
    `Delete` actions on hover (`opacity-0 group-hover:opacity-100` - all
    three are plain `<a class="reg-link-button">`, NOT `<button>`
    elements, so `get_by_role("button", ...)` does not match them; this
    page object uses `get_by_text(..., exact=True)` scoped to the row).
  - `Edit` opens a "Rename" modal (same `Project Name *` field, pre-filled,
    Cancel/Update).
  - `Delete` opens a "Confirm Delete" modal ("Are you sure you want to
    delete this project?", Cancel/Delete). Confirmed live: deleting removes
    the row immediately (0 matches for the deleted title afterwards) - a
    real, working destructive action.
  - Clicking a project's title (not Edit/Delete) switches the right-hand
    detail pane to that project's own item table.
  - There is no visible pagination/search on the list itself in this
    account's current data (dozens of pre-existing projects from prior
    manual/automation use), and no visible empty state was reachable
    without deleting all real project data, so that state is NOT
    asserted on (never fabricate what wasn't actually observed)."""
from playwright.sync_api import Page


class ProjectsPage:
    def __init__(self, page: Page):
        self.page = page
        self.new_project_button = page.get_by_role("button", name="New Project")
        self.table = page.locator("table")
        self.table_rows = page.locator("table tbody tr")

        # "New Project" / "Rename" modal (same shape, different title/submit
        # label) - both are the single open `.rs-modal` at a time.
        self.modal = page.locator(".rs-modal, [role='dialog']").first
        self.modal_name_input = self.modal.locator("input[name='name']")
        self.modal_save_button = self.modal.get_by_role("button", name="Save")
        self.modal_update_button = self.modal.get_by_role("button", name="Update")
        self.modal_cancel_button = self.modal.get_by_role("button", name="Cancel")

        # "Confirm Delete" modal.
        self.delete_modal_heading = page.get_by_text("Confirm Delete", exact=True)
        self.delete_confirm_button = self.modal.get_by_role("button", name="Delete")

    def open_new_project_modal(self):
        self.new_project_button.click()

    def project_row(self, title: str):
        """The row `<div>` wrapping a project's title + its (hover-only)
        Export/Edit/Delete actions, found via the visible title text."""
        return self.page.locator(
            f"xpath=//span[normalize-space(text())='{title}']"
            f"/ancestor::div[contains(@class,'flex-col')][1]"
        )

    def project_title(self, title: str):
        return self.page.get_by_text(title, exact=True)

    def row_action(self, title: str, action: str):
        """action is one of 'Export' / 'Edit' / 'Delete' - hover-revealed
        <a> links, scoped to this project's own row."""
        row = self.project_row(title)
        row.hover()
        return row.get_by_text(action, exact=True)

    def project_exists(self, title: str) -> bool:
        return self.project_title(title).count() > 0
