"""Workspace > Entities - Add Entity wizard validation, negative and
boundary behaviour. Tests that never reach Save create nothing; the ones
that could (duplicate ID, cancel-at-last-step) still clean up in `finally`.
See pages/workspace/workspace_entities_page.py for the confirmed live rules."""
import pytest

from tests.workspace._flows import (
    ENTITY_COUNTRY, code_for, fill_legal_step, finish, go_to_ownership_step, go_to_tax_step, mk,
    open_add_entity, open_entities, pick_option, uid,
)
from utils.wait import wait_for_content

FEATURE = "Workspace Entities"

REQUIRED_CASES = [
    ("22", "ID", "id"),
    ("23", "Name", "name"),
    ("24", "Incorporation Jurisdiction", "jurisdiction"),
    ("25", "Business SIC Code", "sic"),
]


@pytest.mark.regression
@pytest.mark.parametrize("num,label,missing", REQUIRED_CASES, ids=[c[2] for c in REQUIRED_CASES])
def test_workspaceentities_required_field_missing_keeps_next_disabled(page, result, num, label, missing):
    name = uid("req")
    case = mk(page, f"WorkspaceEntities_{num}", FEATURE, f"'Next' stays disabled when only {label} is missing",
              f"With every other Legal Information field filled and only {label} left empty, the wizard's 'Next' "
              "button must stay disabled.",
              f"1. Open Add Entity\n2. Fill every required field except {label}\n3. Verify 'Next' is disabled\n"
              "4. Close the wizard", f"Missing field: {label}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    case.step(2, f"Fill every required field except {label}")
    if missing != "id":
        case.fill(ent.modal_id_input, code_for(name), "ID field")
    if missing != "name":
        case.fill(ent.modal_name_input, name, "Name field")
    if missing != "jurisdiction":
        pick_option(case, ent, ent.jurisdiction_combo, ENTITY_COUNTRY, "Incorporation Jurisdiction")
    if missing != "sic":
        case.click(ent.sic_combo, "Business SIC Code picker")
        wait_for_content(ent.options, timeout=10000)
        case.click(ent.options.first, "first SIC code option")
    case.step(3, "Verify 'Next' is disabled")
    disabled = ent.is_next_button_disabled()
    case.check(f"'Next' is disabled while {label} is empty", disabled, expected="disabled", actual=disabled,
               locator=ent.modal_next_button)
    ent.dismiss_any_modal()
    finish(case, result, disabled, f"'Next' stayed disabled with {label} missing.",
           f"'Next' was enabled although {label} was empty.")


@pytest.mark.regression
def test_workspaceentities_26_whitespace_only_id_and_name_are_rejected(page, result):
    case = mk(page, "WorkspaceEntities_26", FEATURE, "Whitespace-only ID and Name do not satisfy the required check",
              "Typing only spaces into ID and Name (with jurisdiction and SIC code chosen) must keep 'Next' disabled.",
              "1. Open Add Entity\n2. Enter spaces for ID and Name, choose jurisdiction and SIC\n"
              "3. Verify 'Next' is disabled", "ID: '   '; Name: '   '")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    fill_legal_step(case, ent, "   ", "   ")
    disabled = ent.is_next_button_disabled()
    case.check("'Next' is disabled for whitespace-only ID/Name", disabled, expected="disabled", actual=disabled,
               locator=ent.modal_next_button)
    ent.dismiss_any_modal()
    finish(case, result, disabled, "Whitespace-only ID and Name were rejected.",
           "'Next' was enabled for whitespace-only ID and Name.")


@pytest.mark.regression
def test_workspaceentities_27_next_enables_and_advances_when_legal_step_is_complete(page, result):
    name = uid("next")
    case = mk(page, "WorkspaceEntities_27", FEATURE, "'Next' enables once the Legal step is complete and advances",
              "Filling every required Legal Information field must enable 'Next', and clicking it must show the "
              "Ownership Information step.",
              "1. Open Add Entity\n2. Fill all required Legal fields\n3. Verify 'Next' is enabled\n"
              "4. Click Next and verify the Ownership step\n5. Close without saving", f"Name: {name}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    before = ent.is_next_button_disabled()
    fill_legal_step(case, ent, code_for(name), name)
    enabled = not ent.is_next_button_disabled()
    case.check("'Next' was disabled before and is enabled after filling the step", before and enabled,
               expected="disabled -> enabled", actual=f"disabled before={before}, enabled after={enabled}")
    advanced = go_to_ownership_step(case, ent)
    ok = before and enabled and advanced
    case.check("Ownership Information step is shown", advanced, expected="visible", actual=advanced,
               locator=ent.step_ownership_heading)
    ent.dismiss_any_modal()
    finish(case, result, ok, "'Next' enabled on a complete Legal step and advanced to Ownership.",
           f"Wizard did not advance: disabled before={before}, enabled={enabled}, advanced={advanced}.")


@pytest.mark.regression
def test_workspaceentities_28_sub_national_enables_after_jurisdiction_is_chosen(page, result):
    case = mk(page, "WorkspaceEntities_28", FEATURE, "Sub-National is disabled until a jurisdiction is chosen",
              "The Sub-National picker depends on Incorporation Jurisdiction: `aria-disabled` must be true before "
              "a jurisdiction is selected and false afterwards.",
              "1. Open Add Entity\n2. Read Sub-National's aria-disabled\n3. Choose a jurisdiction\n"
              "4. Read aria-disabled again", f"Jurisdiction: {ENTITY_COUNTRY}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    before = ent.sub_national_combo.get_attribute("aria-disabled")
    pick_option(case, ent, ent.jurisdiction_combo, ENTITY_COUNTRY, "Incorporation Jurisdiction")
    after = ent.sub_national_combo.get_attribute("aria-disabled")
    ok = before == "true" and after == "false"
    case.check("Sub-National goes from disabled to enabled", ok, expected="true -> false",
               actual=f"{before} -> {after}", locator=ent.sub_national_combo)
    ent.dismiss_any_modal()
    finish(case, result, ok, "Sub-National enabled once a jurisdiction was chosen.",
           f"Sub-National aria-disabled went {before} -> {after}.")


@pytest.mark.regression
def test_workspaceentities_29_ownership_step_requires_owner_or_unassigned(page, result):
    name = uid("own")
    case = mk(page, "WorkspaceEntities_29", FEATURE, "Ownership step blocks 'Next' until an owner or 'unassigned' is set",
              "On the Ownership step 'Next' must be disabled by default (no owner chosen) and become enabled once "
              "'Owner unknown / not assigned yet' is selected.",
              "1. Open Add Entity and complete the Legal step\n2. Verify 'Next' is disabled on Ownership\n"
              "3. Select 'Owner unknown / not assigned yet'\n4. Verify 'Next' is enabled", f"Name: {name}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    fill_legal_step(case, ent, code_for(name), name)
    go_to_ownership_step(case, ent)
    default_disabled = ent.is_next_button_disabled()
    case.check("'Next' is disabled with no owner chosen", default_disabled, expected="disabled",
               actual=default_disabled)
    case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
    page.wait_for_timeout(400)
    enabled = not ent.is_next_button_disabled()
    ok = default_disabled and enabled
    case.check("'Next' is enabled after choosing 'unassigned'", enabled, expected="enabled", actual=enabled)
    ent.dismiss_any_modal()
    finish(case, result, ok, "Ownership step enforced an owner-or-unassigned choice.",
           f"Ownership gating wrong: disabled by default={default_disabled}, enabled after unassigned={enabled}.")


def _two_owners(case, ent, page):
    """Complete Legal, pick owner 1, add owner 2. Returns (owner1, owner2 options)."""
    name = uid("pct")
    open_add_entity(case, ent)
    fill_legal_step(case, ent, code_for(name), name)
    go_to_ownership_step(case, ent)
    case.click(ent.owner_combos.first, "Owner 1 picker")
    wait_for_content(ent.options, timeout=10000)
    owner1 = ent.options.nth(1).inner_text().strip()
    case.click(ent.options.nth(1), f"owner 1 option '{owner1}'")
    case.click(ent.add_another_owner_button, "'Add Another Owner' button")
    case.click(ent.owner_combos.nth(1), "Owner 2 picker")
    wait_for_content(ent.options, timeout=10000)
    offered = [t.strip() for t in ent.options.all_inner_texts()]
    case.click(ent.options.nth(2), "owner 2 option")
    return owner1, offered


@pytest.mark.regression
def test_workspaceentities_30_ownership_must_total_exactly_100_percent(page, result):
    case = mk(page, "WorkspaceEntities_30", FEATURE, "Owners must total exactly 100% before 'Next' enables",
              "With two owners, 60% + 30% must show Total Ownership 90.00% and keep 'Next' disabled; changing to "
              "60% + 40% must show 100.00% and enable 'Next'.",
              "1. Open Add Entity, complete Legal, add two owners\n2. Enter 60 and 30 - verify total and Next\n"
              "3. Enter 60 and 40 - verify total and Next\n4. Close without saving",
              "Ownership: 60/30 then 60/40 (owners are existing entities, only referenced)")
    ent = open_entities(case, page)
    _two_owners(case, ent, page)
    case.step(2, "Enter 60% and 30%")
    case.fill(ent.ownership_pct_inputs.nth(0), "60", "Owner 1 ownership %")
    case.fill(ent.ownership_pct_inputs.nth(1), "30", "Owner 2 ownership %")
    page.wait_for_timeout(500)
    total_90, disabled_90 = ent.total_ownership(), ent.is_next_button_disabled()
    case.check("60 + 30 totals 90.00% and blocks 'Next'", total_90 == "90.00%" and disabled_90,
               expected="90.00%, Next disabled", actual=f"{total_90}, Next disabled={disabled_90}")
    case.step(3, "Change to 60% and 40%")
    case.fill(ent.ownership_pct_inputs.nth(1), "40", "Owner 2 ownership %")
    page.wait_for_timeout(500)
    total_100, disabled_100 = ent.total_ownership(), ent.is_next_button_disabled()
    ok = total_90 == "90.00%" and disabled_90 and total_100 == "100.00%" and not disabled_100
    case.check("60 + 40 totals 100.00% and enables 'Next'", total_100 == "100.00%" and not disabled_100,
               expected="100.00%, Next enabled", actual=f"{total_100}, Next disabled={disabled_100}")
    ent.dismiss_any_modal()
    finish(case, result, ok, "The 100% ownership rule was enforced.",
           f"Totals/gating wrong: 60/30 -> {total_90}, disabled={disabled_90}; 60/40 -> {total_100}, disabled={disabled_100}.")


@pytest.mark.regression
@pytest.mark.parametrize("num,value", [("31", "150"), ("32", "-5")], ids=["above_100", "negative"])
def test_workspaceentities_ownership_percentage_out_of_range_is_rejected(page, result, num, value):
    case = mk(page, f"WorkspaceEntities_{num}", FEATURE, f"Ownership % of {value} is rejected (allowed 0.01-100)",
              f"Entering {value} as an ownership percentage must show 'Ownership Percentage must between 0.01 and "
              "100' and must not be accepted as the field's value.",
              f"1. Open Add Entity, complete Legal, add two owners at 60/40\n2. Enter {value} for owner 2\n"
              "3. Verify the range error and that the value was not accepted\n4. Close without saving",
              f"Ownership %: {value}")
    ent = open_entities(case, page)
    _two_owners(case, ent, page)
    case.fill(ent.ownership_pct_inputs.nth(0), "60", "Owner 1 ownership %")
    case.fill(ent.ownership_pct_inputs.nth(1), "40", "Owner 2 ownership %")
    case.step(2, f"Enter {value} for owner 2")
    case.fill(ent.ownership_pct_inputs.nth(1), value, "Owner 2 ownership %")
    page.wait_for_timeout(500)
    # The message is attached to the field but not rendered as a visible
    # block (confirmed live), so its presence in the DOM is what is checked.
    error = ent.pct_range_error.count() > 0
    stored = ent.ownership_pct_inputs.nth(1).input_value()
    total = ent.total_ownership()
    ok = error and stored == "40" and total == "100.00%"
    case.check("Range error is raised, the field keeps its last valid value and the total is unchanged", ok,
               expected="error present, value 40, total 100.00%",
               actual=f"error={error}, value='{stored}', total={total}", locator=ent.ownership_pct_inputs.nth(1))
    ent.dismiss_any_modal()
    finish(case, result, ok, f"Ownership % {value} was rejected with the range error.",
           f"Out-of-range % handling wrong: error present={error}, field value='{stored}', total={total}.")


@pytest.mark.regression
def test_workspaceentities_33_second_owner_list_excludes_first_owner(page, result):
    case = mk(page, "WorkspaceEntities_33", FEATURE, "An already chosen owner is not offered for the next owner row",
              "After choosing owner 1, the Owner 2 picker must not offer that same entity again (no duplicate owners).",
              "1. Open Add Entity, complete Legal, choose owner 1\n2. Add another owner and open its picker\n"
              "3. Verify owner 1 is not in the list", "Owner 1: second option of the live owner list")
    ent = open_entities(case, page)
    owner1, offered = _two_owners(case, ent, page)
    ok = bool(owner1) and bool(offered) and owner1 not in offered
    case.check("Owner 2's options do not include owner 1", ok, expected=f"'{owner1}' absent",
               actual=f"{len(offered)} options, contains owner 1={owner1 in offered}")
    ent.dismiss_any_modal()
    finish(case, result, ok, f"'{owner1}' was correctly excluded from the second owner list.",
           f"'{owner1}' was still offered as owner 2 (options: {offered[:6]}...).")


@pytest.mark.regression
def test_workspaceentities_34_back_preserves_legal_step_data(page, result):
    name = uid("back")
    case = mk(page, "WorkspaceEntities_34", FEATURE, "'Back' from Ownership preserves the Legal step's data",
              "Going Next then Back must return to Legal Information with the typed ID, Name and jurisdiction intact.",
              "1. Open Add Entity and complete Legal\n2. Next, then Back\n3. Verify ID, Name and jurisdiction",
              f"Name: {name}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    fill_legal_step(case, ent, code_for(name), name)
    go_to_ownership_step(case, ent)
    case.click(ent.modal_back_button, "'Back' button")
    back = wait_for_content(ent.step_legal_heading, timeout=10000)
    got = (ent.modal_id_input.input_value(), ent.modal_name_input.input_value(),
           ent.jurisdiction_combo.inner_text().strip())
    want = (code_for(name), name, ENTITY_COUNTRY)
    ok = back and got == want
    case.check("Legal step still holds the entered values", ok, expected=str(want), actual=str(got),
               locator=ent.modal_name_input)
    ent.dismiss_any_modal()
    finish(case, result, ok, "'Back' preserved the Legal step's data.", f"After Back the fields were {got}.")


@pytest.mark.regression
@pytest.mark.parametrize("num,step", [("35", "Legal"), ("36", "Ownership"), ("37", "Tax")],
                         ids=["at_legal", "at_ownership", "at_tax"])
def test_workspaceentities_cancelling_wizard_discards_entity(page, result, num, step):
    name = uid("cancel")
    case = mk(page, f"WorkspaceEntities_{num}", FEATURE, f"Cancelling the wizard at the {step} step creates nothing",
              f"Closing the Add Entity wizard (Escape) while on the {step} step must discard everything: after a "
              "reload no entity with that name exists and the row count is unchanged.",
              f"1. Record the row count\n2. Open Add Entity and advance to the {step} step with valid data\n"
              "3. Press Escape\n4. Reload and verify nothing was created", f"Name: {name}")
    ent = open_entities(case, page)
    try:
        baseline = ent.entity_row_count()
        open_add_entity(case, ent)
        fill_legal_step(case, ent, code_for(name), name)
        if step in ("Ownership", "Tax"):
            go_to_ownership_step(case, ent)
            case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
        if step == "Tax":
            go_to_tax_step(case, ent)
        case.step(3, "Press Escape to cancel the wizard")
        case.action("Pressing Escape", kind="type")
        page.keyboard.press("Escape")
        closed = ent.wait_modal_closed(10000)
        case.step(4, "Reload and verify nothing was created")
        ent.goto()
        wait_for_content(ent.table_rows, timeout=20000)
        rows, count = ent.row(name).count(), ent.entity_row_count()
        ok = closed and rows == 0 and count == baseline
        case.check("No entity was created and the row count is unchanged", ok,
                   expected=f"0 matching rows, {baseline} total", actual=f"{rows} matching rows, {count} total")
        finish(case, result, ok, f"Cancelling at the {step} step discarded the entity.",
               f"Cancel at {step} left data behind: closed={closed}, matching rows={rows}, count {baseline}->{count}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_38_duplicate_entity_id_is_rejected_on_save(page, result):
    name = uid("dupid")
    case = mk(page, "WorkspaceEntities_38", FEATURE, "Saving with an existing Entity ID is rejected",
              "Completing the wizard with an ID that already belongs to another entity must fail on Save with "
              "'Entity ID already exists', keep the wizard open, and create no row.",
              "1. Read an existing entity's ID\n2. Run the wizard with that ID and a new name, Save\n"
              "3. Verify the error and that the wizard stays open\n4. Reload and verify no row was created",
              f"Name: {name}; ID: an existing entity's ID, read at runtime")
    ent = open_entities(case, page)
    try:
        existing_id = [v for v in ent.column_values("ID") if v][0]
        open_add_entity(case, ent)
        fill_legal_step(case, ent, existing_id, name)
        go_to_ownership_step(case, ent)
        case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
        go_to_tax_step(case, ent)
        case.step(2, f"Save with the duplicate ID '{existing_id}'")
        case.click(ent.modal_save_button, "'Save' button")
        error = wait_for_content(ent.duplicate_id_error, timeout=15000)
        still_open = ent.step_tax_heading.is_visible()
        case.check("'Entity ID already exists' is shown and the wizard stays open", error and still_open,
                   expected="error visible, wizard open", actual=f"error={error}, wizard open={still_open}",
                   locator=ent.duplicate_id_error)
        case.step(4, "Reload and verify no row was created")
        ent.goto()
        wait_for_content(ent.table_rows, timeout=20000)
        rows = ent.row(name).count()
        ok = error and still_open and rows == 0
        case.check("No entity was created", rows == 0, expected=0, actual=rows)
        finish(case, result, ok, f"Duplicate ID '{existing_id}' was rejected and nothing was created.",
               f"Duplicate-ID handling wrong: error={error}, wizard open={still_open}, rows created={rows}.")
    finally:
        ent.delete_all_matching(name)


@pytest.mark.regression
def test_workspaceentities_39_tax_step_defaults_from_legal_step(page, result):
    name = uid("taxdef")
    case = mk(page, "WorkspaceEntities_39", FEATURE, "Tax step defaults Tax Resident Jurisdiction and Financial Year End",
              "On the Tax step, Tax Resident Jurisdiction must default to the chosen Incorporation Jurisdiction and "
              "Financial Year End must be pre-filled, so Save is available without further input.",
              "1. Open Add Entity, complete Legal and Ownership\n2. Verify the Tax step's defaults\n"
              "3. Close without saving", f"Jurisdiction: {ENTITY_COUNTRY}")
    ent = open_entities(case, page)
    open_add_entity(case, ent)
    fill_legal_step(case, ent, code_for(name), name)
    go_to_ownership_step(case, ent)
    case.click(ent.owner_unassigned_radio, "'Owner unknown / not assigned yet' option")
    go_to_tax_step(case, ent)
    residence = ent.tax_residence_combo.inner_text().strip()
    fye = ent.financial_year_end_input.input_value()
    save_enabled = ent.modal_save_button.get_attribute("disabled") is None
    ok = residence == ENTITY_COUNTRY and bool(fye.strip()) and save_enabled
    case.check("Tax residence defaults to the incorporation jurisdiction, FYE is pre-filled, Save is enabled", ok,
               expected=f"{ENTITY_COUNTRY}, non-empty FYE, Save enabled",
               actual=f"{residence}, FYE='{fye}', Save enabled={save_enabled}", locator=ent.tax_residence_combo)
    ent.dismiss_any_modal()
    finish(case, result, ok, f"Tax step defaulted to {residence} with Financial Year End '{fye}'.",
           f"Tax defaults wrong: residence='{residence}', FYE='{fye}', Save enabled={save_enabled}.")
