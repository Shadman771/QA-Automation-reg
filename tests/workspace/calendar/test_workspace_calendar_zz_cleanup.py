"""Runs last in the Calendar module (file name sorts after the others):
proves no `WorkspaceQA_` event was left behind by any CRUD test, and
removes any that were. Looks across ALL jurisdictions (Filter By =
Jurisdiction), because an event in a country without an entity is hidden
from the default view."""
import pytest

from tests.workspace._flows import QA_PREFIX, finish, mk, open_calendar
from utils.wait import wait_for_content

FEATURE = "Workspace Calendar"


@pytest.mark.smoke
@pytest.mark.regression
def test_workspacecalendar_99_no_test_events_left_behind(page, result):
    case = mk(page, "WorkspaceCalendar_99", FEATURE, "No WorkspaceQA_ test event is left behind",
              "After the Calendar CRUD tests, no event carrying the WorkspaceQA_ prefix (in its title or "
              "description) may remain in any jurisdiction. Any that are found are deleted and reported as a "
              "failure of this check.",
              "1. Open Calendar and switch Filter By to Jurisdiction (all jurisdictions)\n"
              "2. Count rows containing 'WorkspaceQA_'\n3. Delete any found\n4. Verify none remain",
              f"Prefix: {QA_PREFIX}")
    cal = open_calendar(case, page)
    case.click(cal.filter_by_jurisdiction_radio, "'Jurisdiction' filter option")
    page.wait_for_timeout(2500)
    wait_for_content(cal.table_rows, timeout=20000)
    found = [r.inner_text().replace("\n", " ").replace("\t", " ").strip()[:90] for r in cal.row(QA_PREFIX).all()]
    case.check("No leftover test event before cleanup", not found, expected="0", actual=f"{len(found)}: {found}",
               locator=cal.table)
    removed = cal.delete_all_matching(QA_PREFIX) if found else 0
    cal.goto()
    case.click(cal.filter_by_jurisdiction_radio, "'Jurisdiction' filter option")
    page.wait_for_timeout(2500)
    remaining = cal.row(QA_PREFIX).count()
    ok = not found and remaining == 0
    case.check("No test event remains", remaining == 0, expected=0, actual=remaining)
    finish(case, result, ok, "No test events were left behind.",
           f"{len(found)} test event(s) had been left behind: {found}; removed {removed}, {remaining} remain.")
