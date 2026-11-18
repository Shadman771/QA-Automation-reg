"""Workspace > Dashboard - risk chips, feed search, panel and heatmap
controls, navigation and cross-module data integrity. All read-only
(the Dashboard itself has no create/edit/delete - confirmed live; its data
comes from Entities and Calendar, whose CRUD tests cover the Dashboard
side in WorkspaceEntities_21 and WorkspaceCalendar_17)."""
import re

import pytest

from pages.workspace.workspace_calendar_page import WorkspaceCalendarPage
from pages.workspace.workspace_common import WorkspaceNav
from pages.workspace.workspace_entities_page import WorkspaceEntitiesPage
from tests.workspace._flows import finish, mk, open_dashboard
from utils.wait import wait_for_content

FEATURE = "Workspace Dashboard"


@pytest.mark.regression
def test_workspacedashboard_07_risk_counts_add_up_to_all(page, result):
    case = mk(page, "WorkspaceDashboard_07", FEATURE, "High + Medium + No Risk counts add up to 'All'",
              "Data integrity: the three risk chips' live counts must sum to the 'All' chip's count.",
              "1. Open Dashboard\n2. Read the four chip counts\n3. Verify High + Medium + No Risk == All", "-")
    dash = open_dashboard(case, page)
    c = dash.chip_counts()
    total = c.get("High", 0) + c.get("Medium", 0) + c.get("No Risk", 0)
    ok = set(c) == {"All", "High", "Medium", "No Risk"} and total == c["All"] and c["All"] > 0
    case.check("High + Medium + No Risk equals All", ok, expected=c.get("All"), actual=f"{total} from {c}",
               locator=dash.risk_chips.first)
    finish(case, result, ok, f"Risk counts are consistent: {c}.", f"Risk counts inconsistent: {c} (sum {total}).")


@pytest.mark.regression
def test_workspacedashboard_08_zero_count_chips_are_disabled_others_enabled(page, result):
    case = mk(page, "WorkspaceDashboard_08", FEATURE, "Risk chips are disabled exactly when their count is zero",
              "A risk chip with a live count of 0 must carry the real `disabled` attribute; every chip with a "
              "count above 0 must be enabled. (Which chips are zero differs per account - read at runtime.)",
              "1. Open Dashboard\n2. For each chip compare its count with its disabled state", "-")
    dash = open_dashboard(case, page)
    counts = dash.chip_counts()
    states = {label: dash.is_risk_chip_disabled(label) for label in counts}
    wrong = {k: (counts[k], states[k]) for k in counts if (counts[k] == 0) != states[k]}
    ok = len(counts) == 4 and not wrong
    case.check("disabled == (count is 0) for every chip", ok, expected="consistent",
               actual=f"counts={counts}, disabled={states}", locator=dash.risk_chips.first)
    finish(case, result, ok, f"Chip enablement matches the counts: {counts}.",
           f"Chip enablement wrong for {wrong} (count, disabled).")


@pytest.mark.regression
def test_workspacedashboard_09_risk_chips_are_single_select_and_all_resets(page, result):
    case = mk(page, "WorkspaceDashboard_09", FEATURE, "Risk chips are single-select and 'All' resets the feed",
              "Exactly one risk chip is active at a time: selecting a risk chip deactivates 'All' and marks the feed "
              "'Filtered'; selecting 'All' again reactivates it, removes 'Filtered' and restores every card.",
              "1. Verify 'All' is the active chip\n2. Select the first enabled risk chip - verify it alone is "
              "active and 'Filtered' is shown\n3. Select 'All' - verify the reset",
              "Chip: first enabled risk chip, read at runtime")
    dash = open_dashboard(case, page)
    baseline = dash.news_item_count()
    initial = dash.selected_chip_labels()
    counts = dash.chip_counts()
    label = [k for k in ("High", "Medium", "No Risk") if counts.get(k, 0) > 0][0]
    case.click(dash.risk_chip(label), f"'{label}' risk chip")
    wait_for_content(dash.filtered_badge, timeout=10000)
    during = dash.selected_chip_labels()
    filtered = dash.filtered_badge.count() == 1
    case.check(f"Only '{label}' is active and the feed is marked Filtered", during == [label] and filtered,
               expected=f"[{label}], Filtered", actual=f"{during}, Filtered={filtered}", locator=dash.risk_chip(label))
    case.click(dash.risk_chip("All"), "'All' risk chip")
    page.wait_for_timeout(1200)
    after = dash.selected_chip_labels()
    restored = dash.news_item_count()
    ok = (initial == ["All"] and during == [label] and filtered and after == ["All"]
          and dash.filtered_badge.count() == 0 and restored == baseline)
    case.check("'All' is active again, 'Filtered' is gone and every card is back", after == ["All"] and restored == baseline,
               expected=f"[All], {baseline} cards", actual=f"{after}, {restored} cards")
    finish(case, result, ok, f"Chips behaved as single-select; 'All' restored {restored} cards.",
           f"Chip selection wrong: initial={initial}, during={during}, after={after}, cards {baseline}->{restored}.")


