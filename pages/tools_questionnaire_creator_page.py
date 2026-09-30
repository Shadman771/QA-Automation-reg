"""Tools > Questionnaire Creator (/wta/QuestionnaireCreator). Confirmed live
(scratchpad discovery scripts, throwaway - not part of the suite):

  - A rich-text questionnaire builder: a left "Questions" tree grouped by
    topic (Incorporation, Royalties, ... - dozens of pre-authored questions,
    data-driven, not hardcoded here beyond the handful used as fixtures)
    and a right-hand Syncfusion rich-text editor (`div.e-content`, backed
    by a hidden `<textarea class="e-rte-hidden">`) that questions get
    inserted into when clicked.
  - Toolbar: `Start Over`, `Add to Project`, plus font-family ("Arial") and
    font-size ("10") pickers and an `Export` control - all part of the
    rich-text editor chrome, not plain HTML `<select>` elements (confirmed
    live: `select` count is 0 on this page).
  - `Start Over` opens a real confirmation dialog ("Confirm Start Over -
    'Start Over' will remove all of your question(s). Do you want to
    proceed?", No/Yes). Confirmed live: clicking "Yes" actually empties the
    editor (`div.e-content` innerHTML collapses to a bare `<br>`) - a real,
    working destructive/reset action, not just a dialog that does nothing.
  - Clicking a question's visible text in the tree inserts a formatted
    question block (`<span class="questionnaireDiv" id="<n>_question">...`)
    into the editor, growing its content - confirmed live by innerHTML
    length increasing after the click.
  - The editor's content persists across page loads for the same user
    (confirmed live: it was NOT empty on a fresh navigation before any
    interaction) - it is account-level draft state, not per-session, so
    tests that assert on "the editor is empty" first drive a Start Over +
    confirm rather than assuming a blank starting state.
  - `Add to Project` opens its own modal for picking/creating a target
    project (saving the current questionnaire content into Tools >
    Projects) - covered at the level of "the modal opens", since driving a
    full save-and-verify-in-Projects round trip is exercised end-to-end by
    the Projects page's own create/rename/delete coverage instead of
    duplicating it here.
  - Confirmed live (and the cause of a real automation bug caught while
    building this suite): `Add to Project` is NOT rendered at all
    (`get_by_role("button", name="Add to Project").count() == 0`, not
    merely hidden/disabled) while the editor is empty - it only appears
    once at least one question has been inserted. Every test that needs
    this button must insert a question first; asserting its presence on a
    genuinely empty editor is a false expectation, not a real app defect.
  - After a 'Start Over' confirm, the tree's topic groups (e.g.
    "Incorporation") re-collapse and a leaf question's label goes into a
    state Playwright's actionability check reports as "hidden" - it does
    NOT self-resolve by waiting (confirmed: still hidden after 19s
    polling), and real/synthesized clicks aimed at re-expanding the
    parent topic proved unreliable. However, the label is still
    functionally wired to its click handler despite being clipped
    (confirmed live: `locator.click(force=True)` on the "hidden" label
    correctly inserts the question, growing the editor 4 -> 318 chars) -
    likely a max-height/overflow collapse rather than `display:none`.
    Tests click questions with `force=True` for this reason, not to
    paper over a real bug - the app itself never blocks this click."""
from playwright.sync_api import Page


class QuestionnaireCreatorPage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Questions")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.editor = page.locator("div.e-content").first

        # "Confirm Start Over" dialog - scoped by its own text since several
        # rsuite/syncfusion dialog containers exist in the DOM at once.
        self.start_over_dialog = page.locator("[role='dialog']").filter(has_text="Confirm Start Over")
        self.start_over_yes = self.start_over_dialog.get_by_role("button", name="Yes")
        self.start_over_no = self.start_over_dialog.get_by_role("button", name="No")

        self.add_to_project_dialog = page.locator(".rs-modal, [role='dialog']").filter(has_text="Add to Project")

    def question_node(self, text: str):
        return self.page.get_by_text(text, exact=True)

    def click_question(self, text: str):
        self.question_node(text).first.click()


    def editor_html(self) -> str:
        return self.editor.inner_html()

    def editor_is_empty(self) -> bool:
        html = self.editor_html().strip().lower()
        return html in ("<br>", "") or "questionnairediv" not in html
