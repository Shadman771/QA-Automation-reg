"""TPA > Commentary (/tpa/Commentary). See pages/tpa/tpa_commentary_page.py
for the full confirmed-live layout and the news-modal Escape-key gotcha."""
import pytest

from pages.tpa.tpa_commentary_page import TpaCommentaryPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "TPA Commentary"


def _login_and_open(case, page):
    perform_login(case, page)
    commentary = TpaCommentaryPage(page)
    case.action("Navigating to /tpa/Commentary", kind="navigate")
    commentary.goto()
    return commentary


@pytest.mark.smoke
def test_tpacommentary_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "TpaCommentary_01", FEATURE, "Commentary loads with the jurisdiction placeholder",
        description="The page must load with the 'Use the left panel to choose jurisdiction.' placeholder "
                     "shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Commentary\n2. Verify the placeholder text is visible",
    )
    commentary = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(commentary.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("Commentary loaded with the placeholder visible." if ok else
              "Commentary did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpacommentary_02_jurisdiction_renders_commentary_article(page, result):
    case = Case(
        page, "TpaCommentary_02", FEATURE, "Selecting a jurisdiction renders its commentary article",
        description="Checking 'Bangladesh' must render a 'Commentary on Bangladesh' heading, a "
                     "'last updated' line, and a non-empty article body.",
        precondition="User is logged in and on Commentary.",
        test_data="Country: Bangladesh",
        steps="1. Log in and open Commentary\n2. Select 'Bangladesh'\n"
              "3. Verify the heading, 'last updated' line and article body",
    )
    commentary = _login_and_open(case, page)
    case.step(2, "Select Bangladesh")
    case.click(commentary.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify the heading, 'last updated' line and article body")
    heading_ok = wait_for_content(commentary.commentary_heading, timeout=15000)
    heading_text = commentary.heading_text() if heading_ok else ""
    last_updated_ok = commentary.last_updated_text.count() > 0
    body_text = commentary.article_body_text()
    body_ok = len(body_text) > 500

    ok = heading_ok and "Bangladesh" in heading_text and last_updated_ok and body_ok
    case.check("Commentary article renders for the selected country", ok,
               expected="heading contains 'Bangladesh', 'last updated' present, body length > 500",
               actual=f"heading={heading_text!r}, last_updated_ok={last_updated_ok}, body_len={len(body_text)}")

    actual = (f"Selecting Bangladesh correctly rendered its commentary article ({len(body_text)} chars)."
              if ok else f"The commentary article did not render as expected (heading_ok={heading_ok}, "
              f"heading_text={heading_text!r}, last_updated_ok={last_updated_ok}, body_len={len(body_text)}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpacommentary_03_news_modal_opens_and_closes_via_ok(page, result):
    case = Case(
        page, "TpaCommentary_03", FEATURE, "The 'N news since the update' button opens a Related News modal, closed via OK",
        description="Clicking the news-count button must open an '.rs-modal-wrapper' titled 'Related News'. "
                     "NOTE (confirmed live - see pages/tpa/tpa_commentary_page.py): pressing Escape does NOT "
                     "close this modal; it must be closed via its own 'OK' button, or its backdrop silently "
                     "blocks every subsequent click on the page.",
        precondition="User is logged in, on Commentary, with Bangladesh selected.",
        test_data="Country: Bangladesh",
        steps="1. Log in, open Commentary, select Bangladesh\n2. Click the news-count button\n"
              "3. Verify the 'Related News' modal opens\n4. Close it via 'OK' and verify it closes",
    )
    commentary = _login_and_open(case, page)
    case.step(2, "Select Bangladesh, then click the news-count button")
    case.click(commentary.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    wait_for_content(commentary.commentary_heading, timeout=15000)
    # The news-count button renders asynchronously a beat after the
    # heading - same async-render race already documented elsewhere in
    # this project (National Rules' Commentary buttons, News' Add-to-
    # Project buttons) - wait for it directly rather than racing a fixed
    # sleep against the heading's own render.
    has_news_button = wait_for_content(commentary.news_since_button, timeout=10000)
    if has_news_button:
        case.click(commentary.news_since_button.first, "news-count button")
        page.wait_for_timeout(1000)

    case.step(3, "Verify the 'Related News' modal opens")
    modal_ok = has_news_button and case.verify_visible(commentary.news_modal_heading, "'Related News' modal heading")

    case.step(4, "Close it via 'OK' and verify it closes")
    closed_ok = False
    if modal_ok:
        case.click(commentary.news_modal_ok_button, "'OK' button")
        page.wait_for_timeout(600)
        closed_ok = commentary.news_modal_heading.count() == 0 or not commentary.news_modal_heading.is_visible()

    ok = has_news_button and modal_ok and closed_ok
    case.check("The Related News modal opened and was closed via its OK button", ok,
               expected="has_news_button=True, modal_ok=True, closed_ok=True",
               actual=f"has_news_button={has_news_button}, modal_ok={modal_ok}, closed_ok={closed_ok}")

    actual = ("The 'Related News' modal correctly opened on click and closed via its own 'OK' button." if ok else
              f"The news modal did not behave as expected (has_news_button={has_news_button}, "
              f"modal_ok={modal_ok}, closed_ok={closed_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpacommentary_04_switching_country_updates_the_article(page, result):
    case = Case(
        page, "TpaCommentary_04", FEATURE, "Switching the selected country updates the commentary article",
        description="Selecting 'Bangladesh' then switching to 'China' must change the heading from "
                     "'Commentary on Bangladesh' to 'Commentary on China'.",
        precondition="User is logged in and on Commentary.",
        test_data="Countries: Bangladesh -> China",
        steps="1. Log in and open Commentary\n2. Select 'Bangladesh', note the heading\n"
              "3. Select 'China'\n4. Verify the heading updates to 'Commentary on China'",
    )
    commentary = _login_and_open(case, page)
    case.step(2, "Select Bangladesh, note the heading")
    case.click(commentary.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    wait_for_content(commentary.commentary_heading, timeout=15000)
    first_heading = commentary.heading_text()

    case.step(3, "Select China")
    case.click(commentary.jurisdiction.country_checkbox("China"), "'China' checkbox")
    page.wait_for_timeout(500)
    wait_for_content(commentary.commentary_heading, timeout=15000)

    case.step(4, "Verify the heading updates to 'Commentary on China'")
    second_heading = commentary.heading_text()
    ok = "Bangladesh" in first_heading and "China" in second_heading and first_heading != second_heading
    case.check("The commentary heading updated after switching countries", ok,
               expected="first contains 'Bangladesh', second contains 'China'",
               actual=f"first={first_heading!r}, second={second_heading!r}")

    actual = (f"Switching from Bangladesh to China correctly updated the heading to {second_heading!r}." if ok
              else f"The heading did not update as expected (first={first_heading!r}, second={second_heading!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpacommentary_05_export_control_is_present(page, result):
    case = Case(
        page, "TpaCommentary_05", FEATURE, "The 'Export' control is present once a commentary article is shown",
        description="After selecting Bangladesh, an 'Export' control must be visible on the page.",
        precondition="User is logged in and on Commentary.",
        test_data="Country: Bangladesh",
        steps="1. Log in, open Commentary, select Bangladesh\n2. Verify the 'Export' control is visible",
    )
    commentary = _login_and_open(case, page)
    case.step(1, "Select Bangladesh")
    case.click(commentary.jurisdiction.country_checkbox("Bangladesh"), "'Bangladesh' checkbox")
    wait_for_content(commentary.commentary_heading, timeout=15000)

    case.step(2, "Verify the 'Export' control is visible")
    ok = case.verify_visible(commentary.export_control, "'Export' control")
    case.check("The 'Export' control is visible once the article renders", ok, expected=True, actual=ok)

    actual = "The 'Export' control was correctly visible once the commentary article rendered." if ok else \
             "The 'Export' control was not visible after the commentary article rendered."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_tpacommentary_06_a_second_real_country_also_renders(page, result):
    case = Case(
        page, "TpaCommentary_06", FEATURE, "A second real country (Singapore) also renders a commentary article",
        description="Checking 'Singapore' (an independent country, not reusing Bangladesh/China already "
                     "covered) must also render a 'Commentary on Singapore' heading and a non-empty body - "
                     "confirming this isn't a Bangladesh-specific fixture.",
        precondition="User is logged in and on Commentary.",
        test_data="Country: Singapore",
        steps="1. Log in and open Commentary\n2. Select 'Singapore'\n"
              "3. Verify the heading and a non-empty article body",
    )
    commentary = _login_and_open(case, page)
    case.step(2, "Select Singapore")
    case.click(commentary.jurisdiction.country_checkbox("Singapore"), "'Singapore' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify the heading and a non-empty article body")
    heading_ok = wait_for_content(commentary.commentary_heading, timeout=15000)
    heading_text = commentary.heading_text() if heading_ok else ""
    body_text = commentary.article_body_text()
    ok = heading_ok and "Singapore" in heading_text and len(body_text) > 300

    case.check("Commentary renders for a second, independent country", ok,
               expected="heading contains 'Singapore', body length > 300",
               actual=f"heading={heading_text!r}, body_len={len(body_text)}")

    actual = (f"Selecting Singapore correctly rendered its own commentary article ({len(body_text)} chars)."
              if ok else f"Singapore's commentary did not render as expected (heading_ok={heading_ok}, "
              f"heading_text={heading_text!r}, body_len={len(body_text)}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_tpacommentary_07_direct_deep_link_loads_the_page(page, result):
    case = Case(
        page, "TpaCommentary_07", FEATURE, "A direct deep link to /tpa/Commentary loads the page correctly",
        description="A full-page `goto()` straight to /tpa/Commentary must land on the Commentary page with "
                     "the jurisdiction placeholder shown, unlike WTA's own Tools pages which redirect away.",
        precondition="User is logged in.",
        test_data="Direct URL: /tpa/Commentary",
        steps="1. Log in\n2. Navigate directly to /tpa/Commentary\n3. Verify the URL and placeholder",
    )
    perform_login(case, page)
    commentary = TpaCommentaryPage(page)
    case.step(2, "Navigate directly to /tpa/Commentary")
    case.action("Navigating directly to /tpa/Commentary", kind="navigate")
    commentary.goto()

    case.step(3, "Verify the URL and placeholder")
    url_ok = "/tpa/Commentary" in page.url
    placeholder_ok = case.verify_visible(commentary.placeholder_text, "left-panel instruction text")
    ok = url_ok and placeholder_ok
    case.check("Direct deep link to /tpa/Commentary loaded the real page", ok,
               expected="url_ok=True, placeholder_ok=True",
               actual=f"url={page.url}, url_ok={url_ok}, placeholder_ok={placeholder_ok}")

    actual = (f"A direct deep link correctly loaded Commentary at {page.url}." if ok else
              f"The direct deep link did not load Commentary as expected (url={page.url}, "
              f"placeholder_ok={placeholder_ok}).")
    result(case, actual, ok)
    assert ok, actual