@pytest.mark.regression
@pytest.mark.parametrize("num,label,colour", [("10", "High", "bg-reg-red-800"), ("11", "No Risk", "bg-reg-green-500")],
                         ids=["high", "no_risk"])
def test_workspacedashboard_risk_filter_shows_only_that_risk_level(page, result, num, label, colour):
    case = mk(page, f"WorkspaceDashboard_{num}", FEATURE, f"The '{label}' filter shows only {label} items",
              f"Each feed item carries a risk-coloured bar. With the '{label}' chip selected every remaining item's "
              f"bar must be {colour} (no other risk level), and at least one card must remain.",
              f"1. Open Dashboard\n2. Select the '{label}' chip\n3. Verify every item's risk bar colour",
              f"Chip: {label}")
    dash = open_dashboard(case, page)
    if dash.is_risk_chip_disabled(label):
        actual = f"The '{label}' chip is disabled on this account (count 0) - nothing to filter."
        result(case, actual, True)
        pytest.skip(actual)
    baseline = dash.news_item_count()
    case.click(dash.risk_chip(label), f"'{label}' risk chip")
    wait_for_content(dash.filtered_badge, timeout=10000)
    page.wait_for_timeout(800)
    colours = dash.risk_bar_colours()
    cards = dash.news_item_count()
    ok = colours == [colour] and 1 <= cards <= baseline
    case.check(f"Every item's risk bar is {colour}", ok, expected=f"[{colour}], 1..{baseline} cards",
               actual=f"{colours}, {cards} cards", locator=dash.news_cards.first)
    finish(case, result, ok, f"'{label}' showed {cards} card(s), all {label}.",
           f"'{label}' filter showed bar colours {colours} across {cards} cards (baseline {baseline}).")


@pytest.mark.regression
def test_workspacedashboard_12_no_match_search_shows_empty_message(page, result):
    case = mk(page, "WorkspaceDashboard_12", FEATURE, "A feed search with no matches shows the empty message",
              "Typing a term no card contains must remove every card and show 'No news or updates match your "
              "current search or filter.'",
              "1. Open Dashboard\n2. Type a term that matches nothing\n3. Verify zero cards and the message",
              "Search term: zzzqqq_no_such_item")
    dash = open_dashboard(case, page)
    case.click(dash.news_search, "News search box")
    dash.type_news_search("zzzqqq_no_such_item")
    empty = wait_for_content(dash.empty_state, timeout=10000)
    cards = dash.news_item_count()
    ok = empty and cards == 0
    case.check("Empty message is shown with zero cards", ok, expected="message, 0 cards",
               actual=f"message={empty}, cards={cards}", locator=dash.empty_state)
    finish(case, result, ok, "A no-match search showed the empty message.",
           f"No-match search left message={empty}, cards={cards}.")


@pytest.mark.regression
def test_workspacedashboard_13_feed_search_is_case_insensitive(page, result):
    case = mk(page, "WorkspaceDashboard_13", FEATURE, "Feed search is case-insensitive",
              "Searching for a live card's entity name with its letter case inverted must still return that card.",
              "1. Read a card's entity name\n2. Type it with inverted case\n3. Verify the card is still returned",
              "Search term: a live entity name, case-inverted at runtime")
    dash = open_dashboard(case, page)
    target = [n for n in dash.card_entity_names() if re.search(r"[A-Za-z]{4,}", n)][-1]
    term = target.swapcase()
    case.click(dash.news_search, "News search box")
    dash.type_news_search(term)
    page.wait_for_timeout(1200)
    names = dash.card_entity_names()
    ok = target in names
    case.check("Case-inverted search still returns the card", ok, expected=f"includes '{target}'", actual=str(names))
    finish(case, result, ok, f"Searching '{term}' returned '{target}'.",
           f"Searching '{term}' returned {names}; expected it to include '{target}'.")


