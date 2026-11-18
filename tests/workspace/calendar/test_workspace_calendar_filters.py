"""Workspace > Calendar - sorting, search, every filter, and the two views.
All read-only: nothing is created, edited or deleted here. Every expected
value is read from the live page (data differs per environment)."""
import datetime
import re

import pytest

from pages.workspace.workspace_entities_page import WorkspaceEntitiesPage
from tests.workspace._flows import finish, live_country, mk, open_calendar
from utils.wait import wait_for_content

FEATURE = "Workspace Calendar"

SORT_CASES = [
    ("30", "Tax Residence", "countryName"),
    ("31", "Nature of Compliance", "title"),
    ("32", "Due Date", "dueDate"),
]


def _parse_due(text):
    return datetime.datetime.strptime(text, "%d %B %Y").date()


def _parse_range(value):
    """'18-Oct-2026 to 18-Feb-2027' -> (date, date)."""
    a, b = [p.strip() for p in value.split(" to ")]
    fmt = "%d-%b-%Y"
    return datetime.datetime.strptime(a, fmt).date(), datetime.datetime.strptime(b, fmt).date()


def _ordered(values, column, descending):
    keys = [_parse_due(v) for v in values] if column == "Due Date" else [v.lower() for v in values]
    return keys == sorted(keys, reverse=descending)


@pytest.mark.regression
@pytest.mark.parametrize("num,column,field", SORT_CASES, ids=[c[2] for c in SORT_CASES])
def test_workspacecalendar_column_sorts_both_directions(page, result, num, column, field):
    case = mk(page, f"WorkspaceCalendar_{num}", FEATURE, f"'{column}' sorts ascending and descending",
              f"Clicking the '{column}' header must sort the Agenda by that column: `aria-sort`, the `?sort={field}:"
              "<dir>` URL parameter and the actual cell order must all agree, in both directions.",
              f"1. Open Calendar\n2. Click the '{column}' header - verify the order\n3. Click again - verify the "
              "opposite order", f"Column: {column}")
    cal = open_calendar(case, page)
    header = cal.sortable_header(column)
    seen = {}
    for _ in range(3):
        case.click(header, f"'{column}' column header")
        page.wait_for_timeout(1500)
        state = cal.column_sort_state(column)
        if state in ("ascending", "descending") and state not in seen:
            direction = "asc" if state == "ascending" else "desc"
            values = cal.column_values(column)
            seen[state] = {"url": f"sort={field}%3A{direction}" in page.url or f"sort={field}:{direction}" in page.url,
                           "ordered": _ordered(values, column, state == "descending"), "sample": values[:3]}
            case.check(f"{state}: URL carries sort={field}:{direction} and the cells are in that order",
                       seen[state]["url"] and seen[state]["ordered"], expected=f"{state} order",
                       actual=f"url ok={seen[state]['url']}, ordered={seen[state]['ordered']}, first={values[:3]}",
                       locator=header)
        if len(seen) == 2:
            break
    ok = len(seen) == 2 and all(v["url"] and v["ordered"] for v in seen.values())
    finish(case, result, ok, f"'{column}' sorted correctly in both directions.",
           f"'{column}' sort check failed: {seen}.")


@pytest.mark.regression
def test_workspacecalendar_33_event_type_chip_filters_the_agenda(page, result):
    case = mk(page, "WorkspaceCalendar_33", FEATURE, "Selecting one Event Type shows exactly that type's events",
              "Clicking a single Event Type chip must reduce the Agenda to exactly that chip's count; clicking "
              "'All' must restore the full list.",
              "1. Read the chips and the row count\n2. Click the first type chip - verify rows == its count\n"
              "3. Click 'All' - verify the baseline is restored", "Chip: first type chip after 'All', read at runtime")
    cal = open_calendar(case, page)
    counts = cal.chip_counts()
    baseline = cal.agenda_row_count()
    label = [k for k in counts if k != "All"][0]
    case.click(cal.chip_button(label), f"'{label}' event type chip")
    page.wait_for_timeout(1200)
    filtered = cal.agenda_row_count()
    case.check(f"Rows equal the '{label}' count", filtered == counts[label], expected=counts[label], actual=filtered,
               locator=cal.table)
    case.click(cal.chip_button("All"), "'All' event type chip")
    page.wait_for_timeout(1200)
    restored = cal.agenda_row_count()
    ok = filtered == counts[label] and restored == baseline and baseline == counts.get("All")
    case.check("'All' restores the full list", restored == baseline, expected=baseline, actual=restored)
    finish(case, result, ok, f"'{label}' filtered {baseline} rows to {filtered}; 'All' restored {restored}.",
           f"Chip filter wrong: counts={counts}, baseline={baseline}, filtered={filtered}, restored={restored}.")


