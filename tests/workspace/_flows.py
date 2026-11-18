"""Shared building blocks for the Workspace CRUD tests (not collected by
pytest - no `test_` prefix). Every user-visible step goes through `Case`
so it is highlighted, logged and captured as evidence; only teardown
cleanup uses the page objects' own `delete_all_matching()`.

Data-safety contract for every test in tests/workspace/:
  - anything created is named `WorkspaceQA_<tag>_<timestamp>` (`uid()`);
  - it is removed in a `finally` block even when the test fails;
  - pre-existing entities/events are never edited or deleted."""
import datetime
import time

from pages.workspace.workspace_calendar_page import WorkspaceCalendarPage, agenda_date
from pages.workspace.workspace_dashboard_page import WorkspaceDashboardPage
from pages.workspace.workspace_entities_page import WorkspaceEntitiesPage
from utils.auth import perform_login
from utils.case import Case
from utils.wait import wait_for_content

QA_PREFIX = "WorkspaceQA_"
ENTITY_COUNTRY = "Albania"  # present in the wizard's country list on RC, Staging and Live


def uid(tag: str) -> str:
    """Unique, recognisable test-data name: WorkspaceQA_<tag>_<epoch>."""
    return f"{QA_PREFIX}{tag}_{int(time.time())}"


def code_for(name: str) -> str:
    """A unique entity ID derived from the same timestamp as its name."""
    return "WQA" + name.rsplit("_", 1)[-1][-7:]


def mk(page, cid, feature, title, description, steps, test_data="-", precondition="User is logged in."):
    return Case(page, cid, feature, title, description=description, precondition=precondition,
                test_data=test_data, steps=steps)


def finish(case, result, ok, good, bad):
    actual = good if ok else bad
    result(case, actual, ok)
    assert ok, actual


# ---------------------------------------------------------------- open pages
def open_entities(case, page) -> WorkspaceEntitiesPage:
    perform_login(case, page)
    ent = WorkspaceEntitiesPage(page)
    case.action("Navigating to Workspace > Entities", kind="navigate")
    ent.goto()
    wait_for_content(ent.table_rows, timeout=30000)
    return ent


def open_calendar(case, page) -> WorkspaceCalendarPage:
    perform_login(case, page)
    cal = WorkspaceCalendarPage(page)
    case.action("Navigating to Workspace > Calendar", kind="navigate")
    cal.goto()
    wait_for_content(cal.table_rows, timeout=30000)
    return cal


def open_dashboard(case, page) -> WorkspaceDashboardPage:
    perform_login(case, page)
    dash = WorkspaceDashboardPage(page)
    case.action("Navigating to Workspace > Dashboard", kind="navigate")
    dash.goto()
    wait_for_content(dash.news_cards, timeout=30000)
    return dash


# ------------------------------------------------------------------ entities
def pick_option(case, po, combo, text, label):
    """Open an rsuite picker, type to filter, click the matching option."""
    case.click(combo, f"{label} picker")
    wait_for_content(po.options, timeout=10000)
    case.action(f"Typing '{text}' to filter the {label} options", kind="type")
    po.page.keyboard.type(text, delay=30)
    case.click(po.option(text), f"'{text}' option")


def open_add_entity(case, ent):
    case.click(ent.add_entity_button, "'Add Entity' button")
    wait_for_content(ent.modal_id_input, timeout=15000)


def fill_legal_step(case, ent, code, name, country=ENTITY_COUNTRY):
    case.fill(ent.modal_id_input, code, "ID field")
    case.fill(ent.modal_name_input, name, "Name field")
    pick_option(case, ent, ent.jurisdiction_combo, country, "Incorporation Jurisdiction")
    case.click(ent.sic_combo, "Business SIC Code picker")
    wait_for_content(ent.options, timeout=10000)
    case.click(ent.options.first, "first SIC code option")


def go_to_ownership_step(case, ent):
    case.click(ent.modal_next_button, "'Next' (to Ownership)")
    return wait_for_content(ent.step_ownership_heading, timeout=10000)


def go_to_tax_step(case, ent):
    case.click(ent.modal_next_button, "'Next' (to Tax)")
    return wait_for_content(ent.step_tax_heading, timeout=10000)


def create_entity(case, ent, name, code=None, country=ENTITY_COUNTRY, owner=None,
                  tct="Private Limited Company") -> bool:
    """Runs the whole Add Entity wizard and saves. Returns True once the
    wizard has closed and the new row is visible in the grid."""
    open_add_entity(case, ent)
    fill_legal_step(case, ent, code or code_for(name), name, country)
    go_to_ownership_step(case, ent)
    if owner:
        case.click(ent.owner_combos.first, "Owning Entity picker")
        wait_for_content(ent.options, timeout=10000)
        case.click(ent.option(owner), f"owner '{owner}' option")
    else:
        case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
    go_to_tax_step(case, ent)
    if tct:
        case.click(ent.tax_characterization(tct), f"'{tct}' tax characterization")
    case.click(ent.modal_save_button, "'Save' button")
    closed = ent.wait_modal_closed(20000)
    return closed and ent.wait_row(name, 20000)


def open_row_action(case, po, name, action):
    """`action` "Edit" or "Delete" from a row's kebab menu."""
    case.click(po.row_kebab(name), f"row actions menu of '{name[:40]}'")
    item = po.menu_edit if action == "Edit" else po.menu_delete
    case.click(item.first, f"'{action}' menu item")


# ------------------------------------------------------------------ calendar
def due(days: int) -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=days)


def live_country(cal) -> str:
    """A jurisdiction that already has events under the default Entity
    filter - i.e. one the account has an entity in - read at runtime, so a
    created event is visible in the default Agenda on every environment."""
    values = [v for v in cal.column_values("Tax Residence") if v]
    return values[0] if values else ""


def pick_due_date(case, cal, d: datetime.date):
    case.click(cal.modal_due_date_input, "Due Date field (opens the date picker)")
    wait_for_content(cal.date_ok_button, timeout=10000)
    forward = d >= datetime.date.today().replace(day=1)
    for _ in range(14):
        if cal.date_cell_in_month(d):
            break
        nav = cal.date_next_month if forward else cal.date_prev_month
        case.click(nav.first, "next month" if forward else "previous month")
    case.click(cal.date_cell(d).first, f"day cell {d.strftime('%d %b %Y')}")
    case.click(cal.date_ok_button.first, "date picker 'OK'")


def open_create_event(case, cal):
    case.click(cal.create_event_button, "'Create New Event' button")
    wait_for_content(cal.modal_title_input, timeout=15000)


def fill_event(case, cal, country=None, title=None, description=None, days=None, link=None):
    if country:
        pick_option(case, cal, cal.modal_country_combo, country, "Select Country")
    if title is not None:
        case.fill(cal.modal_title_input, title, "Nature of Compliance field")
    if description is not None:
        case.fill(cal.modal_description_input, description, "Description field")
    if days is not None:
        pick_due_date(case, cal, due(days))
    if link is not None:
        case.fill(cal.modal_external_link_input, link, "External Link field")


def create_event(case, cal, country, title, description, days=20, link=None) -> bool:
    """Creates a single custom event. Returns True once the modal closed."""
    open_create_event(case, cal)
    fill_event(case, cal, country, title, description, days, link)
    case.click(cal.modal_save_button, "'Save' button")
    return cal.wait_modal_closed(20000)


def due_text(days: int) -> str:
    return agenda_date(due(days))
