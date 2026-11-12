"""TPA > BEPS > BEPS Questionnaire (/tpa/BEPSQuestionnaireCreator). See
pages/tpa/tpa_beps_questionnaire_page.py for the full confirmed-live layout
notes (byte-identical Syncfusion rich-text-editor shape to WTA's own Tools
Questionnaire Creator / TPA's own FAR Questionnaire creation flow).

Fixture question used throughout: "To what extent are hybrid instruments
used to gain tax advantages?" (confirmed live to be a single, unique, always
-present leaf node under "The digital economy" > "Hybrid mismatch
arrangements").

Every insert below goes through `_insert_fixture_question()`, which expands
the question's own sub-topic row first when needed - confirmed live that the
leaf is genuinely not visible (and not force-clickable either) until that
parent row is expanded. See
`pages/tpa/tpa_beps_questionnaire_page.py` for the full writeup."""
import pytest

from pages.tpa.tpa_beps_questionnaire_page import TpaBepsQuestionnairePage
from pages.wta.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA BEPS Questionnaire"

FIXTURE_QUESTION = "To what extent are hybrid instruments used to gain tax advantages?"
FIXTURE_TOPIC = "Hybrid mismatch arrangements"


def _login_and_open(case, page):
    perform_login(case, page)
    qc = TpaBepsQuestionnairePage(page)
    case.action("Navigating to /tpa/BEPSQuestionnaireCreator", kind="navigate")
    qc.goto()
    return qc


def _insert_fixture_question(case, page, qc):
    """Expand the fixture question's own sub-topic row, then click the leaf.

    Confirmed live (see pages/tpa/tpa_beps_questionnaire_page.py): the leaf
    is normally already visible, but a Start Over collapses its sub-topic,
    and a forced click on a collapsed leaf fails outright - so this expands
    only when actually needed, driving the real interaction."""
    leaf = qc.question_node(FIXTURE_QUESTION)
    if not leaf.first.is_visible():
        # Expand via the row's own +/- ICON, not its text - confirmed live
        # that the text is not the toggle affordance for a collapsed topic
        # (see TpaBepsQuestionnairePage.topic_expand_icon). This only runs
        # when the leaf is genuinely collapsed, i.e. after a Start Over.
        case.click(qc.topic_expand_icon(FIXTURE_TOPIC), f"'{FIXTURE_TOPIC}' expand icon")
        wait_for_content(leaf)
    case.click(leaf, f"'{FIXTURE_QUESTION}' tree node")
    page.wait_for_timeout(1500)


