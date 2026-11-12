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

**Real, live-confirmed tree gotchas (all five cost a full suite run each to
pin down, so they are worth reading before touching this page)**:

1. **The sub-topic row is a plain TOGGLE, and leaves normally start
   EXPANDED.** Confirmed live by printing visibility after each step: on a
   normal load the leaf "To what extent are hybrid instruments used to gain
   tax advantages?" is already `is_visible() == True`; clicking its
   sub-topic row ("Hybrid mismatch arrangements") COLLAPSES it
   (`-> False`), and clicking again re-expands it (`-> True`). So an
   unconditional "expand first" click actively breaks the interaction -
   expand only when the topic is genuinely collapsed (which in practice
   means immediately after a Start Over). The top-level topic row ("The
   digital economy") is NOT involved at all; clicking it changes nothing.
2. **A collapsed leaf cannot be force-clicked.** WTA's own page documents a
   `force=True` accommodation for its equivalent collapsed state; that does
   NOT work here - Playwright's `force` still requires visibility, and
   forced clicks failed fast with "Element is not visible" across a whole
   suite run. Driving the real toggle is the only honest fix.
3. **Question-tree locators MUST be scoped to the tree** (see
   `question_node()` below) - once a question is inserted, the editor
   renders its text verbatim, so an unscoped exact-text lookup matches two
   elements and resolves to the editor's own copy.
4. **The `icon-plus`/`icon-minus` class is NOT a state indicator - it is a
   constant.** This is the single root cause of tests _02-_06 failing
   in-suite while passing standalone (diagnosed 2026-11-12 by dumping the
   row's real DOM across a full toggle cycle). The toggle `<span>` reads
   `icon-plus` in ALL states - freshly expanded, collapsed, and
   re-expanded - so any code that infers "is it collapsed?" from the icon
   class, or that locates the affordance as `span.icon-plus` expecting that
   to mean "collapsed", is reading a value that never changes. The ONLY
   observable expansion state is the topic row's own child `<ul>`:
   `class="... pl-5 flex flex-col"` / `display: flex` when EXPANDED versus
   `class="... pl-5 hidden"` / `display: none` when COLLAPSED (Tailwind's
   `hidden`). `is_topic_expanded()` below reads exactly that, and
   `topic_child_list()` is the locator to wait on to CONFIRM an expansion
   actually happened rather than assuming the click worked.
5. **The tree is not in the DOM for ~1.5s after `goto()` returns.**
   Confirmed live by polling from the moment of navigation: immediately
   after `tpa_goto` the question tree is `count == 0` (not merely hidden -
   genuinely absent), and the fixture leaf first becomes visible ~1.50s
   later. `Locator.is_visible()` does NOT auto-wait, so a bare visibility
   probe taken right after `goto()` returns False for a tree that is simply
   still rendering. Combined with gotcha 4 this produced the exact in-suite
   failure signature seen in `logs/TPA BEPS Questionnaire/`: the probe
   misread "still rendering" as "collapsed", blind-clicked the toggle, and
   thereby COLLAPSED an already-expanded topic - after which the leaf never
   appeared (10s `wait_for_content` burned) and the subsequent leaf click
   burned its full 60s timeout. `goto()` below therefore waits for the tree
   to genuinely render before returning control, so every state read after
   it is taken against a real, settled DOM.

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
from utils.wait import wait_for_content


class TpaBepsQuestionnairePage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Questions")
        self.start_over_button = page.get_by_role("button", name="Start Over")
        self.add_to_project_button = page.get_by_role("button", name="Add to Project")
        self.ask_ai_button = page.get_by_role("button", name="Ask AI")
        self.editor = page.locator("div.e-content").first
        self.tree_rows = page.locator("li[id^='treeCheck_']")

        self.start_over_dialog = page.locator("[role='dialog']").filter(has_text="Confirm Start Over")
        self.start_over_yes = self.start_over_dialog.get_by_role("button", name="Yes")
        self.start_over_no = self.start_over_dialog.get_by_role("button", name="No")

        self.add_to_project_dialog = page.locator(".rs-modal, [role='dialog']").filter(has_text="Add to Project")
        self.add_to_project_title_input = self.add_to_project_dialog.locator("input[name='name']")
        self.add_to_project_submit_button = self.add_to_project_dialog.get_by_role("button", name="Add")

    def goto(self) -> bool:
        """Navigates, then waits for the question tree to GENUINELY render
        before returning control.

        This wait is load-bearing, not defensive padding: confirmed live
        (see gotcha 5 in the module docstring) the tree is absent from the
        DOM for ~1.5s after `tpa_goto` returns, and `Locator.is_visible()`
        does not auto-wait - so without this, any caller that reads tree
        state immediately after `goto()` reads it against a half-rendered
        page and draws the wrong conclusion."""
        tpa_goto(self.page, "/tpa/BEPSQuestionnaireCreator")
        return wait_for_content(self.tree_rows, timeout=20000)

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

    def topic_row(self, text: str):
        """The topic/sub-topic row's own `<li>`. `.last` picks the
        innermost matching `<li>`, since every ancestor `<li>` also
        contains the same text."""
        return self.tree_rows.filter(has_text=text).last

    def topic_child_list(self, text: str):
        """The topic row's own child `<ul>` - THE single source of truth
        for whether that topic is expanded.

        Confirmed live (gotcha 4 in the module docstring): expanded renders
        `class="... pl-5 flex flex-col"` (`display: flex`), collapsed
        renders `class="... pl-5 hidden"` (`display: none`). Because
        Tailwind's `hidden` resolves to `display: none`, Playwright's own
        visibility check on this element IS the expansion state - no
        `page.evaluate` or class-string parsing needed, and it is a real
        locator, so it can be waited on to confirm an expansion actually
        took effect."""
        return self.topic_row(text).locator("xpath=./ul").first

    def topic_toggle(self, text: str):
        """The expand/collapse affordance: the toggle `<span>` in the
        topic row.

        Matched on the `icon-` class PREFIX deliberately rather than on
        `span.icon-plus`: confirmed live that this class is a constant that
        reads `icon-plus` whether the topic is expanded or collapsed (see
        gotcha 4), so selecting specifically on `icon-plus` would wrongly
        imply the match itself carries state information."""
        return self.topic_row(text).locator("span[class*='icon-']").first

    def is_topic_expanded(self, text: str) -> bool:
        """Reads the REAL expansion state off the child `<ul>`, never off
        the (constant) toggle icon class."""
        child = self.topic_child_list(text)
        return child.count() > 0 and child.is_visible()

    def ensure_topic_expanded(self, text: str, timeout: int = 10000) -> bool:
        """Leaves `text`'s topic expanded, and returns whether it is.

        Deterministic and state-based rather than a retry loop: it waits
        for the row to exist, reads the genuine expansion state, toggles
        AT MOST ONCE (and only if actually collapsed), then confirms the
        expansion through an observable DOM change. A topic that is
        already expanded is left alone - clicking it would collapse it,
        which is exactly the bug this replaces. No attempt is made to
        re-click on failure: if one honest toggle does not expand the
        topic, that is a real finding the caller should surface, not
        something to paper over."""
        if not wait_for_content(self.topic_row(text), timeout=timeout):
            return False
        if self.is_topic_expanded(text):
            return True
        self.topic_toggle(text).click()
        return wait_for_content(self.topic_child_list(text), timeout=timeout)

    def wait_for_question_in_editor(self, text: str, timeout: int = 15000) -> bool:
        """Waits for the editor to actually contain the inserted question,
        instead of sleeping a fixed interval and hoping the insert landed."""
        return wait_for_content(self.editor.get_by_text(text, exact=False), timeout=timeout)

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
