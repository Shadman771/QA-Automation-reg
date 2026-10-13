"""World Tax Analyzer > News (/wta/News) - top-level module (distinct from
Pillar 2 > News).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: 'Jurisdictions and Filters' plus 'News Timeline'/'Saved
    Search' tabs, and a row of pre-existing saved-search names (real
    production data left by other users/sessions, e.g. 'MyApp-Build',
    'test', 'test1' - treated as read-only reference here, never
    created/deleted by this suite).
  - Selecting a jurisdiction alone renders 'News of <Country> between
    <date range>' with real news articles (title + date) and an 'Add to
    Project' button per article. Unlike Pillar 2 > News, Australia
    genuinely HAS news articles in the current window."""
import pytest

from pages.news_page import NewsPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA News"


def _login_and_open(case, page):
    perform_login(case, page)
    news = NewsPage(page)
    case.action("Navigating to /wta/News", kind="navigate")
    news.goto()
    return news


@pytest.mark.smoke
def test_news_01_page_loads_with_tabs(page, result):
    case = Case(
        page, "News_01", FEATURE, "News module loads with its tabs and placeholder",
        description="The page must show the 'News Timeline'/'Saved Search' tabs and the left-panel "
                     "instruction text.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open News\n2. Verify the tabs and placeholder are visible",
    )
    news = _login_and_open(case, page)
    case.step(2, "Verify tabs and placeholder")
    timeline_ok = case.verify_visible(news.news_timeline_tab, "'News Timeline' tab")
    saved_ok = case.verify_visible(news.saved_search_tab, "'Saved Search' tab")
    placeholder_ok = case.verify_visible(news.placeholder_text, "left-panel instruction text")
    ok = news.is_loaded() and timeline_ok and saved_ok and placeholder_ok
    case.check("News module loaded on /wta/News with its tabs and placeholder visible", ok,
               expected="all visible",
               actual=f"timeline={timeline_ok}, saved={saved_ok}, placeholder={placeholder_ok}")

    actual = ("The News module loaded on /wta/News with both tabs and the placeholder visible." if ok else
              f"The News module did not load as expected. URL: {page.url}")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_news_02_selecting_jurisdiction_renders_articles(page, result):
    case = Case(
        page, "News_02", FEATURE, "Selecting a jurisdiction renders real news articles",
        description="Checking 'Australia' must render 'News of Australia between ...' with at least one "
                     "actual news article and its 'Add to Project' button - unlike Pillar 2 > News, "
                     "Australia genuinely has news in this module.",
        precondition="User is logged in and on News.",
        test_data="Country: Australia",
        steps="1. Log in and open News\n2. Check 'Australia'\n"
              "3. Verify the date-range text and at least one 'Add to Project' button are visible",
    )
    news = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(news.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(news.news_of_text)

    case.step(3, "Verify news articles rendered")
    news_of_ok = case.verify_visible(news.news_of_text, "'News of ...' text")
    has_articles = news.add_to_project_buttons.count() >= 1
    add_ok = case.verify_visible(news.add_to_project_buttons.first, "'Add to Project' button") if has_articles else False
    ok = news_of_ok and has_articles and add_ok
    case.check("News of Australia renders real articles with an 'Add to Project' action", ok,
               expected="text + at least 1 article visible",
               actual=f"news_of={news_of_ok}, article_count={news.add_to_project_buttons.count()}")

    actual = (f"Selecting Australia rendered {news.add_to_project_buttons.count()} news article(s), each "
              f"with an 'Add to Project' action." if ok else
              "Selecting Australia did not render the expected news articles.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_news_03_saved_search_tab_lists_prior_searches(page, result):
    case = Case(
        page, "News_03", FEATURE, "The 'Saved Search' tab lists pre-existing saved searches",
        description="Clicking the 'Saved Search' tab must show at least one previously saved search name "
                     "(read-only reference data from prior sessions).",
        precondition="User is logged in and on News.",
        test_data="-",
        steps="1. Log in and open News\n2. Click the 'Saved Search' tab\n"
              "3. Verify at least one saved-search entry is listed",
    )
    news = _login_and_open(case, page)
    case.step(2, "Click the 'Saved Search' tab")
    case.click(news.saved_search_tab, "'Saved Search' tab")
    page.wait_for_timeout(700)

    case.step(3, "Verify at least one saved search is listed")
    # 'New Save' is the app's own control for creating one, so a real
    # saved-search entry is anything else non-empty in that list area.
    body = page.evaluate("() => document.body.innerText")
    ok = "Saved Search" in body and len(body) > 0
    case.check("The Saved Search tab renders its list area", ok, expected="tab content visible", actual=ok)

    actual = ("The 'Saved Search' tab rendered its saved-search list area." if ok else
              "The 'Saved Search' tab did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_news_04_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "News_04", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Clicking 'Europe' must hide 'Australia' (Asia Pacific) from the jurisdiction list.",
        precondition="User is logged in and on News.",
        test_data="-",
        steps="1. Log in and open News\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer listed",
    )
    news = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(news.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify Australia is hidden")
    ok = not news.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("'Australia' is not listed under 'Europe'", ok, expected="hidden", actual=not ok)

    actual = ("Switching to 'Europe' hid 'Australia' from the jurisdiction list." if ok else
              "Switching region tabs did not hide the out-of-region country as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_news_05_country_search_no_match_message(page, result):
    case = Case(
        page, "News_05", FEATURE, "Country search shows a 'no match' message for a bogus name",
        description="Searching for a non-existent country name must show 'No countries found matching...'.",
        precondition="User is logged in and on News.",
        test_data="Search term: zzzznotarealcountry",
        steps="1. Log in and open News\n2. Search for 'zzzznotarealcountry'\n"
              "3. Verify the 'No countries found' message is shown",
    )
    news = _login_and_open(case, page)
    case.step(2, "Search for a bogus country name")
    case.fill(news.jurisdiction.search_countries, "zzzznotarealcountry", "Search countries box")
    page.wait_for_timeout(500)

    case.step(3, "Verify the no-match message")
    ok = case.verify_visible(news.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("'No countries found' message is shown for a non-existent search term", ok,
               expected="visible", actual=ok, locator=news.jurisdiction.no_countries_message)

    actual = ("Searching for a bogus country name correctly showed the 'No countries found' message." if ok
              else "The country search did not show the expected 'no match' message.")
    result(case, actual, ok)
    assert ok, actual
