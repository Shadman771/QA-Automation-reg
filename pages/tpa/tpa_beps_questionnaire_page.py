"""TPA > BEPS > BEPS Questionnaire (/tpa/BEPSQuestionnaireCreator). Confirmed
live via scratchpad discovery scripts (not part of the suite): "BEPS" is a
SUBMENU nested inside the unlabeled "more" overflow menu (same shape as
Treaties/Commentary/Tools - confirmed live via a full nav HTML dump, see
pages/tpa/tpa_common.py), holding exactly 2 real children:

    BEPS Questionnaire -> /tpa/BEPSQuestionnaireCreator
    BEPS Mapper        -> /tpa/beps

No 5-sub-feature or otherwise invented shape exists - confirmed live via the
"more" menu's own submenu HTML dump, same discovery discipline as Treaties'
"doesn't mirror WTA's 5-page shape" finding.

**Real, live-confirmed structural identity**: this page is byte-identical in
shape to WTA's own Tools > Questionnaire Creator
(pages/wta/tools_questionnaire_creator_page.py) and TPA's own FAR
Questionnaire (pages/tpa/tpa_tools_far_questionnaire_page.py's underlying
creation flow) - NOT assumed, confirmed via a full HTML dump showing the
identical Syncfusion rich-text-editor markup (`div.e-content` /
`id="richtexteditor_..."`), the same `Start Over` / `Export` / `Add to
Project` toolbar, and the same left "Questions" tree (grouped by topic,
e.g. "The digital economy" > "Hybrid mismatch arrangements" >
"To what extent are hybrid instruments used to gain tax advantages?").

Confirmed live the editor already carries pre-existing content from prior
manual/automation use on this shared account (same "account-level draft
state, not per-session" behavior as WTA's own Questionnaire Creator) - tests
that need "editor is empty" first drive a Start Over + confirm rather than
assuming a blank starting state, same pattern as the WTA page. An emptied
editor reads exactly `<p><br></p>` (confirmed live), which is why
`editor_is_empty()` below keys off the inserted-block marker rather than
"has no child elements".

**Real, live-confirmed tree gotchas (all three cost a full suite run each to
pin down, so they are worth reading before touching this page)**:

1. **The sub-topic row is a plain TOGGLE, and leaves normally start
   EXPANDED.** Confirmed live by printing visibility after each step: on a
   normal load the leaf "To what extent are hybrid instruments used to gain
   tax advantages?" is already `is_visible() == True`; clicking its
   sub-topic row ("Hybrid mismatch arrangements") COLLAPSES it
   (`-> False`), and clicking again re-expands it (`-> True`). So an
   unconditional "expand first" click actively breaks the interaction -
   expand only when the leaf is genuinely hidden (which in practice means
   immediately after a Start Over). The top-level topic row ("The digital
   economy") is NOT involved at all; clicking it changes nothing.
2. **A collapsed leaf cannot be force-clicked.** WTA's own page documents a
   `force=True` accommodation for its equivalent collapsed state; that does
   NOT work here - Playwright's `force` still requires visibility, and
   forced clicks failed fast with "Element is not visible" across a whole
   suite run. Driving the real toggle is the only honest fix.
3. **Question-tree locators MUST be scoped to the tree** (see
   `question_node()` below) - once a question is inserted, the editor
   renders its text verbatim, so an unscoped exact-text lookup matches two
   elements and resolves to the editor's own copy.

**Real, live-confirmed application behavior**: inserting a question that is
ALREADY in the editor is a NO-OP, not a duplicate insert (confirmed live:
editor stayed at exactly 357 chars across a repeat click). Any test
asserting "clicking a question grows the editor" must therefore reset via
Start Over first, or it measures a no-op - the same reset-first rationale
the equivalent WTA test documents.

Unlike WTA's Tools pages (no deep link at all) but LIKE every other TPA
page, this supports a direct deep link (confirmed live for
/tpa/BEPSQuestionnaireCreator) - `goto()` below uses the shared `tpa_goto`
helper, same pattern as every other TPA page object.

An "Ask AI" control is also present (confirmed live, not explored further -
out of scope for this round beyond confirming its presence, since driving a
real AI generation round-trip is not a deterministic, repeatable assertion)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto


class TpaBepsQuestionnairePage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Questions")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.ask_ai_button = page.get_by_role("button", name="Ask AI")
        self.editor = page.locator("div.e-content").first

        self.start_over_dialog = page.locator("[role='dialog']").filter(has_text="Confirm Start Over")
        self.start_over_yes = self.start_over_dialog.get_by_role("button", name="Yes")
        self.start_over_no = self.start_over_dialog.get_by_role("button", name="No")

        self.add_to_project_dialog = page.locator(".rs-modal, [role='dialog']").filter(has_text="Add to Project")
        self.add_to_project_title_input = self.add_to_project_dialog.locator("input[name='name']")
        self.add_to_project_submit_button = self.add_to_project_dialog.get_by_role("button", name="Add")

    def goto(self):
        tpa_goto(self.page, "/tpa/BEPSQuestionnaireCreator")

    def question_node(self, text: str):
        """Scoped to the question tree's own `<li id="treeCheck_NNN">` rows,
        NOT the whole page.

        Real, live-confirmed ambiguity this guards against: once a question
        has been inserted, the editor renders that same question text
        verbatim, so an unscoped `get_by_text(text, exact=True)` matches
        TWO elements - the tree leaf and the editor's own copy - and
        `.first` resolves to the editor copy (inside a `contenteditable`),
        where every click times out as not-stable. Confirmed live: this was
        the root cause of 3 tests hanging for their full 60s timeout
        budget."""
        return self.page.locator("li[id^='treeCheck_']").get_by_text(text, exact=True)

    def topic_node(self, text: str):
        """A collapsible topic/SUB-TOPIC row - clicking a top-level topic
        (e.g. "The digital economy") then its sub-topic (e.g. "Hybrid
        mismatch arrangements") is what reveals the leaf questions; the
        sub-topic alone is not enough (confirmed live, see the module
        docstring). Scoped to the tree for the same reason as
        `question_node()`."""
        return self.page.locator("li[id^='treeCheck_']").get_by_text(text, exact=True)

    def topic_expand_icon(self, text: str):
        """The real expand/collapse affordance for a topic row: the
        `span.icon-plus`/`span.icon-minus` inside that row's own `<li>`.

        Confirmed live, and the thing that finally made post-Start-Over
        inserts work: clicking the row's TEXT does not re-expand a
        collapsed topic (the leaf stayed hidden through a 10s
        `wait_for_content` and the subsequent leaf click then burned its
        full 60s timeout), while clicking this icon expands it immediately
        (leaf visible, and the following insert grew the editor 11 -> 357
        chars). `.last` picks the innermost matching `<li>`, since every
        ancestor `<li>` also contains the same text."""
        return (self.page.locator("li[id^='treeCheck_']")
                .filter(has_text=text).last
                .locator("span.icon-plus, span.icon-minus").first)

    def expand_topic(self, text: str):
        self.topic_expand_icon(text).click()

    def click_question(self, text: str):
        self.question_node(text).first.click()

    def editor_html(self) -> str:
        return self.editor.inner_html()

    def editor_is_empty(self) -> bool:
        """Same marker-based heuristic as WTA's own Questionnaire Creator
        (confirmed live: inserted blocks share the identical
        `class="questionnaireDiv"` wrapper) - checking for zero child
        elements is NOT reliable here, since 'Start Over' can leave behind
        an empty `<p>`/`<br>` wrapper that still counts as a child."""
        html = self.editor_html().strip()
        return html.lower() in ("<br>", "") or "questionnairediv" not in html.lower()