@pytest.mark.regression
def test_workspacedashboard_14_clearing_the_search_restores_the_feed(page, result):
    case = mk(page, "WorkspaceDashboard_14", FEATURE, "Clearing the feed search restores every card",
              "After a search has narrowed the feed, deleting the search text must bring back the full baseline "
              "set of cards.",
              "1. Record the card names\n2. Search for one entity (feed narrows)\n3. Clear the search box\n"
              "4. Verify the same cards are back", "Search term: a live entity name, read at runtime")
    dash = open_dashboard(case, page)
    baseline = dash.card_entity_names()
    case.click(dash.news_search, "News search box")
    dash.type_news_search(baseline[-1])
    page.wait_for_timeout(1200)
    narrowed = dash.news_item_count()
    case.check("Search narrowed the feed", narrowed <= len(baseline), expected=f"<= {len(baseline)}", actual=narrowed)
    case.action("Clearing the search box with the keyboard", kind="type")
    dash.clear_news_search()
    page.wait_for_timeout(1500)
    restored = dash.card_entity_names()
    ok = 1 <= narrowed <= len(baseline) and restored == baseline
    case.check("All baseline cards are back", restored == baseline, expected=f"{len(baseline)} cards",
               actual=f"{len(restored)} cards, identical={restored == baseline}")
    finish(case, result, ok, f"Feed went {len(baseline)} -> {narrowed} -> {len(restored)} cards.",
           f"Clearing the search left {len(restored)} cards (baseline {len(baseline)}), identical={restored == baseline}.")


@pytest.mark.regression
def test_workspacedashboard_15_feed_panel_collapses(page, result):
    case = mk(page, "WorkspaceDashboard_15", FEATURE, "The News, Alerts & Updates panel can be collapsed",
              "Clicking 'Collapse panel' must hide the feed (heading and cards) while the Risk Heatmap stays visible.",
              "1. Verify the feed is shown\n2. Click 'Collapse panel'\n3. Verify the feed is hidden and the heatmap remains",
              "-")
    dash = open_dashboard(case, page)
    before = dash.heading_news.is_visible() and dash.news_item_count() > 0
    case.click(dash.collapse_panel_button, "'Collapse panel' button")
    page.wait_for_timeout(1200)
    hidden = dash.heading_news.count() == 0 or not dash.heading_news.is_visible()
    heatmap = dash.heading_risk_heatmap.is_visible()
    ok = before and hidden and heatmap
    case.check("Feed is hidden and the Risk Heatmap is still shown", ok, expected="feed hidden, heatmap visible",
               actual=f"feed shown before={before}, hidden after={hidden}, heatmap={heatmap}",
               locator=dash.heading_risk_heatmap)
    finish(case, result, ok, "The feed panel collapsed and the heatmap stayed visible.",
           f"Collapse check failed: before={before}, hidden={hidden}, heatmap={heatmap}.")


@pytest.mark.regression
def test_workspacedashboard_16_heatmap_renders_chart_and_toolbar(page, result):
    case = mk(page, "WorkspaceDashboard_16", FEATURE, "The Risk Heatmap renders its chart and toolbar",
              "The Risk Heatmap must render its chart canvas and its 4-button toolbar (zoom/fit controls).",
              "1. Open Dashboard\n2. Verify the chart canvas\n3. Verify the 4 toolbar buttons", "-")
    dash = open_dashboard(case, page)
    canvas = wait_for_content(dash.heatmap_canvas, timeout=30000)
    buttons = dash.heatmap_toolbar_buttons.count()
    ok = canvas and buttons == 4
    case.check("Chart canvas and 4 toolbar buttons are rendered", ok, expected="canvas + 4 buttons",
               actual=f"canvas={canvas}, {buttons} buttons", locator=dash.heatmap_canvas)
    finish(case, result, ok, "Heatmap chart and toolbar rendered.",
           f"Heatmap check failed: canvas={canvas}, toolbar buttons={buttons}.")


