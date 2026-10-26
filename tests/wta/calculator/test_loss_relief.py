"""Calculators > Loss Relief Calculator (/wta/LossCalculator).

New module, built via live DOM discovery (scratchpad scripts, not part
of the suite) - no QA-sheet rows exist for this page. Unlike every other
Calculator sub-page, there is no "Calculate" button and no Generate
Memo/Get Forms/Add to Project action row (confirmed live) - every field
recalculates live as you type. Covers the default "Ordinary loss relief"
mode in depth, including a purely-arithmetic, independently-reproducible
calculation-validation anchor (see pages/wta/calculator_loss_relief_page.py
docstring), plus structural coverage of "Capital loss relief" mode
(including its real, live-confirmed duplicate-label quirk) and "By
Entity" mode."""
import pytest

from pages.wta.calculator_menu import CalculatorMenu
from pages.wta.calculator_loss_relief_page import LossReliefPage, ORDINARY_FIELD_LABELS
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - Loss Relief"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > Loss Relief Calculator", kind="navigate")
    lr = LossReliefPage(page)
    CalculatorMenu(page).open_item("Loss Relief Calculator", ready_locator=lr.instructions_heading)
    return lr


def _select_au_2023(case, page, lr):
    case.click(lr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    lr.open_and_pick(lr.source_jurisdiction_combobox(), "Australia")
    case.click(lr.tax_year_combobox(), "'Tax Year' select")
    lr.open_and_pick(lr.tax_year_combobox(), "01 July 2023")
    page.wait_for_timeout(500)


def _enter_amount(case, page, field, value, label):
    case.click(field, label)
    field.press_sequentially(value, delay=15)
    page.wait_for_timeout(700)


@pytest.mark.smoke
def test_lossrelief_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "LossRelief_01", FEATURE, "Loss Relief Calculator opens from the Calculators dropdown",
        description="Clicking 'Loss Relief Calculator' in the Calculators dropdown must land on "
                     "/wta/LossCalculator with the 'Information' panel and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > Loss Relief Calculator\n2. Verify the URL and instructions banner",
    )
    lr = _login_and_open(case, page)
    case.step(2, "Verify URL and instructions banner")
    url_ok = "/wta/LossCalculator" in page.url
    banner_ok = case.verify_visible(lr.instructions_heading, "'How to complete this calculation' heading")
    ok = url_ok and banner_ok
    case.check("Loss Relief Calculator page loads with its instructions banner", ok,
               expected="url contains /wta/LossCalculator, banner visible",
               actual=f"url={page.url}, banner={banner_ok}")

    actual = ("Loss Relief Calculator opened correctly with its instructions banner visible." if ok else
              "Loss Relief Calculator did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_lossrelief_02_initial_state_defaults(page, result):
    case = Case(
        page, "LossRelief_02", FEATURE, "Initial state: 'By Jurisdiction' and 'Ordinary loss relief' checked",
        description="On first load, 'By Jurisdiction' and 'Ordinary loss relief' must both be the checked "
                     "defaults, with no Calculate/Generate Memo/Get Forms/Add to Project buttons present "
                     "(confirmed live: this page has none of those, unlike every other Calculator sub-page).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Loss Relief Calculator\n"
              "2. Verify default radios and the absence of action buttons",
    )
    lr = _login_and_open(case, page)
    case.step(2, "Verify default radios and absent action buttons")
    # Confirmed live: the 4 radios are NOT interleaved by visual row -
    # [0]=By Jurisdiction, [1]=By Entity, [2]=Ordinary loss relief,
    # [3]=Capital loss relief (see page object docstring).
    radios = page.locator("input[type='radio']")
    mode_ok = radios.nth(0).is_checked()
    loss_mode_ok = radios.nth(2).is_checked()
    no_calculate = page.get_by_role("button", name="Calculate").count() == 0
    no_memo = page.get_by_role("button", name="Generate Memo").count() == 0
    ok = mode_ok and loss_mode_ok and no_calculate and no_memo
    case.check("Defaults checked and no action buttons present", ok,
               expected="By Jurisdiction + Ordinary checked, no action buttons",
               actual=f"mode={mode_ok}, loss_mode={loss_mode_ok}, no_calc={no_calculate}, no_memo={no_memo}")

    actual = ("Loss Relief Calculator correctly starts with the expected defaults and no action buttons." if ok
              else "The initial state did not match expectations.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_03_source_jurisdiction_lists_real_countries(page, result):
    case = Case(
        page, "LossRelief_03", FEATURE, "'Source Jurisdiction' lists real countries",
        description="Opening 'Source Jurisdiction' must list real country names including Australia.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator\n2. Open 'Source Jurisdiction'\n"
              "3. Verify real countries are listed",
    )
    lr = _login_and_open(case, page)
    case.step(2, "Open 'Source Jurisdiction'")
    case.click(lr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    options = lr.open_listbox_options(lr.source_jurisdiction_combobox())

    case.step(3, "Verify real countries are listed")
    count = options.count()
    all_text = [options.nth(i).inner_text() for i in range(count)]
    ok = count > 50 and "Australia" in all_text
    case.check("'Source Jurisdiction' lists real countries including Australia", ok,
               expected="> 50 options including Australia", actual=f"count={count}")

    actual = (f"'Source Jurisdiction' correctly lists {count} real countries." if ok else
              f"'Source Jurisdiction' did not list the expected real countries (count={count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_04_tax_year_lists_real_date_ranges(page, result):
    case = Case(
        page, "LossRelief_04", FEATURE, "'Tax Year' lists real date-range options",
        description="After selecting a Source Jurisdiction, 'Tax Year' must list real date-range options "
                     "(e.g. '01 July 2023 - 30 June 2024'), not plain year numbers.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open Loss Relief Calculator, select Australia\n2. Open 'Tax Year'\n"
              "3. Verify real date-range options are listed",
    )
    lr = _login_and_open(case, page)
    case.click(lr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    lr.open_and_pick(lr.source_jurisdiction_combobox(), "Australia")
    case.step(2, "Open 'Tax Year'")
    case.click(lr.tax_year_combobox(), "'Tax Year' select")
    options = lr.open_listbox_options(lr.tax_year_combobox())

    case.step(3, "Verify real date-range options are listed")
    count = options.count()
    first_text = options.first.inner_text() if count else ""
    ok = count > 0 and "-" in first_text and any(ch.isdigit() for ch in first_text)
    case.check("'Tax Year' lists real date-range options", ok,
               expected="date-range format with a '-'", actual=f"count={count}, first={first_text!r}")

    actual = (f"'Tax Year' correctly lists {count} real date-range options (e.g. {first_text!r})." if ok else
              f"'Tax Year' did not list the expected date-range options (count={count}, first={first_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_05_ordinary_mode_lists_all_expected_fields(page, result):
    case = Case(
        page, "LossRelief_05", FEATURE, "Ordinary loss relief mode shows all 13 expected fields",
        description="With Australia/01 July 2023-30 June 2024 selected and 'Ordinary loss relief' the "
                     "default mode, all 13 expected field labels must be visible.",
        precondition="User is logged in, Australia/2023-2024 selected.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024\n"
              "2. Verify all 13 Ordinary-mode field labels are visible",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)

    case.step(2, "Verify all 13 Ordinary-mode field labels are visible")
    missing = [lbl for lbl in ORDINARY_FIELD_LABELS if not case.verify_visible(
        page.get_by_text(lbl, exact=True), f"'{lbl}' label")]
    ok = not missing
    case.check("All 13 expected Ordinary-mode field labels are visible", ok,
               expected="all 13 visible", actual=f"missing={missing}" if missing else "all present")

    actual = ("All 13 expected Ordinary loss relief fields are visible." if ok else
              f"Missing expected fields: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_lossrelief_06_calculation_chain_matches_independent_arithmetic(page, result):
    case = Case(
        page, "LossRelief_06", FEATURE, "The live computed fields match an independent arithmetic calculation",
        description="Entering Losses brought forward=1000, Tax losses in current period=500, Losses "
                     "actually offset in current year=300 must live-compute: Brought forward losses "
                     "available=1,000, Total Losses available=1,500, Losses available for offset=1,500, "
                     "Losses available for carry forward=1,200, Total losses carried forward=1,200 - each "
                     "independently recomputed in Python from the same formulas, not compared to itself.",
        precondition="User is logged in, Australia/2023-2024 selected, Ordinary loss relief mode.",
        test_data="Losses brought forward=1000, Tax losses in current period=500, "
                  "Losses actually offset=300",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024\n"
              "2. Enter the 3 input amounts\n"
              "3. Independently compute the expected chain\n"
              "4. Verify every computed field matches",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)

    case.step(2, "Enter Losses brought forward=1000, Tax losses in current period=500, "
                 "Losses actually offset in current year=300")
    _enter_amount(case, page, lr.ordinary_field("Losses brought forward"), "1000", "'Losses brought forward' field")
    _enter_amount(case, page, lr.ordinary_field("Tax losses in current period"), "500",
                  "'Tax losses in current period' field")
    _enter_amount(case, page, lr.ordinary_field("Losses actually offset in current year"), "300",
                  "'Losses actually offset in current year' field")
    page.wait_for_timeout(800)

    case.step(3, "Independently compute the expected chain")
    losses_brought_forward = 1000
    restriction_brought_forward = 0
    brought_forward_available = losses_brought_forward - restriction_brought_forward
    tax_losses_current_period = 500
    total_available_current_year = brought_forward_available + tax_losses_current_period
    surrendered = carried_back = restriction_offset = 0
    available_for_offset = total_available_current_year - surrendered - carried_back - restriction_offset
    actually_offset = 300
    available_for_carry_forward = available_for_offset - actually_offset
    restriction_carried_forward = 0
    total_carried_forward = available_for_carry_forward - restriction_carried_forward

    case.step(4, "Verify every computed field matches the independent calculation")

    def val(label):
        return lr.ordinary_field(label).input_value().replace(",", "")

    actual_values = {
        "Brought forward losses available for offset in current period": val(
            "Brought forward losses available for offset in current period"),
        "Total Losses available in current year": val("Total Losses available in current year"),
        "Losses available for offset in current year": val("Losses available for offset in current year"),
        "Losses available for carry forward": val("Losses available for carry forward"),
        "Total losses carried forward": val("Total losses carried forward"),
    }
    expected_values = {
        "Brought forward losses available for offset in current period": str(brought_forward_available),
        "Total Losses available in current year": str(total_available_current_year),
        "Losses available for offset in current year": str(available_for_offset),
        "Losses available for carry forward": str(available_for_carry_forward),
        "Total losses carried forward": str(total_carried_forward),
    }
    ok = actual_values == expected_values
    case.check("All computed fields match the independent arithmetic calculation", ok,
               expected=expected_values, actual=actual_values)

    actual = ("All computed fields correctly matched the independent arithmetic calculation." if ok else
              f"Computed fields did not match (expected {expected_values}, got {actual_values}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_07_offset_exceeding_available_field_hint_present(page, result):
    case = Case(
        page, "LossRelief_07", FEATURE, "'Losses actually offset' field shows its documented validation hint",
        description="The 'Losses actually offset in current year' field must show its hint text: 'Losses "
                     "actually offset must not exceed Losses available for offset in current year.'",
        precondition="User is logged in, Australia/2023-2024 selected.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024\n"
              "2. Verify the hint text under 'Losses actually offset in current year' is visible",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)

    case.step(2, "Verify the hint text is visible")
    hint = page.get_by_text("Losses actually offset must not exceed Losses available for offset in current year",
                             exact=False)
    ok = case.verify_visible(hint, "offset validation hint")
    case.check("The offset validation hint is visible", ok, expected="visible", actual=f"visible={ok}")

    actual = ("The offset validation hint is correctly documented on the page." if ok else
              "The expected offset validation hint was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_lossrelief_08_mode_toggle_switches_to_capital_loss_fields(page, result):
    case = Case(
        page, "LossRelief_08", FEATURE, "Switching to 'Capital loss relief' shows the capital-specific fields",
        description="Clicking 'Capital loss relief' must swap the Ordinary-mode fields for Capital-mode "
                     "fields (e.g. 'Capital losses brought forward', 'Excess capital losses to carry "
                     "forward').",
        precondition="User is logged in, Australia/2023-2024 selected.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024\n"
              "2. Click 'Capital loss relief'\n3. Verify the capital-specific fields are visible",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)
    case.step(2, "Click 'Capital loss relief'")
    case.click(lr.capital_loss_radio, "'Capital loss relief' radio")

    case.step(3, "Verify capital-specific fields are visible")
    brought_forward_ok = case.verify_visible(
        page.get_by_text("Capital losses brought forward", exact=True), "'Capital losses brought forward' label")
    excess_ok = case.verify_visible(
        page.get_by_text("Excess capital losses to carry forward", exact=True),
        "'Excess capital losses to carry forward' label")
    ordinary_gone = page.get_by_text("Losses brought forward", exact=True).count() == 0
    ok = brought_forward_ok and excess_ok and ordinary_gone
    case.check("Capital-mode fields are visible and Ordinary-mode fields are gone", ok,
               expected="capital fields visible, ordinary fields absent",
               actual=f"brought_forward={brought_forward_ok}, excess={excess_ok}, ordinary_gone={ordinary_gone}")

    actual = ("Switching to 'Capital loss relief' correctly swapped in the capital-specific fields." if ok else
              "Switching to 'Capital loss relief' did not show the expected fields.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_09_capital_mode_has_nine_fields_with_correct_editable_pattern(page, result):
    case = Case(
        page, "LossRelief_09", FEATURE, "Capital loss relief mode shows exactly 9 fields in the expected editable pattern",
        description="Capital loss relief mode must show exactly 9 input fields, with fields 1,2,4,6,8 "
                     "editable and fields 3,5,7,9 disabled/computed (confirmed live) - including the real "
                     "app quirk where fields 4 and 6 share the exact same visible label text ('Capital "
                     "losses in current year'), so this is checked positionally.",
        precondition="User is logged in, Australia/2023-2024 selected, Capital loss relief mode.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024, switch to Capital mode\n"
              "2. Verify exactly 9 fields exist with the expected disabled/editable pattern",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)
    case.click(lr.capital_loss_radio, "'Capital loss relief' radio")
    page.wait_for_timeout(800)

    case.step(2, "Verify exactly 9 fields with the expected disabled/editable pattern")
    count = page.locator("input[class*='reg-input']").count()
    expected_disabled = {3: True, 5: True, 7: True, 9: True, 1: False, 2: False, 4: False, 6: False, 8: False}
    actual_disabled = {n: lr.capital_field(n).is_disabled() for n in range(1, 10)}
    ok = count == 9 and actual_disabled == expected_disabled
    case.check("Capital mode shows exactly 9 fields with the expected editable/disabled pattern", ok,
               expected=f"count=9, {expected_disabled}", actual=f"count={count}, {actual_disabled}")

    actual = ("Capital loss relief mode correctly shows exactly 9 fields in the expected editable pattern." if ok
              else f"Capital mode's field count/pattern did not match (count={count}, pattern={actual_disabled}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_10_capital_mode_computed_field_updates_live(page, result):
    case = Case(
        page, "LossRelief_10", FEATURE, "Entering 'Capital losses brought forward' live-updates the computed offset field",
        description="Entering 100 into 'Capital losses brought forward' (field 1, with no restriction "
                     "entered) must live-update 'Capital loss brought forward available for offset against "
                     "current year gains' (field 3, disabled) to 100.",
        precondition="User is logged in, Australia/2023-2024 selected, Capital loss relief mode.",
        test_data="Capital losses brought forward=100",
        steps="1. Log in, open Loss Relief Calculator, select Australia/2023-2024, switch to Capital mode\n"
              "2. Enter 100 into 'Capital losses brought forward'\n"
              "3. Verify the computed offset-available field becomes 100",
    )
    lr = _login_and_open(case, page)
    _select_au_2023(case, page, lr)
    case.click(lr.capital_loss_radio, "'Capital loss relief' radio")
    page.wait_for_timeout(800)

    case.step(2, "Enter 100 into 'Capital losses brought forward' (field 1)")
    field1 = lr.capital_field(1)
    case.click(field1, "'Capital losses brought forward' field")
    field1.press_sequentially("100", delay=15)
    page.wait_for_timeout(800)

    case.step(3, "Verify the computed offset-available field (field 3) becomes 100")
    value = lr.capital_field(3).input_value().replace(",", "")
    ok = value == "100"
    case.check("'Capital loss brought forward available' computes to 100", ok, expected="100", actual=value)

    actual = (f"The computed field correctly updated to {value} after entering 100." if ok else
              f"The computed field did not update as expected (got {value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_lossrelief_11_mode_toggle_switches_to_entity_fields(page, result):
    case = Case(
        page, "LossRelief_11", FEATURE, "Switching to 'By Entity' swaps in Corporate Group/Source Company fields",
        description="Clicking 'By Entity' must swap 'Source Jurisdiction' for 'Corporate Group' and "
                     "'Source Company' fields.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator\n2. Click 'By Entity'\n"
              "3. Verify 'Corporate Group' and 'Source Company' fields are visible",
    )
    lr = _login_and_open(case, page)
    case.step(2, "Click 'By Entity'")
    case.click(lr.mode_by_entity, "'By Entity' radio")

    case.step(3, "Verify entity-mode fields are visible")
    group_ok = case.verify_visible(lr.corporate_group_combobox(), "'Corporate Group' select")
    company_ok = case.verify_visible(lr.source_company_combobox(), "'Source Company' select")
    ok = group_ok and company_ok
    case.check("'By Entity' mode shows Corporate Group/Source Company fields", ok,
               expected="both visible", actual=f"group={group_ok}, company={company_ok}")

    actual = ("Switching to 'By Entity' correctly swapped in the entity-based fields." if ok else
              "Switching to 'By Entity' did not show the expected fields.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_12_corporate_group_lists_real_entity_charts(page, result):
    case = Case(
        page, "LossRelief_12", FEATURE, "'Corporate Group' lists this account's real entity charts",
        description="In 'By Entity' mode, opening 'Corporate Group' must list this account's real, "
                     "previously-created entity charts.",
        precondition="User is logged in, 'By Entity' mode selected.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator, switch to 'By Entity'\n"
              "2. Open 'Corporate Group'\n3. Verify at least one real entity chart is listed",
    )
    lr = _login_and_open(case, page)
    case.click(lr.mode_by_entity, "'By Entity' radio")
    case.step(2, "Open 'Corporate Group'")
    case.click(lr.corporate_group_combobox(), "'Corporate Group' select")
    options = lr.open_listbox_options(lr.corporate_group_combobox())

    case.step(3, "Verify at least one real entity chart is listed")
    count = options.count()
    names = [options.nth(i).inner_text() for i in range(count)]
    ok = count >= 1
    case.check("'Corporate Group' lists at least one real entity chart", ok,
               expected=">= 1 option", actual=f"count={count}, names={names}")

    actual = (f"'Corporate Group' correctly lists {count} real entity chart(s): {names}." if ok else
              "'Corporate Group' did not list any entity charts.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_lossrelief_13_start_over_shows_confirm_dialog(page, result):
    case = Case(
        page, "LossRelief_13", FEATURE, "'Start over' shows a confirmation dialog",
        description="Clicking 'Start over' must show a confirmation dialog reading 'Are you sure to reset "
                     "all your selections?' with Cancel/Yes actions - the same dialog as WHT Router, not "
                     "an immediate reset.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Loss Relief Calculator\n2. Click 'Start over'\n3. Verify the confirmation dialog",
    )
    lr = _login_and_open(case, page)
    case.step(2, "Click 'Start over'")
    case.click(lr.start_over_button, "'Start over' button")

    case.step(3, "Verify the confirmation dialog")
    ok = case.verify_visible(lr.start_over_confirm_heading, "Start Over confirmation text")
    case.check("'Start over' shows the expected confirmation dialog", ok,
               expected="'Are you sure to reset all your selections?' visible", actual=f"visible={ok}")
    if ok:
        lr.start_over_confirm_cancel.click()

    actual = ("'Start over' correctly showed a confirmation dialog before resetting." if ok else
              "'Start over' did not show the expected confirmation dialog.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_14_start_over_yes_resets_source_jurisdiction(page, result):
    case = Case(
        page, "LossRelief_14", FEATURE, "Confirming 'Start over' (Yes) resets the Source Jurisdiction selection",
        description="Confirming 'Start over' with 'Yes' must reset the Source Jurisdiction select back to "
                     "its 'Select' placeholder state.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open Loss Relief Calculator, select Australia\n"
              "2. Click 'Start over' then 'Yes'\n3. Verify Source Jurisdiction resets to 'Select'",
    )
    lr = _login_and_open(case, page)
    case.click(lr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    lr.open_and_pick(lr.source_jurisdiction_combobox(), "Australia")

    case.step(2, "Click 'Start over' then 'Yes'")
    lr.start_over_and_confirm()

    case.step(3, "Verify Source Jurisdiction resets to 'Select'")
    text = lr.source_jurisdiction_combobox().inner_text()
    ok = text.strip() == "Select"
    case.check("Source Jurisdiction resets to the 'Select' placeholder", ok, expected="Select", actual=text)

    actual = ("Confirming 'Start over' correctly reset the selection to its placeholder state." if ok else
              f"Confirming 'Start over' did not reset the selection as expected (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_lossrelief_15_start_over_cancel_keeps_current_state(page, result):
    case = Case(
        page, "LossRelief_15", FEATURE, "'Start over' Cancel keeps the current selection",
        description="Clicking Cancel on the Start Over confirmation must leave the already-selected Source "
                     "Jurisdiction untouched.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open Loss Relief Calculator, select Australia\n"
              "2. Click 'Start over' then Cancel\n3. Verify Source Jurisdiction is still Australia",
    )
    lr = _login_and_open(case, page)
    case.click(lr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    lr.open_and_pick(lr.source_jurisdiction_combobox(), "Australia")

    case.step(2, "Click 'Start over' then Cancel")
    case.click(lr.start_over_button, "'Start over' button")
    lr.start_over_confirm_heading.wait_for(state="visible", timeout=5000)
    case.click(lr.start_over_confirm_cancel, "'Cancel' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify Source Jurisdiction is still Australia")
    text = lr.source_jurisdiction_combobox().inner_text()
    ok = "Australia" in text
    case.check("Source Jurisdiction selection survives Cancel", ok, expected="Australia", actual=text)

    actual = ("Cancelling 'Start over' correctly preserved the current selection." if ok else
              f"Cancelling 'Start over' did not preserve the selection (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual
