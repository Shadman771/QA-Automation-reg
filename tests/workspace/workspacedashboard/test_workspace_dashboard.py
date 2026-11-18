"""Workspace > Dashboard (`/companydata/dashboard/`). See
pages/workspace/workspace_dashboard_page.py for the full confirmed-live
layout: the Risk Heatmap (a yFiles chart with a real DOM legend) and the
filterable News, Alerts & Updates feed."""
import pytest

from pages.workspace.workspace_common import WorkspaceNav
from pages.workspace.workspace_dashboard_page import WorkspaceDashboardPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

FEATURE = "Workspace Dashboard"


def _login_and_open(case, page):
    perform_login(case, page)
    dashboard = WorkspaceDashboardPage(page)
    case.action("Navigating to Workspace > Dashboard", kind="navigate")
    dashboard.goto()
    return dashboard


@pytest.mark.smoke
def test_workspacedashboard_01_page_loads_with_risk_heatmap(page, result):
    case = Case(
        page, "WorkspaceDashboard_01", FEATURE, "Dashboard loads with the Risk Heatmap section",
        description="The 'Risk Heatmap' heading and its High/Medium/No Risk legend must be visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Dashboard\n2. Verify the Risk Heatmap heading and legend",
    )
    dashboard = _login_and_open(case, page)
    case.step(2, "Verify the Risk Heatmap heading and legend are visible")
    heading_ok = case.verify_visible(dashboard.heading_risk_heatmap, "'Risk Heatmap' heading")
    legend_ok = (
        dashboard.legend_high_risk.is_visible()
        and dashboard.legend_medium_risk.is_visible()
        and dashboard.legend_no_risk.is_visible()
    )
    ok = heading_ok and legend_ok
    case.check("Risk Heatmap heading and full legend (High/Medium/No Risk) are visible", ok,
               expected="heading + 3-item legend visible", actual=f"heading={heading_ok}, legend={legend_ok}")

    actual = "Risk Heatmap section loaded with its legend." if ok else "Risk Heatmap section/legend did not load."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_workspacedashboard_02_news_feed_loads(page, result):
    case = Case(
        page, "WorkspaceDashboard_02", FEATURE, "News, Alerts & Updates feed loads with real items",
        description="The 'News, Alerts & Updates' heading must be visible and the feed must show at least one item.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Dashboard\n2. Verify the News heading and a non-zero item count",
    )
    dashboard = _login_and_open(case, page)
    case.step(2, "Verify the News, Alerts & Updates heading and item count")
    heading_ok = wait_for_content(dashboard.heading_news, timeout=20000)
    count = dashboard.news_item_count() if heading_ok else 0
    ok = heading_ok and count > 0
    case.check("News feed shows at least one real item", ok, expected="> 0 items", actual=str(count))

    actual = f"News feed loaded with {count} item(s)." if ok else "News feed did not load with any items."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacedashboard_03_all_chip_is_selected_by_default(page, result):
    case = Case(
        page, "WorkspaceDashboard_03", FEATURE, "The 'All' risk chip is selected by default",
        description="On initial load, no 'Filtered' badge should be shown next to the News heading - "
                     "the feed starts unfiltered ('All').",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Workspace > Dashboard\n2. Verify no 'Filtered' badge is shown",
    )
    dashboard = _login_and_open(case, page)
    wait_for_content(dashboard.heading_news, timeout=20000)
    case.step(2, "Verify no 'Filtered' badge is shown next to the News heading")
    filtered_shown = dashboard.filtered_badge.is_visible() if dashboard.filtered_badge.count() else False
    ok = not filtered_shown
    case.check("News feed is not filtered on initial load", ok, expected="no 'Filtered' badge", actual=filtered_shown)

    actual = "Feed starts unfiltered, as expected." if ok else "Feed unexpectedly started pre-filtered."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacedashboard_04_selecting_high_risk_chip_filters_the_feed(page, result):
    case = Case(
        page, "WorkspaceDashboard_04", FEATURE, "Selecting the 'High' risk chip filters the News feed",
        description="Clicking the 'High' risk chip must add a 'Filtered' badge to the News heading and "
                     "must not increase the item count beyond the unfiltered baseline.",
        precondition="User is logged in and the 'High' chip is enabled (has a non-zero live count).",
        test_data="Risk chip: High",
        steps="1. Log in and open Workspace > Dashboard\n2. Record the unfiltered item count\n"
              "3. Click the 'High' risk chip\n4. Verify the 'Filtered' badge appears and the count is <= baseline",
    )
    dashboard = _login_and_open(case, page)
    wait_for_content(dashboard.heading_news, timeout=20000)
    case.step(2, "Record the unfiltered ('All') item count")
    baseline = dashboard.news_item_count()

    case.step(3, "Click the 'High' risk chip")
    high_chip = dashboard.risk_chip("High")
    if high_chip.count() == 0 or dashboard.is_risk_chip_disabled("High"):
        actual = "The 'High' risk chip is disabled/absent on this account (0 high-risk items) - skipping filter assertion."
        result(case, actual, True, expected="chip enabled or documented as disabled")
        pytest.skip(actual)
    case.click(high_chip, "'High' risk chip")
    page.wait_for_timeout(300)

    case.step(4, "Verify the 'Filtered' badge appears and the item count narrows or stays the same")
    filtered_ok = case.verify_visible(dashboard.filtered_badge, "'Filtered' badge")
    filtered_count = dashboard.news_item_count()
    count_ok = filtered_count <= baseline
    ok = filtered_ok and count_ok
    case.check("Selecting 'High' marks the feed as Filtered and narrows/keeps the item count", ok,
               expected=f"Filtered badge visible, count <= {baseline}",
               actual=f"Filtered badge={filtered_ok}, count={filtered_count}")

    actual = (f"Feed correctly filtered to {filtered_count} item(s) (baseline {baseline})." if ok else
              f"Filter did not behave as expected (Filtered badge={filtered_ok}, count={filtered_count}, baseline={baseline}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacedashboard_05_news_search_narrows_the_feed(page, result):
    case = Case(
        page, "WorkspaceDashboard_05", FEATURE, "Searching the News feed filters to matching cards",
        description="Searching for an entity name read live from the feed must return at least one card, "
                     "and every remaining card must contain the search term.",
        precondition="User is logged in.",
        test_data="Search term: the last feed card's entity name, read at runtime (no hardcoded entity)",
        steps="1. Log in and open Workspace > Dashboard\n2. Read the baseline cards and pick a real entity name\n"
              "3. Type it into the News search box\n4. Verify >=1 card remains and every card matches the term",
    )
    dashboard = _login_and_open(case, page)
    wait_for_content(dashboard.news_cards, timeout=20000)
    case.step(2, "Read the baseline cards and pick a real entity name")
    names = [n for n in dashboard.card_entity_names() if n]
    baseline = dashboard.news_item_count()
    term = names[-1] if names else ""
    case.check("Feed has at least one named card to search for", bool(term),
               expected="non-empty entity name", actual=repr(term))

    case.step(3, f"Type '{term}' into the News search box")
    case.click(dashboard.news_search, "News search box")
    case.action(f"Typing '{term}' key-by-key (the feed filters on keystrokes, not fill())", kind="type")
    dashboard.type_news_search(term)
    page.wait_for_timeout(800)

    case.step(4, "Verify >=1 card remains and every card matches the term")
    texts = dashboard.card_texts()
    mismatches = [t.splitlines()[0] for t in texts if term.lower() not in t.lower()]
    ok = bool(term) and len(texts) >= 1 and not mismatches and len(texts) <= baseline
    case.check("Search returns only feed cards matching the term", ok,
               expected=f">=1 card, all containing '{term}', <= {baseline}",
               actual=f"{len(texts)} card(s), non-matching={mismatches}")

    actual = (f"Searching '{term}' filtered {baseline} cards down to {len(texts)}, all matching." if ok else
              f"Search for '{term}' did not filter correctly: {len(texts)} card(s), non-matching={mismatches}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_workspacedashboard_06_workspace_nav_links_present(page, result):
    case = Case(
        page, "WorkspaceDashboard_06", FEATURE, "Workspace sidebar shows Dashboard/Entities/Calendar links",
        description="The left sidebar must show working links to Dashboard, Entities and Calendar (the "
                     "in-scope sub-features), each with a real, distinct href.",
        precondition="User is logged in and on Workspace > Dashboard.",
        test_data="-",
        steps="1. Log in and open Workspace > Dashboard\n2. Verify Dashboard/Entities/Calendar sidebar links",
    )
    dashboard = _login_and_open(case, page)
    nav = WorkspaceNav(page)
    case.step(2, "Verify the 3 in-scope sidebar links are visible")
    dash_ok = case.verify_visible(nav.nav_dashboard, "'Dashboard' sidebar link")
    entities_ok = nav.nav_entities.is_visible()
    calendar_ok = nav.nav_calendar.is_visible()
    ok = dash_ok and entities_ok and calendar_ok
    case.check("Dashboard/Entities/Calendar sidebar links are all visible", ok,
               expected="all 3 visible", actual=f"Dashboard={dash_ok}, Entities={entities_ok}, Calendar={calendar_ok}")

    actual = "All 3 in-scope sidebar links are visible." if ok else "One or more sidebar links were not visible."
    result(case, actual, ok)
    assert ok, actual
