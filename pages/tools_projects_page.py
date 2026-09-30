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
    asserted on (never fabricate what wasn't actually observed).

Confirmed live via network capture (Playwright `page.on("request"/"response")`,
throwaway scratchpad probes - not part of the suite) - the real REST-ish shape
behind every list mutation, all under `https://regpluswta.api.kaz.com.bd/api/Project/`:

  - Create: `POST CreateProject` body `{"id":0,"name":"<name>"}` -> 200
    `{"id":<newId>,"hasError":false}` on success. On an exact-duplicate name,
    still 200 but `{"id":0,"hasError":true,"errorMessage":"Please choose
    another name"}` - so the backend DOES block true duplicates. However,
    confirmed live: no toast/inline error is ever rendered for the user on
    that rejection (`.Toastify__toast`/`.rs-message`/`[role='alert']` all 0
    matches, and "choose another name" never appears in the page text) - the
    modal simply closes with zero visible feedback. This is a real,
    documented UX gap (silent failure), NOT a data-integrity bug - no
    duplicate row is actually created.
  - Rename: `POST RenameProject` body `{"id":<id>,"name":"<newName>"}` -> 200
    `{"id":<id>,"hasError":false}` - same `id`/`hasError` response shape as
    Create.
  - Delete: `POST Delete` body `{"id":<id>,"name":"<name>"}` -> 200, but a
    DIFFERENT response shape from Create/Rename: `{"isSuccess":<bool>,
    "error":<string|null>}`. Confirmed live (and a real backend quirk worth
    documenting): one observed Delete response had `isSuccess:false` with an
    EF Core "A second operation was started on this context instance..."
    DbContext-threading error message, yet the project was still actually
    gone from the very next `GetProjects` response - i.e. the reported
    `isSuccess` can be an unreliable false-negative under rapid
    back-to-back calls. Because of this, tests here treat HTTP 200 plus the
    project's real absence from the list (the authoritative signal) as the
    pass condition, rather than hard-asserting `isSuccess:true` every time -
    that would risk an intermittent, non-representative failure on a
    genuinely-successful delete.
  - Required-field / input validation, confirmed live: there is no
    `maxlength` attribute on the name `<input>` and no client- or
    server-side length cap was hit at 300 characters (accepted verbatim,
    `hasError:false`). A whitespace-only name (e.g. `"   "`) does NOT
    disable Save (only a fully empty string does) and IS accepted by the
    backend, creating a project with a literally blank-looking title - a
    real, documented gap (the disabled-Save signal is not whitespace-aware).
    Leading/trailing whitespace on an otherwise-valid name is preserved
    verbatim end-to-end (not trimmed client-side before Save-enable, nor
    server-side in storage/response) - a documented observation, not
    necessarily "wrong" for a free-text name field.
  - Special characters, confirmed live: a name containing `<script>...
    </script>` saves and lists successfully, and is NOT rendered as a live
    `<script>` tag anywhere in the page HTML (0 matches for the raw literal
    tag) - it renders back as plain escaped text. Confirmed XSS-safe
    rendering for this field.
  - Persistence, confirmed live: unlike a fresh `page.goto("/wta/Project")`
    from OUTSIDE the app (which redirects to `/wta/Information` - see the
    Tools-menu-level gotcha in `pages/tools_menu.py`), `page.reload()` while
    already on `/wta/Project` stays on `/wta/Project` and the project list
    reloads from the server unchanged - reload is a safe, supported way to
    prove a save was server-persisted rather than only an optimistic
    client-side update.
  - The project item table's data cells (added via Questionnaire Creator's
    "Add to Project", see pages/tools_questionnaire_creator_page.py) render
    each cell's value inside a `<textarea>`, not as plain visible text -
    `Locator.inner_text()` on the `<td>` returns "" for these (browsers
    don't expose a textarea's value through innerText), so verifying a
    saved item's Title requires reading the `<textarea>`'s `.input_value()`
    instead - confirmed live via full DOM inspection of a real saved row."""
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
        Export/Edit/Delete actions, found via the visible title text.

        Uses `get_by_text(..., exact=True)` (which whitespace-normalizes on
        both sides, so a leading/trailing-whitespace `title` still matches -
        confirmed live) chained with an ancestor XPath that contains no
        string literal of `title` itself. A plain XPath string-literal
        match (the previous implementation) breaks - a real bug caught
        while building this suite's special-character coverage - for any
        title containing a single quote (can't be safely embedded in an
        XPath `'...'` literal without a concat() escape), e.g.
        `<script>alert('x')</script>`.

        Scoped to `.first`: this is a real, live, shared account, and a
        title collision (two rows with an identical title) is possible -
        confirmed live, it happened once during this suite's own test
        development. Every caller (hover/click/delete) needs exactly one
        row, so this never returns a multi-match locator that would
        strict-mode-violate on `.hover()`/`.click()`."""
        return self.page.get_by_text(title, exact=True).first.locator(
            "xpath=ancestor::div[contains(@class,'flex-col')][1]"
        )

    def blank_or_whitespace_title_row(self):
        """Locates a project row whose title renders as empty/whitespace-only
        text (e.g. a project created with a whitespace-only name - see
        module docstring on that confirmed-live gap). `normalize-space()`
        can't distinguish "" from many unrelated empty elements, so this
        scans each project title `<span>` directly instead of an XPath
        equality match. Returns None if none is found."""
        spans = self.page.locator("span.text-14-medium")
        for i in range(spans.count()):
            span = spans.nth(i)
            if span.inner_text().strip() == "":
                return span.locator("xpath=ancestor::div[contains(@class,'flex-col')][1]")
        return None

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

    def item_table_row_title_value(self, row_index: int = 0) -> str:
        """The item table's data cells render each value inside a
        `<textarea>` (confirmed live - see module docstring), so a saved
        item's Title must be read via the textarea's `.input_value()`, not
        `Locator.inner_text()` on the `<td>` (which returns "" for a
        textarea's content)."""
        row = self.table_rows.nth(row_index)
        return row.locator("td").nth(2).locator("textarea").first.input_value()