@pytest.mark.regression
def test_workspacedashboard_17_every_feed_card_names_an_entity_and_jurisdiction(page, result):
    case = mk(page, "WorkspaceDashboard_17", FEATURE, "Every feed card names its entity and jurisdiction",
              "Each card in the feed must carry a non-empty entity name and a jurisdiction flag ('<Country> Flag') - "
              "no anonymous or jurisdiction-less cards.",
              "1. Open Dashboard\n2. Read every card's entity name and flag\n3. Verify none is empty", "-")
    dash = open_dashboard(case, page)
    names, flags = dash.card_entity_names(), dash.card_flags()
    bad = [i for i, (n, f) in enumerate(zip(names, flags)) if not n or not f.endswith(" Flag") or len(f) <= 5]
    ok = len(names) > 0 and len(names) == len(flags) == dash.news_item_count() and not bad
    case.check("Every card has an entity name and a jurisdiction flag", ok, expected="no incomplete cards",
               actual=f"{len(names)} cards, incomplete indexes={bad}", locator=dash.news_cards.first)
    finish(case, result, ok, f"All {len(names)} cards name an entity and a jurisdiction.",
           f"Incomplete cards at indexes {bad} (names={names}, flags={flags}).")


@pytest.mark.regression
def test_workspacedashboard_18_feed_entities_exist_in_entities_grid(page, result):
    case = mk(page, "WorkspaceDashboard_18", FEATURE, "Every entity in the Dashboard feed exists in Entities",
              "Cross-module data integrity: each feed card's entity name must be an entity listed in the Entities "
              "grid (the feed must not reference unknown or deleted entities).",
              "1. Read the feed's entity names\n2. Open Entities and read all entity names\n"
              "3. Verify every feed entity is in the grid", "-")
    dash = open_dashboard(case, page)
    feed = sorted(set(n for n in dash.card_entity_names() if n))
    ent = WorkspaceEntitiesPage(page)
    case.action("Navigating to Workspace > Entities", kind="navigate")
    ent.goto()
    wait_for_content(ent.table_rows, timeout=30000)
    grid = set(ent.entity_names())
    missing = [n for n in feed if n not in grid]
    ok = bool(feed) and not missing
    case.check("Every feed entity is listed in the Entities grid", ok, expected="none missing",
               actual=f"{len(feed)} feed entities, missing={missing}", locator=ent.table)
    finish(case, result, ok, f"All {len(feed)} feed entities exist in the Entities grid.",
           f"Feed references entities not in the grid: {missing}.")


@pytest.mark.regression
@pytest.mark.parametrize("num,name,route", [("19", "Entities", "/companydata/entities/"),
                                            ("20", "Calendar", "/companydata/calendar/")],
                         ids=["to_entities", "to_calendar"])
def test_workspacedashboard_sidebar_navigates_to_module(page, result, num, name, route):
    case = mk(page, f"WorkspaceDashboard_{num}", FEATURE, f"The sidebar's '{name}' link opens {name}",
              f"Clicking '{name}' in the Workspace sidebar from the Dashboard must navigate to {route} and render "
              "that module's own primary control.",
              f"1. Open Dashboard\n2. Click '{name}' in the sidebar\n3. Verify the URL and the module's main button",
              f"Target: {name}")
    dash = open_dashboard(case, page)
    nav = WorkspaceNav(page)
    link = nav.nav_entities if name == "Entities" else nav.nav_calendar
    case.click(link, f"'{name}' sidebar link")
    marker = (WorkspaceEntitiesPage(page).add_entity_button if name == "Entities"
              else WorkspaceCalendarPage(page).create_event_button)
    shown = wait_for_content(marker, timeout=30000)
    ok = shown and route in page.url
    case.check(f"{name} opened on its own route", ok, expected=route, actual=f"{page.url}, main control shown={shown}",
               locator=marker)
    finish(case, result, ok, f"Sidebar navigation opened {name}.",
           f"Sidebar navigation to {name} failed: url={page.url}, main control shown={shown}.")