@pytest.mark.regression
def test_workspacecalendar_34_event_type_chips_are_multi_select(page, result):
    case = mk(page, "WorkspaceCalendar_34", FEATURE, "Two Event Type chips can be combined",
              "Event Type chips are multi-select: selecting two types must show the sum of both counts.",
              "1. Read the chips\n2. Click the first two type chips\n3. Verify rows == sum of both counts",
              "Chips: first two type chips after 'All', read at runtime")
    cal = open_calendar(case, page)
    counts = cal.chip_counts()
    types = [k for k in counts if k != "All"]
    if len(types) < 2:
        actual = f"Only {len(types)} event type on this account - a two-type combination cannot be exercised."
        result(case, actual, True)
        pytest.skip(actual)
    a, b = types[0], types[1]
    case.click(cal.chip_button(a), f"'{a}' event type chip")
    page.wait_for_timeout(1000)
    case.click(cal.chip_button(b), f"'{b}' event type chip")
    page.wait_for_timeout(1200)
    rows = cal.agenda_row_count()
    ok = rows == counts[a] + counts[b]
    case.check(f"Rows equal '{a}' + '{b}'", ok, expected=counts[a] + counts[b], actual=rows, locator=cal.table)
    finish(case, result, ok, f"'{a}' + '{b}' showed {rows} rows ({counts[a]} + {counts[b]}).",
           f"Combined filter showed {rows} rows, expected {counts[a]} + {counts[b]}.")


@pytest.mark.regression
def test_workspacecalendar_35_event_type_counts_add_up_to_all(page, result):
    case = mk(page, "WorkspaceCalendar_35", FEATURE, "Event Type counts add up to 'All' and to the Agenda rows",
              "Data integrity: the sum of every individual Event Type count must equal the 'All' count, which must "
              "equal the number of Agenda rows.",
              "1. Read every chip count\n2. Compare the sum of the type chips, the 'All' chip and the row count", "-")
    cal = open_calendar(case, page)
    counts = cal.chip_counts()
    total = sum(v for k, v in counts.items() if k != "All")
    rows = cal.agenda_row_count()
    ok = len(counts) >= 2 and total == counts.get("All") == rows
    case.check("Sum of type counts == All == Agenda rows", ok, expected=f"{counts.get('All')}",
               actual=f"sum={total}, All={counts.get('All')}, rows={rows}", locator=cal.event_type_chips.first)
    finish(case, result, ok, f"Counts are consistent: {counts}, {rows} rows.",
           f"Counts inconsistent: {counts}, sum of types={total}, rows={rows}.")