@pytest.mark.smoke
def test_bepsquestionnaire_01_page_loads_with_tree_and_toolbar(page, result):
    case = Case(
        page, "BepsQuestionnaire_01", FEATURE, "BEPS Questionnaire loads with the question tree and toolbar",
        description="The page must load with the 'Questions' heading, the rich-text editor, 'Start Over' and "
                     "'Export' all visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open BEPS Questionnaire\n2. Verify heading, editor, and toolbar controls are visible",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Verify heading, editor, and toolbar controls")
    heading_ok = case.verify_visible(qc.heading, "'Questions' heading")
    editor_ok = case.verify_visible(qc.editor, "rich-text editor")
    start_over_ok = case.verify_visible(qc.start_over_button, "'Start Over' button")
    ok = heading_ok and editor_ok and start_over_ok
    case.check("'Questions' heading, editor and 'Start Over' are visible", ok,
               expected="all visible",
               actual=f"heading={heading_ok}, editor={editor_ok}, start_over={start_over_ok}")

    actual = ("BEPS Questionnaire correctly loaded with its tree and toolbar." if ok else
              "BEPS Questionnaire did not load as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_bepsquestionnaire_02_clicking_question_grows_editor(page, result):
    case = Case(
        page, "BepsQuestionnaire_02", FEATURE, "Clicking a tree question inserts it into the editor",
        description=f"Clicking '{FIXTURE_QUESTION}' in the question tree must grow the editor's content length. "
                     "The editor is reset via Start Over first, for a real, confirmed-live reason: re-clicking a "
                     "question that is ALREADY inserted does NOT insert a duplicate (confirmed live: editor "
                     "stayed at exactly 357 chars across a repeat click), so without the reset this would be "
                     "measuring a no-op rather than the insert behavior - same reset-first rationale as the "
                     "equivalent WTA Questionnaire Creator test.",
        precondition="User is logged in and on BEPS Questionnaire.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in and open BEPS Questionnaire\n2. Reset via Start Over so the editor is empty, then "
              f"record its content length\n3. Click '{FIXTURE_QUESTION}'\n"
              "4. Verify the editor's content length increased",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Reset via Start Over so the editor starts empty, then record its length")
    # The app itself disables 'Start Over' when there is nothing to reset.
    if not qc.editor_is_empty():
        case.click(qc.start_over_button, "'Start Over' button")
        page.wait_for_timeout(500)
        case.click(qc.start_over_yes, "'Yes' (confirm Start Over)")
        page.wait_for_timeout(1500)
    before_len = len(qc.editor_html())

    case.step(3, f"Click '{FIXTURE_QUESTION}'")
    _insert_fixture_question(case, page, qc)
    page.wait_for_timeout(1500)

    case.step(4, "Verify the editor's content length increased")
    after_len = len(qc.editor_html())
    ok = after_len > before_len
    case.check("Editor content length increased after clicking the question", ok,
               expected=f"> {before_len}", actual=after_len)

    actual = (f"Clicking the question grew the editor from {before_len} to {after_len} chars." if ok else
              f"Editor content did not grow (before={before_len}, after={after_len}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsquestionnaire_03_start_over_shows_confirmation_dialog(page, result):
    case = Case(
        page, "BepsQuestionnaire_03", FEATURE, "'Start Over' shows a confirmation dialog before clearing",
        description="Clicking 'Start Over' must show a 'Confirm Start Over' dialog with 'No' and 'Yes' options, "
                     "without clearing anything yet.",
        precondition="User is logged in and on BEPS Questionnaire, with at least one question already inserted.",
        test_data=f"Question: {FIXTURE_QUESTION} (inserted if editor is empty)",
        steps=f"1. Log in and open BEPS Questionnaire\n2. Ensure the editor has content (click '{FIXTURE_QUESTION}' "
              f"if empty)\n3. Click 'Start Over'\n4. Verify the confirmation dialog with 'Yes'/'No' is shown",
    )
    qc = _login_and_open(case, page)
    case.step(2, "Ensure the editor has content so 'Start Over' is enabled")
    if qc.editor_is_empty():
        _insert_fixture_question(case, page, qc)
        page.wait_for_timeout(1500)

    case.step(3, "Click 'Start Over'")
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(500)

    case.step(4, "Verify the confirmation dialog with 'Yes'/'No' is shown")
    dialog_ok = case.verify_visible(qc.start_over_dialog, "'Confirm Start Over' dialog")
    yes_ok = case.verify_visible(qc.start_over_yes, "'Yes' button")
    no_ok = case.verify_visible(qc.start_over_no, "'No' button")
    ok = dialog_ok and yes_ok and no_ok
    case.check("'Confirm Start Over' dialog with No/Yes is shown", ok,
               expected="all visible", actual=f"dialog={dialog_ok}, yes={yes_ok}, no={no_ok}")

    # Decline, so this test does not itself destroy the shared account's content.
    if no_ok:
        case.click(qc.start_over_no, "'No' (decline Start Over)")

    actual = ("'Start Over' correctly showed a confirmation dialog with No/Yes before clearing anything." if ok else
              "The 'Confirm Start Over' dialog did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsquestionnaire_04_start_over_no_keeps_content(page, result):
    case = Case(
        page, "BepsQuestionnaire_04", FEATURE, "Clicking 'No' on Start Over keeps the editor content unchanged",
        description=f"After inserting '{FIXTURE_QUESTION}', clicking 'Start Over' then 'No' must leave the "
                     "editor's content length unchanged.",
        precondition="User is logged in and on BEPS Questionnaire.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in, open BEPS Questionnaire, click '{FIXTURE_QUESTION}'\n2. Record editor length\n"
              "3. Click 'Start Over', then 'No'\n4. Verify the editor length is unchanged",
    )
    qc = _login_and_open(case, page)
    _insert_fixture_question(case, page, qc)
    page.wait_for_timeout(1500)
    case.step(2, "Record editor length")
    before_len = len(qc.editor_html())

    case.step(3, "Click 'Start Over', then 'No'")
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(500)
    case.click(qc.start_over_no, "'No' (decline Start Over)")
    page.wait_for_timeout(500)

    case.step(4, "Verify the editor length is unchanged")
    after_len = len(qc.editor_html())
    ok = after_len == before_len
    case.check("Editor content is unchanged after declining Start Over", ok,
               expected=before_len, actual=after_len)

    actual = (f"Declining Start Over correctly left the editor unchanged ({after_len} chars)." if ok else
              f"Editor content changed unexpectedly after declining Start Over (before={before_len}, after={after_len}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsquestionnaire_05_start_over_yes_clears_editor(page, result):
    case = Case(
        page, "BepsQuestionnaire_05", FEATURE, "Confirming 'Start Over' clears the editor",
        description=f"After inserting '{FIXTURE_QUESTION}', clicking 'Start Over' then 'Yes' must empty the "
                     "editor. The fixture question is re-inserted afterward to restore this shared account's "
                     "content to a reasonable, known state, same cleanup convention as the equivalent WTA test.",
        precondition="User is logged in and on BEPS Questionnaire.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps=f"1. Log in, open BEPS Questionnaire, click '{FIXTURE_QUESTION}'\n2. Click 'Start Over', then 'Yes'\n"
              f"3. Verify the editor is empty\n4. Clean up: re-insert '{FIXTURE_QUESTION}'",
    )
    qc = _login_and_open(case, page)
    _insert_fixture_question(case, page, qc)
    page.wait_for_timeout(1500)

    case.step(2, "Click 'Start Over', then 'Yes'")
    case.click(qc.start_over_button, "'Start Over' button")
    page.wait_for_timeout(500)
    case.click(qc.start_over_yes, "'Yes' (confirm Start Over)")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the editor is empty")
    empty_ok = qc.editor_is_empty()
    ok = empty_ok
    case.check("Editor is empty after confirming Start Over", ok,
               expected="empty", actual=qc.editor_html()[:120])

    case.step(4, f"Clean up: re-insert '{FIXTURE_QUESTION}'")
    _insert_fixture_question(case, page, qc)
    page.wait_for_timeout(1000)

    actual = ("Confirming 'Start Over' correctly cleared the editor." if ok else
              f"The editor still had content after confirming Start Over (html={qc.editor_html()[:200]!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsquestionnaire_06_add_to_project_absent_when_empty_present_after_question(page, result):
    case = Case(
        page, "BepsQuestionnaire_06", FEATURE, "'Add to Project' is absent on an empty editor, present once content exists",
        description="Same confirmed-live gotcha as WTA's own Questionnaire Creator: 'Add to Project' is NOT "
                     "rendered at all while the editor is empty, only appearing once at least one question has "
                     "been inserted.",
        precondition="User is logged in and on BEPS Questionnaire, with the editor emptied via Start Over.",
        test_data=f"Question: {FIXTURE_QUESTION}",
        steps="1. Log in, open BEPS Questionnaire, empty the editor via Start Over\n"
              "2. Verify 'Add to Project' is absent\n"
              f"3. Click '{FIXTURE_QUESTION}'\n4. Verify 'Add to Project' is now visible",
    )
    qc = _login_and_open(case, page)
    case.step(1, "Empty the editor via Start Over, if needed")
    if not qc.editor_is_empty():
        case.click(qc.start_over_button, "'Start Over' button")
        page.wait_for_timeout(500)
        case.click(qc.start_over_yes, "'Yes' (confirm Start Over)")
        page.wait_for_timeout(1500)

    case.step(2, "Verify 'Add to Project' is absent")
    absent_ok = qc.add_to_project_button.count() == 0
    case.check("'Add to Project' is not rendered on an empty editor", absent_ok,
               expected="count == 0", actual=qc.add_to_project_button.count())

    case.step(3, f"Click '{FIXTURE_QUESTION}'")
    _insert_fixture_question(case, page, qc)
    page.wait_for_timeout(1500)

    case.step(4, "Verify 'Add to Project' is now visible")
    present_ok = case.verify_visible(qc.add_to_project_button, "'Add to Project' button")
    ok = absent_ok and present_ok
    case.check("'Add to Project' appears once the editor has content", present_ok,
               expected="visible", actual=present_ok)

    actual = ("'Add to Project' correctly appeared only once the editor had content." if ok else
              f"'Add to Project' visibility did not match expectations (absent_when_empty={absent_ok}, "
              f"present_after_question={present_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_bepsquestionnaire_07_direct_deep_link_works(page, result):
    case = Case(
        page, "BepsQuestionnaire_07", FEATURE, "A direct deep link to /tpa/BEPSQuestionnaireCreator loads the page",
        description="Navigating straight to /tpa/BEPSQuestionnaireCreator must load with the 'Questions' heading "
                     "visible - same deep-link support as every other TPA page, unlike WTA's own Tools pages.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/BEPSQuestionnaireCreator\n3. Verify the 'Questions' heading renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/BEPSQuestionnaireCreator")
    qc = TpaBepsQuestionnairePage(page)
    qc.goto()
    case.step(3, "Verify the 'Questions' heading renders")
    ok = case.verify_visible(qc.heading, "'Questions' heading")
    case.check("Direct deep link to /tpa/BEPSQuestionnaireCreator loads with the 'Questions' heading", ok,
                expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/BEPSQuestionnaireCreator correctly loaded." if ok else
              "The direct deep link to /tpa/BEPSQuestionnaireCreator did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
