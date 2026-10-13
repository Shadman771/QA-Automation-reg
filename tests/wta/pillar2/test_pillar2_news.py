"""Pillar 2 > News (/wta/PillarTwoNews).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: 'Jurisdictions and Filters' plus 'News Timeline'/'Saved
    Search' tabs above the jurisdiction list.
  - Selecting a jurisdiction alone renders 'Pillar Two news of <Country>
    between <date range>' with 'Save Searches' and 'Start Over' controls.
  - For Australia in the current date window the app genuinely shows
    'No News Found' - confirmed as a real empty state, not an automation
    bug, so it is asserted as the expected result rather than worked
    around."""
import pytest

from pages.pillar2_news_page import PillarTwoNewsPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 News"


def _login_and_open(case, page):
    perform_login(case, page)
    news = PillarTwoNewsPage(page)
    case.action("Navigating to /wta/PillarTwoNews", kind="navigate")
    news.goto()
    return news


@pytest.mark.smoke
def test_p2news_01_page_loads_with_tabs_and_placeholder(page, result):
    case = Case(
        page, "P2News_01", FEATURE, "Pillar 2 > News loads with its tabs and placeholder",
        description="The page must show the 'News Timeline' and 'Saved Search' tabs plus the left-panel "
                     "instruction text.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > News\n2. Verify the tabs and placeholder are visible",
    )
    news = _login_and_open(case, page)
    case.step(2, "Verify tabs and placeholder")
    timeline_ok = case.verify_visible(news.news_timeline_tab, "'News Timeline' tab")
    saved_ok = case.verify_visible(news.saved_search_tab, "'Saved Search' tab")
    placeholder_ok = case.verify_visible(news.placeholder_text, "left-panel instruction text")
    ok = timeline_ok and saved_ok and placeholder_ok
    case.check("'News Timeline'/'Saved Search' tabs and the placeholder are visible", ok,
               expected="all visible",
               actual=f"timeline={timeline_ok}, saved={saved_ok}, placeholder={placeholder_ok}")

    actual = ("Pillar 2 > News loaded with both tabs and the placeholder visible." if ok else
              "Pillar 2 > News did not show the expected tabs/placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2news_02_selecting_jurisdiction_renders_news_view(page, result):
    case = Case(
        page, "P2News_02", FEATURE, "Selecting a jurisdiction renders the news search view",
        description="Checking 'Australia' must render 'Pillar Two news of Australia between ...' with "
                     "'Save Searches' and 'Start Over' controls. The app genuinely shows 'No News Found' "
                     "for Australia in the current date window - a real empty state, asserted as expected.",
        precondition="User is logged in and on Pillar 2 > News.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > News\n2. Check 'Australia'\n"
              "3. Verify the news search view (date-range text, Save Searches, Start Over) is rendered",
    )
    news = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(news.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(news.news_of_text)

    case.step(3, "Verify the news search view rendered")
    news_of_ok = case.verify_visible(news.news_of_text, "'Pillar Two news of ...' text")
    save_ok = case.verify_visible(news.save_searches_button, "'Save Searches' button")
    start_over_ok = case.verify_visible(news.start_over_button, "'Start Over' button")
    ok = news_of_ok and save_ok and start_over_ok
    case.check("News search view (date range text + Save Searches + Start Over) is visible", ok,
               expected="all visible",
               actual=f"news_of={news_of_ok}, save={save_ok}, start_over={start_over_ok}")

    actual = ("Selecting Australia rendered the Pillar Two news search view with its date range text and "
              "Save Searches/Start Over controls." if ok else
              "Selecting a jurisdiction did not render the expected news search view.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2news_03_no_news_found_is_a_genuine_empty_state(page, result):
    case = Case(
        page, "P2News_03", FEATURE, "Australia genuinely has no Pillar Two news in the current window",
        description="For Australia, the current date window must show a 'No News Found' empty state - "
                     "this is real application behaviour (no Pillar Two news items exist for Australia "
                     "right now), documented here rather than treated as a failure.",
        precondition="User is logged in, Australia selected on Pillar 2 > News.",
        test_data="Country: Australia",
        steps="1. Log in, open Pillar 2 > News, select Australia\n"
              "2. Verify the 'No News Found' message is shown",
    )
    news = _login_and_open(case, page)
    news.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(news.no_news_found)

    case.step(2, "Verify the empty state")
    ok = case.verify_visible(news.no_news_found, "'No News Found' message")
    case.check("'No News Found' is shown for Australia in the current window", ok,
               expected="visible (genuine empty state)", actual=ok, locator=news.no_news_found)

    actual = ("The app correctly showed 'No News Found' for Australia - a genuine empty state confirmed "
              "against the live application, not missing functionality." if ok else
              "Expected the genuine 'No News Found' empty state for Australia but it was not shown "
              "(the underlying news data set may have changed since this was last verified).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2news_04_start_over_resets_selection(page, result):
    case = Case(
        page, "P2News_04", FEATURE, "'Start Over', confirmed, resets the jurisdiction selection",
        description="After selecting Australia, clicking 'Start Over' opens a 'Confirm Start Over' modal "
                     "('Start over action will reset all of your selection(s). Do you want to proceed?'); "
                     "confirming with 'Yes' must then uncheck Australia and restore the left-panel "
                     "placeholder.",
        precondition="User is logged in, Australia selected on Pillar 2 > News.",
        test_data="Country: Australia",
        steps="1. Log in, open Pillar 2 > News, select Australia\n2. Click 'Start Over'\n"
              "3. Verify the confirmation modal appears and click 'Yes'\n"
              "4. Verify Australia is unchecked and the placeholder returns",
    )
    news = _login_and_open(case, page)
    news.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(news.start_over_button)

    case.step(2, "Click 'Start Over'")
    case.click(news.start_over_button, "'Start Over' button")
    wait_for_content(news.confirm_start_over_heading)

    case.step(3, "Confirm the reset in the modal")
    modal_ok = case.verify_visible(news.confirm_start_over_heading, "'Confirm Start Over' modal")
    case.click(news.confirm_yes_button, "'Yes' (confirm Start Over)")
    wait_for_content(news.placeholder_text)

    case.step(4, "Verify the selection was reset")
    australia_unchecked = not news.jurisdiction.is_country_checked("Australia")
    placeholder_back = news.placeholder_text.is_visible()
    ok = modal_ok and australia_unchecked and placeholder_back
    case.check("Confirming 'Start Over' unchecks Australia and restores the placeholder", ok,
               expected="modal shown, then unchecked + placeholder visible",
               actual=f"modal={modal_ok}, unchecked={australia_unchecked}, placeholder={placeholder_back}")

    actual = ("Clicking 'Start Over' opened the confirmation modal, and confirming with 'Yes' reset the "
              "jurisdiction selection and restored the placeholder." if ok else
              "'Start Over' (with confirmation) did not fully reset the jurisdiction selection.")
    result(case, actual, ok)
    assert ok, actual
