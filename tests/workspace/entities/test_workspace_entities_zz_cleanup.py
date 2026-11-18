"""Runs last in the Entities module (file name sorts after the others):
proves no `WorkspaceQA_` entity was left behind by any CRUD test, and
removes any that were, so a failed/interrupted run can never leave test
data in a shared or production account."""
import pytest

from tests.workspace._flows import QA_PREFIX, finish, mk, open_entities

FEATURE = "Workspace Entities"


@pytest.mark.smoke
@pytest.mark.regression
def test_workspaceentities_99_no_test_entities_left_behind(page, result):
    case = mk(page, "WorkspaceEntities_99", FEATURE, "No WorkspaceQA_ test entity is left behind",
              "After the Entities CRUD tests, the grid must contain no entity whose name or ID carries the "
              "WorkspaceQA_ prefix. Any that are found are deleted and reported as a failure of this check.",
              "1. Open Entities\n2. Count rows containing 'WorkspaceQA_'\n3. Delete any found\n"
              "4. Verify none remain", f"Prefix: {QA_PREFIX}")
    ent = open_entities(case, page)
    case.step(2, "Count leftover test entities")
    found = [n for n in ent.entity_names() if QA_PREFIX in n]
    case.check("No leftover test entity before cleanup", not found, expected="0", actual=f"{len(found)}: {found}",
               locator=ent.table)
    removed = ent.delete_all_matching(QA_PREFIX) if found else 0
    ent.goto()
    remaining = ent.row(QA_PREFIX).count()
    ok = not found and remaining == 0
    case.check("No test entity remains", remaining == 0, expected=0, actual=remaining)
    finish(case, result, ok, "No test entities were left behind.",
           f"{len(found)} test entit(ies) had been left behind: {found}; removed {removed}, {remaining} remain.")