@pytest.mark.regression
def test_workspacecalendar_36_search_filters_rows_and_recounts_chips(page, result):
    case = mk(page, "WorkspaceCalendar_36", FEATURE, "Search filters the Agenda and the Event Type counts follow",
              "Typing part of a live event title must leave only rows containing it, and the 'All' chip must be "
              "recalculated to the number of rows shown.",
              "1. Read a live event title\n2. Type its first 8 characters\n3. Verify the rows and the 'All' count",
              "Search term: first 8 characters of the last Agenda title, read at runtime")
    cal = open_calendar(case, page)
    baseline = cal.agenda_row_count()
    term = [t for t in cal.column_values("Nature of Compliance") if len(t) >= 4][-1][:8]
    case.click(cal.search_input, "Calendar search box")
    cal.type_search(term)
    page.wait_for_timeout(1500)
    rows = [r.inner_text() for r in cal.table_rows.all()]
    all_count = cal.chip_counts().get("All")
    matching = all(term.lower() in r.lower() for r in rows)
    ok = 1 <= len(rows) <= baseline and matching and all_count == len(rows)
    case.check("Only matching rows remain and 'All' equals the rows shown", ok,
               expected=f"1..{baseline} rows containing '{term}', All == rows",
               actual=f"{len(rows)} rows, all match={matching}, All({all_count})", locator=cal.table)
    finish(case, result, ok, f"Searching '{term}' left {len(rows)} matching row(s) and All({all_count}).",
           f"Search '{term}': {len(rows)} rows, all match={matching}, All({all_count}), baseline {baseline}.")


@pytest.mark.regression
def test_workspacecalendar_37_no_match_search_shows_empty_state(page, result):
    case = mk(page, "WorkspaceCalendar_37", FEATURE, "A search with no matches shows the empty state",
              "Typing a term no event contains must replace the Agenda with the 'Stay on Top of Compliance "
              "Deadlines' empty state and zero rows.",
              "1. Open Calendar\n2. Type a term that matches nothing\n3. Verify the empty state and zero rows",
              "Search term: zzzqqq_no_such_event")
    cal = open_calendar(case, page)
    case.click(cal.search_input, "Calendar search box")
    cal.type_search("zzzqqq_no_such_event")
    empty = wait_for_content(cal.empty_state, timeout=10000)
    rows = cal.agenda_row_count()
    ok = empty and rows == 0
    case.check("Empty state is shown with zero rows", ok, expected="empty state, 0 rows",
               actual=f"empty state={empty}, rows={rows}", locator=cal.empty_state)
    finish(case, result, ok, "A no-match search showed the empty state.",
           f"No-match search left empty state={empty}, rows={rows}.")


@pytest.mark.regression
def test_workspacecalendar_38_jurisdiction_filter_lists_all_jurisdictions(page, result):
    case = mk(page, "WorkspaceCalendar_38", FEATURE, "Filter By Jurisdiction widens the Agenda beyond entity jurisdictions",
              "Switching Filter By from Entity to Jurisdiction (nothing selected) must list events for all "
              "jurisdictions: at least as many rows and jurisdictions as the entity-scoped default, with every "
              "default jurisdiction still present and the chip counts recalculated.",
              "1. Record rows and jurisdictions under the default Entity filter\n2. Click 'Jurisdiction'\n"
              "3. Verify the widened list", "-")
    cal = open_calendar(case, page)
    base_rows = cal.agenda_row_count()
    base_countries = set(cal.column_values("Tax Residence"))
    case.click(cal.filter_by_jurisdiction_radio, "'Jurisdiction' filter option")
    page.wait_for_timeout(2500)
    wait_for_content(cal.table_rows, timeout=20000)
    rows = cal.agenda_row_count()
    countries = set(cal.column_values("Tax Residence"))
    all_count = cal.chip_counts().get("All")
    ok = rows >= base_rows and base_countries <= countries and all_count == rows
    case.check("Jurisdiction view is a superset of the entity view and All == rows", ok,
               expected=f">= {base_rows} rows incl. {sorted(base_countries)}",
               actual=f"{rows} rows, {len(countries)} jurisdictions, All({all_count})", locator=cal.table)
    finish(case, result, ok, f"Jurisdiction filter widened {base_rows} rows/{len(base_countries)} jurisdictions "
                             f"to {rows}/{len(countries)}.",
           f"Jurisdiction filter: {rows} rows (was {base_rows}), missing={sorted(base_countries - countries)}, All({all_count}).")


@pytest.mark.regression
def test_workspacecalendar_39_selecting_a_jurisdiction_shows_only_its_events(page, result):
    case = mk(page, "WorkspaceCalendar_39", FEATURE, "Selecting one jurisdiction shows only that jurisdiction's events",
              "With Filter By = Jurisdiction, choosing one country must list only events whose Tax Residence is "
              "that country and show it as a selected chip.",
              "1. Read a jurisdiction from the Agenda\n2. Filter By Jurisdiction > select it\n"
              "3. Verify every row's Tax Residence and the selected chip",
              "Jurisdiction: first Agenda row's Tax Residence, read at runtime")
    cal = open_calendar(case, page)
    country = live_country(cal)
    case.click(cal.filter_by_jurisdiction_radio, "'Jurisdiction' filter option")
    page.wait_for_timeout(1500)
    case.click(cal.filter_picker.first, "'Select Jurisdictions' picker")
    wait_for_content(cal.picker_popup, timeout=10000)
    case.action(f"Typing '{country}' to filter the jurisdiction list", kind="type")
    page.keyboard.type(country, delay=30)
    case.click(cal.picker_option(country).first, f"'{country}' option")
    page.wait_for_timeout(2500)
    residences = cal.column_values("Tax Residence")
    chips = [c.strip() for c in cal.filter_selected_chips.all_inner_texts()]
    ok = len(residences) >= 1 and set(residences) == {country} and chips == [country]
    case.check("Every row is for the selected jurisdiction and it is shown as the selected chip", ok,
               expected=f"all '{country}', chip ['{country}']", actual=f"{sorted(set(residences))}, chips {chips}",
               locator=cal.table)
    finish(case, result, ok, f"Only {country}'s {len(residences)} event(s) were listed.",
           f"Jurisdiction selection wrong: residences={sorted(set(residences))}, chips={chips}.")


@pytest.mark.regression
def test_workspacecalendar_40_selecting_an_entity_shows_only_its_jurisdiction(page, result):
    case = mk(page, "WorkspaceCalendar_40", FEATURE, "Selecting one entity shows only its jurisdiction's events",
              "Cross-module: with Filter By = Entity, un-checking 'All Entity's Jurisdiction' and choosing one "
              "entity must list only events for that entity's Tax Residence (as recorded in the Entities grid) and "
              "show the entity as the selected chip.",
              "1. Open Entities and pick an entity whose Tax Residence has Agenda events\n"
              "2. Calendar > Select Entity(ies): un-check All, check that entity\n"
              "3. Verify every row's Tax Residence and the selected chip",
              "Entity: read at runtime from the Entities grid")
    cal = open_calendar(case, page)
    agenda_countries = set(cal.column_values("Tax Residence"))
    ent = WorkspaceEntitiesPage(page)
    ent.goto()
    wait_for_content(ent.table_rows, timeout=20000)
    pairs = list(zip(ent.entity_names(), ent.column_values("Tax Residence")))
    names = [n for n, _ in pairs]
    candidates = [(n, c) for n, c in pairs if c in agenda_countries and names.count(n) == 1 and len(n) > 3]
    if not candidates:
        actual = "No uniquely named entity has a Tax Residence with Agenda events on this account."
        result(case, actual, True)
        pytest.skip(actual)
    entity, country = candidates[-1]
    cal.goto()
    wait_for_content(cal.table_rows, timeout=20000)
    case.step(2, f"Select only the entity '{entity}'")
    case.click(cal.filter_picker.first, "'Select Entity(ies)' picker")
    wait_for_content(cal.picker_popup, timeout=10000)
    case.click(cal.picker_option("All Entity's Jurisdiction"), "'All Entity's Jurisdiction' option (un-check)")
    page.wait_for_timeout(1000)
    case.click(cal.picker_option(entity).first, f"'{entity}' option")
    page.wait_for_timeout(2500)
    residences = cal.column_values("Tax Residence")
    chips = [c.strip() for c in cal.filter_selected_chips.all_inner_texts()]
    ok = len(residences) >= 1 and set(residences) == {country} and chips == [entity]
    case.check("Only the entity's jurisdiction is listed and the entity is the selected chip", ok,
               expected=f"all '{country}', chip ['{entity}']", actual=f"{sorted(set(residences))}, chips {chips}",
               locator=cal.table)
    finish(case, result, ok, f"Selecting '{entity}' listed only {country}'s {len(residences)} event(s).",
           f"Entity selection wrong: expected {country}; residences={sorted(set(residences))}, chips={chips}.")


@pytest.mark.regression
def test_workspacecalendar_41_default_date_range_brackets_today_and_all_rows(page, result):
    case = mk(page, "WorkspaceCalendar_41", FEATURE, "The default Date Range brackets today and every listed due date",
              "The Date Range defaults to a rolling window around today (not a fixed date). Today and every Agenda "
              "row's Due Date must fall inside the displayed range.",
              "1. Read the Date Range value\n2. Verify today is inside it\n3. Verify every Due Date is inside it", "-")
    cal = open_calendar(case, page)
    value = cal.date_range_input.first.input_value()
    start, end = _parse_range(value)
    today = datetime.date.today()
    dues = [_parse_due(v) for v in cal.column_values("Due Date")]
    outside = [d.isoformat() for d in dues if not (start <= d <= end)]
    ok = start <= today <= end and bool(dues) and not outside
    case.check("Today and every Due Date are inside the displayed range", ok, expected=f"within {value}",
               actual=f"today inside={start <= today <= end}, {len(dues)} rows, outside={outside}",
               locator=cal.date_range_input)
    finish(case, result, ok, f"All {len(dues)} due dates fall within {value}.",
           f"Date range '{value}': today inside={start <= today <= end}, due dates outside={outside}.")


@pytest.mark.regression
def test_workspacecalendar_42_this_year_preset_applies_the_calendar_year(page, result):
    case = mk(page, "WorkspaceCalendar_42", FEATURE, "The 'This Year' preset filters the Agenda to the current year",
              "Opening the Date Range picker and choosing 'This Year' must set the range to 1 January - 31 December "
              "of the current year and list only events due in that year.",
              "1. Open the Date Range picker\n2. Click 'This Year' (and OK if shown)\n"
              "3. Verify the range value and every Due Date's year", "Preset: This Year")
    cal = open_calendar(case, page)
    year = datetime.date.today().year
    case.click(cal.date_range_input.first, "Date Range field")
    wait_for_content(cal.date_preset("This Year"), timeout=10000)
    case.click(cal.date_preset("This Year"), "'This Year' preset")
    page.wait_for_timeout(800)
    if cal.date_ok_button.count() and cal.date_ok_button.first.is_visible():
        case.click(cal.date_ok_button.first, "date range 'OK'")
    page.wait_for_timeout(2500)
    value = cal.date_range_input.first.input_value()
    wait_for_content(cal.table_rows, timeout=20000)
    years = sorted({_parse_due(v).year for v in cal.column_values("Due Date")})
    ok = value == f"01-Jan-{year} to 31-Dec-{year}" and years == [year]
    case.check("Range is the calendar year and every Due Date is in it", ok,
               expected=f"01-Jan-{year} to 31-Dec-{year}; years [{year}]", actual=f"{value}; years {years}",
               locator=cal.date_range_input)
    finish(case, result, ok, f"'This Year' set {value} and listed only {year} events.",
           f"'This Year' gave range '{value}' and due-date years {years}.")


@pytest.mark.regression
def test_workspacecalendar_43_filters_panel_collapses(page, result):
    case = mk(page, "WorkspaceCalendar_43", FEATURE, "The Filters panel can be collapsed",
              "Clicking the Filters panel's collapse button must hide its contents (Date Range, Filter By, Event "
              "Types) while the Agenda stays usable.",
              "1. Verify 'Date Range' is visible\n2. Click the Filters collapse button\n"
              "3. Verify 'Date Range' is hidden and the Agenda is still shown", "-")
    cal = open_calendar(case, page)
    before = cal.date_range_label.is_visible()
    rows = cal.agenda_row_count()
    case.click(cal.filters_collapse_button, "Filters collapse button")
    page.wait_for_timeout(1000)
    hidden = not cal.date_range_label.is_visible()
    ok = before and hidden and cal.agenda_row_count() == rows and cal.create_event_button.is_visible()
    case.check("Filter controls are hidden and the Agenda is unchanged", ok, expected="hidden, same rows",
               actual=f"visible before={before}, hidden after={hidden}, rows {rows}->{cal.agenda_row_count()}")
    finish(case, result, ok, "The Filters panel collapsed and the Agenda stayed in place.",
           f"Collapse check failed: visible before={before}, hidden after={hidden}.")


def _month_index(text):
    d = datetime.datetime.strptime(text, "%B %Y")
    return d.year * 12 + d.month


@pytest.mark.regression
def test_workspacecalendar_44_month_navigation_moves_one_month_at_a_time(page, result):
    case = mk(page, "WorkspaceCalendar_44", FEATURE, "Month navigation moves exactly one month per click",
              "In Calendar view the next chevron must advance the heading by one month and the previous chevron "
              "must go back by one month (including across a year boundary).",
              "1. Switch to Calendar view and read the month heading\n2. Click next - verify +1 month\n"
              "3. Click previous twice - verify -1 month from the start", "-")
    cal = open_calendar(case, page)
    case.click(cal.toggle_calendar, "'Calendar' view toggle")
    wait_for_content(cal.month_heading, timeout=15000)
    start = cal.month_heading.first.inner_text().strip()
    case.click(cal.month_next, "next-month chevron")
    page.wait_for_timeout(800)
    nxt = cal.month_heading.first.inner_text().strip()
    case.click(cal.month_prev, "previous-month chevron")
    page.wait_for_timeout(800)
    case.click(cal.month_prev, "previous-month chevron")
    page.wait_for_timeout(800)
    prev = cal.month_heading.first.inner_text().strip()
    ok = _month_index(nxt) == _month_index(start) + 1 and _month_index(prev) == _month_index(start) - 1
    case.check("Heading moved +1 then -1 month relative to the start", ok,
               expected=f"{start} -> +1 -> -1", actual=f"{start} -> {nxt} -> {prev}", locator=cal.month_heading)
    finish(case, result, ok, f"Month navigation: {start} -> {nxt} -> {prev}.",
           f"Month navigation wrong: {start} -> {nxt} -> {prev}.")


@pytest.mark.regression
def test_workspacecalendar_45_view_toggle_round_trip_restores_agenda(page, result):
    case = mk(page, "WorkspaceCalendar_45", FEATURE, "Agenda -> Calendar -> Agenda restores the Agenda list",
              "The page title must read 'Agenda' or 'Calendar' to match the active view, the month grid must "
              "replace the table in Calendar view, and switching back must restore the same Agenda rows.",
              "1. Record the Agenda rows and title\n2. Switch to Calendar - verify title and no table\n"
              "3. Switch back - verify title and identical rows", "-")
    cal = open_calendar(case, page)
    before = cal.column_values("Nature of Compliance")
    t0 = cal.view_title.inner_text().strip()
    case.click(cal.toggle_calendar, "'Calendar' view toggle")
    wait_for_content(cal.month_heading, timeout=15000)
    t1 = cal.view_title.inner_text().strip()
    grid = cal.weekday_sun.first.is_visible() and cal.agenda_row_count() == 0
    case.check("Calendar view shows the month grid instead of the table, titled 'Calendar'",
               t1 == "Calendar" and grid, expected="title Calendar, grid shown",
               actual=f"title '{t1}', grid={grid}", locator=cal.view_title)
    case.click(cal.toggle_agenda, "'Agenda' view toggle")
    wait_for_content(cal.table_rows, timeout=15000)
    t2 = cal.view_title.inner_text().strip()
    after = cal.column_values("Nature of Compliance")
    ok = t0 == "Agenda" and t1 == "Calendar" and grid and t2 == "Agenda" and after == before
    case.check("Agenda is restored with identical rows", t2 == "Agenda" and after == before,
               expected=f"{len(before)} rows", actual=f"title '{t2}', {len(after)} rows, identical={after == before}")
    finish(case, result, ok, "The view toggle round trip restored the Agenda.",
           f"Round trip wrong: titles {t0}/{t1}/{t2}, grid={grid}, rows identical={after == before}.")
