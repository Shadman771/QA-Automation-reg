"""Calculators > Interest And Penalties (/wta/InterestAndPenalties).

New module, built via live DOM discovery (scratchpad scripts, not part
of the suite) - no QA-sheet rows exist for this page. Uses its own
confirmed-good anchor (Bangladesh + tax year 2023, a DIFFERENT year than
Corporate Rate Finder's/CIT Calculator's Bangladesh/2024 anchor - see
pages/wta/calculator_interest_penalty_page.py docstring) and documents a
real, live-confirmed application crash (typing a comma into either date
field) without triggering it in every run - see the page object's
`pick_date()` for the safe calendar-click alternative actually used
throughout."""
import pytest

from pages.wta.calculator_menu import CalculatorMenu
from pages.wta.calculator_interest_penalty_page import InterestPenaltyPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - Interest And Penalties"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > Interest And Penalties", kind="navigate")
    iap = InterestPenaltyPage(page)
    CalculatorMenu(page).open_item("Interest And Penalties", ready_locator=iap.instructions_heading)
    return iap


def _select_bd_2023_late_payment(case, page, iap):
    case.click(iap.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    iap.open_and_pick(iap.source_jurisdiction_combobox(), "Bangladesh")
    case.click(iap.tax_year_combobox(), "'Tax Year' select")
    iap.open_and_pick(iap.tax_year_combobox(), "01 July 2023")
    page.wait_for_timeout(500)
    case.click(iap.offence_type_combobox(), "'Type of offences' select")
    iap.open_and_pick(iap.offence_type_combobox(), "Late payment")


@pytest.mark.smoke
def test_iap_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "IAP_01", FEATURE, "Interest And Penalties opens from the Calculators dropdown",
        description="Clicking 'Interest And Penalties' in the Calculators dropdown must land on "
                     "/wta/InterestAndPenalties with the 'Initial Data' panel and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > Interest And Penalties\n2. Verify the URL and instructions banner",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Verify URL and instructions banner")
    url_ok = "/wta/InterestAndPenalties" in page.url
    banner_ok = case.verify_visible(iap.instructions_heading, "'How to complete this calculation' heading")
    ok = url_ok and banner_ok
    case.check("Interest And Penalties page loads with its instructions banner", ok,
               expected="url contains /wta/InterestAndPenalties, banner visible",
               actual=f"url={page.url}, banner={banner_ok}")

    actual = ("Interest And Penalties opened correctly with its instructions banner visible." if ok else
              "Interest And Penalties did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_iap_02_initial_state_defaults_and_disabled_actions(page, result):
    case = Case(
        page, "IAP_02", FEATURE, "Initial state: 'By Jurisdiction' checked, action buttons present but disabled",
        description="On first load, 'By Jurisdiction' must be the checked mode, and Generate Memo/Get "
                     "Forms/Add to Project must be present but disabled.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Interest And Penalties\n"
              "2. Verify 'By Jurisdiction' is checked and all 3 action buttons are disabled",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Verify default mode and disabled actions")
    mode_ok = page.locator("input[type='radio']").first.is_checked()
    gm_disabled = not iap.generate_memo_button.is_enabled()
    gf_disabled = not iap.get_forms_button.is_enabled()
    atp_disabled = not iap.add_to_project_button.is_enabled()
    ok = mode_ok and gm_disabled and gf_disabled and atp_disabled
    case.check("'By Jurisdiction' checked and all action buttons disabled initially", ok,
               expected="mode=checked, all 3 buttons disabled",
               actual=f"mode_checked={mode_ok}, gm_disabled={gm_disabled}, gf_disabled={gf_disabled}, "
                      f"atp_disabled={atp_disabled}")

    actual = ("Interest And Penalties correctly starts on 'By Jurisdiction' with all action buttons "
              "disabled." if ok else "The initial state did not match expectations.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_03_source_jurisdiction_lists_real_countries(page, result):
    case = Case(
        page, "IAP_03", FEATURE, "'Source Jurisdiction' lists real countries",
        description="Opening 'Source Jurisdiction' must list real country names including Bangladesh.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties\n2. Open 'Source Jurisdiction'\n"
              "3. Verify real countries are listed",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Open 'Source Jurisdiction'")
    case.click(iap.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    options = iap.open_listbox_options(iap.source_jurisdiction_combobox())

    case.step(3, "Verify real countries are listed")
    count = options.count()
    all_text = [options.nth(i).inner_text() for i in range(count)]
    ok = count > 50 and "Bangladesh" in all_text
    case.check("'Source Jurisdiction' lists real countries including Bangladesh", ok,
               expected="> 50 options including Bangladesh", actual=f"count={count}")

    actual = (f"'Source Jurisdiction' correctly lists {count} real countries." if ok else
              f"'Source Jurisdiction' did not list the expected real countries (count={count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_04_no_offence_data_disables_type_of_offences(page, result):
    case = Case(
        page, "IAP_04", FEATURE, "A jurisdiction/year with no offence data disables 'Type of offences'",
        description="Selecting Australia / 01 July 2023-30 June 2024 (a confirmed live null-AllOffense "
                     "combination) must leave 'Type of offences' disabled, showing 'No offenses available' "
                     "- this is real, documented application behavior, not an automation bug.",
        precondition="User is logged in.",
        test_data="Source Jurisdiction: Australia, Tax Year: 01 July 2023 - 30 June 2024",
        steps="1. Log in, open Interest And Penalties, select Australia / 2023-2024\n"
              "2. Verify 'Type of offences' is disabled showing 'No offenses available'",
    )
    iap = _login_and_open(case, page)
    case.click(iap.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    iap.open_and_pick(iap.source_jurisdiction_combobox(), "Australia")
    case.click(iap.tax_year_combobox(), "'Tax Year' select")
    iap.open_and_pick(iap.tax_year_combobox(), "01 July 2023")
    page.wait_for_timeout(1000)

    case.step(2, "Verify 'Type of offences' is disabled")
    disabled = iap.offence_type_combobox().get_attribute("aria-disabled") == "true"
    text = iap.offence_type_combobox().inner_text()
    ok = disabled and "No offenses available" in text
    case.check("'Type of offences' is disabled with the expected placeholder", ok,
               expected="disabled, 'No offenses available'", actual=f"disabled={disabled}, text={text!r}")

    actual = ("'Type of offences' correctly showed the real no-data state for this jurisdiction/year." if ok
              else f"'Type of offences' did not show the expected no-data state (disabled={disabled}, "
                   f"text={text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_05_bd_2023_lists_late_payment_offence(page, result):
    case = Case(
        page, "IAP_05", FEATURE, "Bangladesh/2023-2024 lists the real 'Late payment' offence",
        description="Selecting Bangladesh / 01 July 2023-30 June 2024 must enable 'Type of offences' and "
                     "list the real, live-confirmed seeded offence 'Late payment'.",
        precondition="User is logged in.",
        test_data="Source Jurisdiction: Bangladesh, Tax Year: 01 July 2023 - 30 June 2024",
        steps="1. Log in, open Interest And Penalties, select Bangladesh / 2023-2024\n"
              "2. Verify 'Type of offences' is enabled and lists 'Late payment'",
    )
    iap = _login_and_open(case, page)
    case.click(iap.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    iap.open_and_pick(iap.source_jurisdiction_combobox(), "Bangladesh")
    case.click(iap.tax_year_combobox(), "'Tax Year' select")
    iap.open_and_pick(iap.tax_year_combobox(), "01 July 2023")
    page.wait_for_timeout(1000)

    case.step(2, "Verify 'Type of offences' is enabled and lists 'Late payment'")
    disabled = iap.offence_type_combobox().get_attribute("aria-disabled") == "true"
    case.click(iap.offence_type_combobox(), "'Type of offences' select")
    options = iap.open_listbox_options(iap.offence_type_combobox())
    names = [options.nth(i).inner_text() for i in range(options.count())]
    ok = not disabled and "Late payment" in names
    case.check("'Type of offences' lists the real 'Late payment' offence", ok,
               expected="enabled, includes 'Late payment'", actual=f"disabled={disabled}, options={names}")

    actual = ("'Type of offences' correctly listed the real seeded offence for Bangladesh/2023-2024." if ok
              else f"'Type of offences' did not list the expected offence (disabled={disabled}, options={names}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_iap_06_calculation_matches_independent_arithmetic(page, result):
    case = Case(
        page, "IAP_06", FEATURE, "Total days overdue/penalty/interest match an independent calculation",
        description="With Bangladesh/2023-2024, 'Late payment' offence, Tax due=1,000, Final tax due date="
                     "01 Oct 2026, Overdue tax paid=11 Oct 2026: Total days overdue must be 10 (simple "
                     "calendar day difference), and Total penalty amount/Total interest and penalty must "
                     "both equal 1,000,000 = PenaltyPerDay(100,000) x 10 days - independently recomputed "
                     "in Python from the known PenaltyPerDay, not compared to the UI itself.",
        precondition="User is logged in.",
        test_data="Bangladesh/2023-2024, Late payment, Tax due=1000, "
                  "01 Oct 2026 -> 11 Oct 2026",
        steps="1. Log in, open Interest And Penalties, select Bangladesh/2023-2024/Late payment\n"
              "2. Enter Tax due=1000, Final tax due date=01 Oct 2026, Overdue tax paid=11 Oct 2026\n"
              "3. Independently compute the expected days/penalty\n"
              "4. Verify all 3 computed fields match",
    )
    iap = _login_and_open(case, page)
    _select_bd_2023_late_payment(case, page, iap)

    case.step(2, "Enter Tax due=1000, Final tax due date=01 Oct 2026, Overdue tax paid=11 Oct 2026")
    tax_due = iap.tax_due_input()
    case.click(tax_due, "'Tax due (amount)' field")
    tax_due.press_sequentially("1000", delay=15)
    tax_due.press("Tab")
    page.wait_for_timeout(500)
    case.action("Picking Final tax due date = 01 Oct 2026 via the calendar", kind="click")
    iap.pick_date(iap.final_tax_due_date_input(), 1, "Oct", 2026)
    case.action("Picking Overdue tax paid = 11 Oct 2026 via the calendar", kind="click")
    iap.pick_date(iap.overdue_tax_paid_input(), 11, "Oct", 2026)
    page.wait_for_timeout(1000)

    case.step(3, "Independently compute the expected days/penalty")
    from datetime import date
    days_overdue = (date(2026, 10, 11) - date(2026, 10, 1)).days
    penalty_per_day = 100000
    expected_penalty = penalty_per_day * days_overdue

    case.step(4, "Verify all 3 computed fields match the independent calculation")
    actual_days = iap.field("Total days overdue").input_value().replace(",", "")
    actual_penalty = iap.field("Total penalty amount").input_value().replace(",", "")
    actual_total = iap.field("Total interest and penalty").input_value().replace(",", "")
    ok = (actual_days == str(days_overdue) and actual_penalty == str(expected_penalty)
          and actual_total == str(expected_penalty))
    case.check("Total days overdue/penalty/interest match the independent calculation", ok,
               expected=f"days={days_overdue}, penalty={expected_penalty}, total={expected_penalty}",
               actual=f"days={actual_days}, penalty={actual_penalty}, total={actual_total}")

    actual = (f"All 3 computed fields correctly matched the independent calculation "
              f"(days={actual_days}, penalty={actual_penalty})." if ok else
              f"Computed fields did not match (expected days={days_overdue}/penalty={expected_penalty}, "
              f"got days={actual_days}/penalty={actual_penalty}/total={actual_total}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_07_outstanding_tax_due_equals_tax_due_without_advance_payment(page, result):
    case = Case(
        page, "IAP_07", FEATURE, "Outstanding tax due equals Tax due when no advance payment is entered",
        description="With Tax due=1,000 and 'Tax paid in advance' left blank, Outstanding tax due must "
                     "equal 1,000.",
        precondition="User is logged in, Bangladesh/2023-2024/Late payment selected.",
        test_data="Tax due=1000",
        steps="1. Log in, open Interest And Penalties, select Bangladesh/2023-2024/Late payment\n"
              "2. Enter Tax due=1000\n3. Verify Outstanding tax due equals 1,000",
    )
    iap = _login_and_open(case, page)
    _select_bd_2023_late_payment(case, page, iap)

    case.step(2, "Enter Tax due=1000")
    tax_due = iap.tax_due_input()
    case.click(tax_due, "'Tax due (amount)' field")
    tax_due.press_sequentially("1000", delay=15)
    tax_due.press("Tab")
    page.wait_for_timeout(800)

    case.step(3, "Verify Outstanding tax due equals 1,000")
    outstanding = iap.field("Outstanding tax due").input_value().replace(",", "")
    ok = outstanding == "1000"
    case.check("Outstanding tax due equals Tax due with no advance payment", ok, expected="1000", actual=outstanding)

    actual = (f"Outstanding tax due correctly equals {outstanding} with no advance payment entered." if ok else
              f"Outstanding tax due did not match the expected value (got {outstanding!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_08_payment_type_radios_present(page, result):
    case = Case(
        page, "IAP_08", FEATURE, "'Payment type' offers 'One time payment' and 'Installment' options",
        description="The 'Interest due' section's 'Payment type' field must offer both 'One time payment' "
                     "(default) and 'Installment' radio options.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties\n2. Verify both payment type options are visible",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Verify both payment type options are visible")
    one_time_ok = case.verify_visible(iap.payment_type_one_time, "'One time payment' option")
    installment_ok = case.verify_visible(iap.payment_type_installment, "'Installment' option")
    ok = one_time_ok and installment_ok
    case.check("Both 'Payment type' options are visible", ok,
               expected="both visible", actual=f"one_time={one_time_ok}, installment={installment_ok}")

    actual = ("Both 'Payment type' options are correctly visible." if ok else
              "One or both 'Payment type' options were not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_09_action_buttons_enabled_after_calculation(page, result):
    case = Case(
        page, "IAP_09", FEATURE, "Generate Memo/Get Forms/Add to Project become enabled once the calculation completes",
        description="After a successful Bangladesh/2023-2024/Late payment/1,000/01-11 Oct 2026 calculation, "
                     "the 3 action buttons must become enabled.",
        precondition="User is logged in, full calculation completed.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties, complete a full calculation\n"
              "2. Verify the 3 action buttons are enabled",
    )
    iap = _login_and_open(case, page)
    _select_bd_2023_late_payment(case, page, iap)
    tax_due = iap.tax_due_input()
    case.click(tax_due, "'Tax due (amount)' field")
    tax_due.press_sequentially("1000", delay=15)
    tax_due.press("Tab")
    page.wait_for_timeout(500)
    iap.pick_date(iap.final_tax_due_date_input(), 1, "Oct", 2026)
    iap.pick_date(iap.overdue_tax_paid_input(), 11, "Oct", 2026)
    page.wait_for_timeout(1000)

    case.step(2, "Verify the 3 action buttons are enabled")
    gm_ok = iap.generate_memo_button.is_enabled()
    gf_ok = iap.get_forms_button.is_enabled()
    atp_ok = iap.add_to_project_button.is_enabled()
    ok = gm_ok and gf_ok and atp_ok
    case.check("All 3 action buttons are enabled after calculation", ok,
               expected="all 3 enabled", actual=f"gm={gm_ok}, gf={gf_ok}, atp={atp_ok}")

    actual = ("All 3 action buttons correctly became enabled after calculation." if ok else
              f"Action buttons did not enable as expected (gm={gm_ok}, gf={gf_ok}, atp={atp_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_iap_10_mode_toggle_switches_to_entity_fields(page, result):
    case = Case(
        page, "IAP_10", FEATURE, "Switching to 'By Entity' swaps in Corporate Group fields",
        description="Clicking 'By Entity' must swap 'Source Jurisdiction' for 'Corporate Group'.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties\n2. Click 'By Entity'\n"
              "3. Verify 'Corporate Group' field is visible",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Click 'By Entity'")
    case.click(iap.mode_by_entity, "'By Entity' radio")

    case.step(3, "Verify 'Corporate Group' field is visible")
    ok = case.verify_visible(iap.corporate_group_combobox(), "'Corporate Group' select")
    case.check("'By Entity' mode shows the 'Corporate Group' field", ok, expected="visible", actual=f"visible={ok}")

    actual = ("Switching to 'By Entity' correctly swapped in the entity-based field." if ok else
              "Switching to 'By Entity' did not show the expected field.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_11_corporate_group_lists_real_entity_charts(page, result):
    case = Case(
        page, "IAP_11", FEATURE, "'Corporate Group' lists this account's real entity charts",
        description="In 'By Entity' mode, opening 'Corporate Group' must list this account's real, "
                     "previously-created entity charts.",
        precondition="User is logged in, 'By Entity' mode selected.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties, switch to 'By Entity'\n"
              "2. Open 'Corporate Group'\n3. Verify at least one real entity chart is listed",
    )
    iap = _login_and_open(case, page)
    case.click(iap.mode_by_entity, "'By Entity' radio")
    case.step(2, "Open 'Corporate Group'")
    case.click(iap.corporate_group_combobox(), "'Corporate Group' select")
    options = iap.open_listbox_options(iap.corporate_group_combobox())

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
def test_iap_12_start_over_shows_confirm_dialog(page, result):
    case = Case(
        page, "IAP_12", FEATURE, "'Start over' shows a confirmation dialog",
        description="Clicking 'Start over' must show a confirmation dialog reading 'Are you sure to reset "
                     "all your selections?' with Cancel/Yes actions.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Interest And Penalties\n2. Click 'Start over'\n3. Verify the confirmation dialog",
    )
    iap = _login_and_open(case, page)
    case.step(2, "Click 'Start over'")
    case.click(iap.start_over_button, "'Start over' button")

    case.step(3, "Verify the confirmation dialog")
    ok = case.verify_visible(iap.start_over_confirm_heading, "Start Over confirmation text")
    case.check("'Start over' shows the expected confirmation dialog", ok,
               expected="'Are you sure to reset all your selections?' visible", actual=f"visible={ok}")
    if ok:
        iap.start_over_confirm_cancel.click()

    actual = ("'Start over' correctly showed a confirmation dialog before resetting." if ok else
              "'Start over' did not show the expected confirmation dialog.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_iap_13_start_over_yes_resets_source_jurisdiction(page, result):
    case = Case(
        page, "IAP_13", FEATURE, "Confirming 'Start over' (Yes) resets the Source Jurisdiction selection",
        description="Confirming 'Start over' with 'Yes' must reset the Source Jurisdiction select back to "
                     "its 'Select' placeholder state.",
        precondition="User is logged in, Bangladesh selected as Source Jurisdiction.",
        test_data="Source Jurisdiction: Bangladesh",
        steps="1. Log in, open Interest And Penalties, select Bangladesh\n"
              "2. Click 'Start over' then 'Yes'\n3. Verify Source Jurisdiction resets to 'Select'",
    )
    iap = _login_and_open(case, page)
    case.click(iap.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    iap.open_and_pick(iap.source_jurisdiction_combobox(), "Bangladesh")

    case.step(2, "Click 'Start over' then 'Yes'")
    iap.start_over_and_confirm()

    case.step(3, "Verify Source Jurisdiction resets to 'Select'")
    text = iap.source_jurisdiction_combobox().inner_text()
    ok = text.strip() == "Select"
    case.check("Source Jurisdiction resets to the 'Select' placeholder", ok, expected="Select", actual=text)

    actual = ("Confirming 'Start over' correctly reset the selection to its placeholder state." if ok else
              f"Confirming 'Start over' did not reset the selection as expected (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual
