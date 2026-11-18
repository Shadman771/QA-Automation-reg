"""Workspace > Calendar - custom event create / read / update / delete.

Every test creates its own `WorkspaceQA_<tag>_<timestamp>` event (the tag
is written into both the title and the description, so cleanup finds it
even if the title is changed) in a jurisdiction read from the live Agenda,
and deletes it in a `finally` block. System deadlines and pre-existing
custom events are never edited or deleted."""
import pytest

from pages.workspace.workspace_dashboard_page import WorkspaceDashboardPage
from tests.workspace._flows import (
    create_event, due_text, fill_event, finish, live_country, mk, open_calendar, open_row_action, pick_due_date,
    due, uid,
)
from utils.wait import wait_for_content

FEATURE = "Workspace Calendar"
PRE = "User is logged in. The test creates its own WorkspaceQA_ event and deletes it afterwards."


@pytest.mark.smoke
def test_workspacecalendar_06_create_event_appears_in_agenda_with_saved_values(page, result):
    tag = uid("create")
    case = mk(page, "WorkspaceCalendar_06", FEATURE, "Creating an event adds an Agenda row with the saved values",
              "Saving a Single Event must add an Agenda row whose Tax Residence, Nature of Compliance, Description "
              "and Due Date equal what was entered.",
              "1. Open Calendar\n2. Create New Event (country, title, description, due date) and Save\n"
              "3. Verify the new row's cells", f"Title: {tag}; Due: today+20 days; Country: read from the live Agenda",
              PRE)
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        case.step(2, f"Create an event for {country}")
        saved = create_event(case, cal, country, tag, f"desc {tag}", days=20)
        shown = cal.wait_row(tag, 20000)
        case.step(3, "Verify the new row's cells")
        cells = cal.row_cells(tag)
        want = {"Tax Residence": country, "Nature of Compliance": tag, "Description": f"desc {tag}",
                "Due Date": due_text(20)}
        wrong = {k: cells.get(k) for k, v in want.items() if cells.get(k) != v}
        ok = saved and shown and not wrong
        case.check("Agenda row equals the entered values", ok, expected=str(want), actual=str(cells),
                   locator=cal.row(tag))
        finish(case, result, ok, f"Event '{tag}' was created with the correct values.",
               f"Created event row wrong: saved={saved}, shown={shown}, mismatches={wrong}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_07_created_event_persists_after_reload(page, result):
    tag = uid("persist")
    case = mk(page, "WorkspaceCalendar_07", FEATURE, "A created event persists after a page reload",
              "After creating an event, reloading the Calendar must still list it.",
              "1. Create an event\n2. Reload the page\n3. Verify the row is still listed", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        case.step(2, "Reload the Calendar")
        cal.goto()
        ok = saved and cal.wait_row(tag, 20000)
        case.check("Event is still listed after reload", ok, expected="1 row", actual=cal.row(tag).count(),
                   locator=cal.row(tag))
        finish(case, result, ok, "The created event persisted across a reload.",
               "The created event was not listed after a reload.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_08_create_and_delete_update_event_type_counts(page, result):
    tag = uid("counts")
    case = mk(page, "WorkspaceCalendar_08", FEATURE, "Event Types counts follow create and delete",
              "Creating a custom event must raise the 'All' and 'Custom Event' chip counts by exactly 1; deleting "
              "it must return both to their baseline.",
              "1. Record the 'All' and 'Custom Event' counts\n2. Create an event and re-read\n"
              "3. Delete it and re-read", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        base = cal.chip_counts()
        b_all, b_custom = base.get("All", 0), base.get("Custom Event", 0)
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        after = cal.chip_counts()
        up = after.get("All") == b_all + 1 and after.get("Custom Event") == b_custom + 1
        case.check("'All' and 'Custom Event' each rose by 1", up, expected=f"All {b_all + 1}, Custom {b_custom + 1}",
                   actual=f"All {after.get('All')}, Custom {after.get('Custom Event')}",
                   locator=cal.event_type_chips.first)
        case.step(3, "Delete the event")
        open_row_action(case, cal, tag, "Delete")
        case.click(cal.delete_confirm_button, "'Delete' confirm button")
        cal.wait_modal_closed(15000)
        cal.wait_row_gone(tag)
        page.wait_for_timeout(800)
        end = cal.chip_counts()
        down = end.get("All") == b_all and end.get("Custom Event", 0) == b_custom
        ok = saved and up and down
        case.check("Both counts are back to their baseline", down, expected=f"All {b_all}, Custom {b_custom}",
                   actual=f"All {end.get('All')}, Custom {end.get('Custom Event', 0)}")
        finish(case, result, ok, f"Counts went All {b_all}->{after.get('All')}->{end.get('All')}.",
               f"Chip counts wrong: baseline={base}, after create={after}, after delete={end}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_09_external_link_is_shown_as_e_file_link(page, result):
    tag = uid("link")
    case = mk(page, "WorkspaceCalendar_09", FEATURE, "An External Link is shown as an 'E-File' link; none leaves it blank",
              "An event saved with an External Link must show 'E-File' in its Applicable Form cell; an event saved "
              "without one must leave that cell empty.",
              "1. Create one event with an External Link and one without\n2. Verify both Applicable Form cells",
              f"Titles: {tag}_with / {tag}_without; Link: https://example.com/qa", PRE)
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        s1 = create_event(case, cal, country, f"{tag}_with", f"desc {tag}", link="https://example.com/qa")
        cal.wait_row(f"{tag}_with", 20000)
        s2 = create_event(case, cal, country, f"{tag}_without", f"desc {tag}")
        cal.wait_row(f"{tag}_without", 20000)
        with_link = cal.row_cells(f"{tag}_with").get("Applicable Form")
        without = cal.row_cells(f"{tag}_without").get("Applicable Form")
        ok = s1 and s2 and with_link == "E-File" and without == ""
        case.check("Applicable Form is 'E-File' with a link and empty without", ok, expected="'E-File' / ''",
                   actual=f"'{with_link}' / '{without}'", locator=cal.row(f"{tag}_with"))
        finish(case, result, ok, "External Link was rendered as an E-File link only where one was saved.",
               f"Applicable Form cells were '{with_link}' (with link) and '{without}' (without).")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_10_created_event_appears_in_month_grid(page, result):
    tag = uid("grid")
    case = mk(page, "WorkspaceCalendar_10", FEATURE, "A created event appears in the Calendar month grid",
              "After creating an event, switching to the Calendar view and navigating to its due month must show "
              "the event on the grid.",
              "1. Create an event due today+20 days\n2. Switch to Calendar view\n"
              "3. Navigate forward until the event is shown (max 5 months)", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}", days=20)
        cal.wait_row(tag, 20000)
        case.step(2, "Switch to Calendar view")
        case.click(cal.toggle_calendar, "'Calendar' view toggle")
        wait_for_content(cal.month_heading, timeout=15000)
        found = False
        for _ in range(5):
            if wait_for_content(cal.grid_event(tag), timeout=2500):
                found = True
                break
            case.click(cal.month_next, "next-month chevron")
        month = cal.month_heading.first.inner_text()
        ok = saved and found
        case.check("Event is shown on the month grid", ok, expected="visible", actual=f"found={found} (showing {month})",
                   locator=cal.grid_event(tag))
        finish(case, result, ok, f"Event was shown on the month grid ({month}).",
               f"Event was not found on the month grid (last month shown: {month}).")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.smoke
def test_workspacecalendar_11_edit_event_updates_row_and_persists(page, result):
    tag = uid("edit")
    case = mk(page, "WorkspaceCalendar_11", FEATURE, "Editing an event updates its row and persists",
              "Row menu > Edit, changing the title and description, then Save must update the Agenda row, remove "
              "the old title, and survive a reload.",
              "1. Create an event\n2. Row menu > Edit; change title and description; Save\n"
              "3. Verify the row\n4. Reload and verify again", f"Title: {tag} -> {tag}_edited", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        case.step(2, "Edit the event")
        open_row_action(case, cal, tag, "Edit")
        opened = wait_for_content(cal.modal_edit_heading, timeout=15000)
        fill_event(case, cal, title=f"{tag}_edited", description=f"changed {tag}")
        case.click(cal.modal_save_button, "'Save' button")
        closed = cal.wait_modal_closed(20000)
        shown = cal.wait_row(f"{tag}_edited", 20000)
        cells = cal.row_cells(f"{tag}_edited")
        old = [t for t in cal.column_values("Nature of Compliance") if t == tag]
        case.check("Row shows the new title and description; the old title is gone",
                   shown and cells.get("Description") == f"changed {tag}" and not old,
                   expected=f"{tag}_edited / changed {tag}", actual=f"{cells}, old rows={old}",
                   locator=cal.row(f"{tag}_edited"))
        case.step(4, "Reload and verify the edit persisted")
        cal.goto()
        persisted = cal.wait_row(f"{tag}_edited", 20000)
        ok = (saved and opened and closed and shown and cells.get("Description") == f"changed {tag}"
              and not old and persisted)
        case.check("Edited event is still shown after reload", persisted, expected="visible", actual=persisted)
        finish(case, result, ok, "The event was edited and the change persisted.",
               f"Edit failed: opened={opened}, closed={closed}, shown={shown}, persisted={persisted}, cells={cells}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_12_edit_modal_is_prefilled_with_saved_values(page, result):
    tag = uid("prefill")
    case = mk(page, "WorkspaceCalendar_12", FEATURE, "The Edit Event modal is pre-filled with the saved values",
              "Opening Edit must show the event's saved country, title, description, due date (ISO) and link.",
              "1. Create an event with every field\n2. Row menu > Edit\n3. Verify every pre-filled field\n4. Cancel",
              f"Title: {tag}; Link: https://example.com/qa", PRE)
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        saved = create_event(case, cal, country, tag, f"desc {tag}", days=20, link="https://example.com/qa")
        cal.wait_row(tag, 20000)
        open_row_action(case, cal, tag, "Edit")
        opened = wait_for_content(cal.modal_edit_heading, timeout=15000)
        got = {"country": cal.modal_country_combo.inner_text().strip(), "title": cal.modal_title_input.input_value(),
               "description": cal.modal_description_input.input_value(),
               "due": cal.modal_due_date_input.input_value(), "link": cal.modal_external_link_input.input_value()}
        want = {"country": country, "title": tag, "description": f"desc {tag}", "due": due(20).isoformat(),
                "link": "https://example.com/qa"}
        ok = saved and opened and got == want
        case.check("Edit modal shows every saved value", ok, expected=str(want), actual=str(got),
                   locator=cal.modal_title_input)
        case.click(cal.delete_cancel_button, "'Cancel' button")
        cal.wait_modal_closed(10000)
        finish(case, result, ok, "Edit modal was pre-filled with the saved values.",
               f"Edit modal pre-fill was {got}, expected {want}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_13_edit_due_date_updates_row(page, result):
    tag = uid("redate")
    case = mk(page, "WorkspaceCalendar_13", FEATURE, "Changing an event's due date updates the Agenda row",
              "Editing an event and picking a different due date must update the row's Due Date cell.",
              "1. Create an event due today+20 days\n2. Edit it and pick today+25 days; Save\n"
              "3. Verify the Due Date cell", f"Title: {tag}; Due: +20d -> +25d", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}", days=20)
        cal.wait_row(tag, 20000)
        open_row_action(case, cal, tag, "Edit")
        wait_for_content(cal.modal_edit_heading, timeout=15000)
        pick_due_date(case, cal, due(25))
        case.click(cal.modal_save_button, "'Save' button")
        closed = cal.wait_modal_closed(20000)
        wait_for_content(cal.row(tag).filter(has_text=due_text(25)), timeout=15000)
        got = cal.row_cells(tag).get("Due Date")
        ok = saved and closed and got == due_text(25)
        case.check("Due Date cell shows the new date", ok, expected=due_text(25), actual=got, locator=cal.row(tag))
        finish(case, result, ok, f"Due date was changed to {got}.",
               f"Due Date cell was '{got}', expected '{due_text(25)}' (closed={closed}).")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_14_delete_dialog_names_event_and_cancel_keeps_it(page, result):
    tag = uid("delcancel")
    case = mk(page, "WorkspaceCalendar_14", FEATURE, "Delete asks for confirmation and Cancel keeps the event",
              "Row menu > Delete must ask \"Do you want to delete the event '<title>'? This action is "
              "irreversible.\"; Cancel must leave the row in place.",
              "1. Create an event\n2. Row menu > Delete\n3. Verify the dialog text\n4. Cancel\n"
              "5. Verify the row is still listed", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        open_row_action(case, cal, tag, "Delete")
        shown = wait_for_content(cal.delete_dialog_text, timeout=10000)
        text = cal.delete_dialog_text.first.inner_text() if shown else ""
        named = f"'{tag}'" in text and "irreversible" in text
        case.check("Dialog names this event and warns it is irreversible", shown and named,
                   expected=f"...delete the event '{tag}'? This action is irreversible.", actual=text,
                   locator=cal.delete_dialog_text)
        case.click(cal.delete_cancel_button, "'Cancel' button")
        closed = cal.wait_modal_closed(10000)
        still = cal.row(tag).count() == 1
        ok = saved and shown and named and closed and still
        case.check("Row is still listed after Cancel", still, expected="1 row", actual=cal.row(tag).count())
        finish(case, result, ok, "Delete asked for confirmation and Cancel kept the event.",
               f"Cancel flow wrong: dialog='{text}', closed={closed}, row still listed={still}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.smoke
def test_workspacecalendar_15_delete_event_removes_it_permanently(page, result):
    tag = uid("delete")
    case = mk(page, "WorkspaceCalendar_15", FEATURE, "Confirming Delete removes the event permanently",
              "Row menu > Delete > Delete must remove the row and it must stay gone after a reload.",
              "1. Create an event\n2. Row menu > Delete > confirm\n3. Verify the row is gone\n"
              "4. Reload and verify it is still gone", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        open_row_action(case, cal, tag, "Delete")
        case.click(cal.delete_confirm_button, "'Delete' confirm button")
        cal.wait_modal_closed(15000)
        gone = cal.wait_row_gone(tag)
        case.check("Row disappears right after confirming", gone, expected="0 rows", actual=cal.row(tag).count())
        cal.goto()
        wait_for_content(cal.table_rows, timeout=20000)
        gone_after = cal.row(tag).count() == 0
        ok = saved and gone and gone_after
        case.check("Row is still absent after reload", gone_after, expected="0 rows", actual=cal.row(tag).count())
        finish(case, result, ok, "The event was deleted and stayed deleted after a reload.",
               f"Delete failed: saved={saved}, gone={gone}, gone after reload={gone_after}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_16_only_custom_events_have_row_actions(page, result):
    case = mk(page, "WorkspaceCalendar_16", FEATURE, "Only custom events have Edit/Delete; system deadlines do not",
              "The number of Agenda rows carrying a row-actions menu must equal the 'Custom Event' chip count - "
              "system deadlines (CbC Report, CIT Return, ...) cannot be edited or deleted. (Read-only check.)",
              "1. Open Calendar\n2. Count rows that have an actions menu\n3. Compare with the 'Custom Event' count",
              "-")
    cal = open_calendar(case, page)
    with_menu = cal.rows_with_kebab()
    counts = cal.chip_counts()
    custom = counts.get("Custom Event", 0)
    total = cal.agenda_row_count()
    ok = with_menu == custom and total == counts.get("All")
    case.check("Rows with an actions menu equal the Custom Event count", ok,
               expected=f"{custom} of {counts.get('All')} rows", actual=f"{with_menu} of {total} rows",
               locator=cal.table)
    finish(case, result, ok, f"{with_menu} custom event row(s) had actions; the other {total - with_menu} did not.",
           f"{with_menu} rows had an actions menu but the Custom Event count is {custom} (rows={total}, chips={counts}).")


@pytest.mark.regression
def test_workspacecalendar_17_created_event_appears_in_dashboard_feed(page, result):
    tag = uid("xdash")
    case = mk(page, "WorkspaceCalendar_17", FEATURE, "A created event appears in the Dashboard feed",
              "Cross-module: the Dashboard's News, Alerts & Updates feed must show a newly created calendar event, "
              "and drop it once the event is deleted.",
              "1. Create an event\n2. Open Dashboard and verify it is in the feed\n3. Delete the event\n"
              "4. Re-open Dashboard and verify it is gone", f"Title: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}", days=10)
        cal.wait_row(tag, 20000)
        case.step(2, "Open the Dashboard")
        dash = WorkspaceDashboardPage(page)
        dash.goto()
        item = dash.news_cards.filter(has_text=tag)
        shown = wait_for_content(item, timeout=30000)
        case.check("Dashboard feed shows the event", shown, expected="visible", actual=shown, locator=item)
        case.step(3, "Delete the event")
        deleted = cal.delete_all_matching(tag)
        dash.goto()
        wait_for_content(dash.news_cards, timeout=20000)
        page.wait_for_timeout(2000)
        still = dash.news_cards.filter(has_text=tag).count()
        ok = saved and shown and deleted == 1 and still == 0
        case.check("Deleted event is no longer in the feed", still == 0, expected=0, actual=still)
        finish(case, result, ok, "The event appeared in the Dashboard feed and disappeared after deletion.",
               f"Cross-module check failed: shown={shown}, deleted={deleted}, still in feed={still}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_18_created_event_is_found_by_search(page, result):
    tag = uid("search")
    case = mk(page, "WorkspaceCalendar_18", FEATURE, "A created event is found by the Agenda search",
              "Typing the new event's unique title into the search box must leave exactly that row, and the 'All' "
              "chip must then read 1.",
              "1. Create an event\n2. Type its title in the search box\n3. Verify one row and All(1)",
              f"Search term: {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        case.click(cal.search_input, "Calendar search box")
        cal.type_search(tag)
        page.wait_for_timeout(1500)
        titles = cal.column_values("Nature of Compliance")
        all_count = cal.chip_counts().get("All")
        ok = saved and titles == [tag] and all_count == 1
        case.check("Search leaves exactly the created event and All(1)", ok, expected=f"[{tag}], All(1)",
                   actual=f"{titles}, All({all_count})", locator=cal.row(tag))
        finish(case, result, ok, "Search returned exactly the created event.",
               f"Search returned {titles} with All({all_count}).")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_19_duplicate_titles_are_allowed(page, result):
    tag = uid("dup")
    case = mk(page, "WorkspaceCalendar_19", FEATURE, "Two events may share the same title (no uniqueness rule)",
              "Confirmed live behaviour: the app does not enforce unique event titles - saving the same title twice "
              "for the same country and date must produce two separate rows.",
              "1. Create an event\n2. Create a second event with the identical title\n3. Verify two rows exist",
              f"Title (twice): {tag}", PRE)
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        s1 = create_event(case, cal, country, tag, f"desc {tag}")
        cal.wait_row(tag, 20000)
        s2 = create_event(case, cal, country, tag, f"desc {tag}")
        page.wait_for_timeout(2000)
        rows = cal.row(tag).count()
        ok = s1 and s2 and rows == 2
        case.check("Two rows with the same title exist", ok, expected=2, actual=rows, locator=cal.row(tag))
        finish(case, result, ok, "Both same-titled events were saved as separate rows.",
               f"Expected 2 rows for the duplicated title, found {rows} (saved: {s1}, {s2}).")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_20_past_due_date_is_accepted_and_listed(page, result):
    tag = uid("past")
    case = mk(page, "WorkspaceCalendar_20", FEATURE, "A past due date is accepted and listed",
              "Confirmed live behaviour: the Due Date picker does not block past dates. An event due 10 days ago "
              "(inside the default date range) must be saved and listed with that date.",
              "1. Create an event due today-10 days\n2. Verify the row and its Due Date",
              f"Title: {tag}; Due: today-10 days", PRE)
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), tag, f"desc {tag}", days=-10)
        shown = cal.wait_row(tag, 20000)
        got = cal.row_cells(tag).get("Due Date")
        ok = saved and shown and got == due_text(-10)
        case.check("Past-dated event is listed with its date", ok, expected=due_text(-10), actual=got,
                   locator=cal.row(tag))
        finish(case, result, ok, f"Past-dated event was saved and listed ({got}).",
               f"Past-dated event: saved={saved}, shown={shown}, Due Date='{got}'.")
    finally:
        cal.delete_all_matching(tag)
