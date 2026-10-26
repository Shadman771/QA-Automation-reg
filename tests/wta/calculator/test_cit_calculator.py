"""Calculators > CIT Calculator (/wta/CitCalculator).

New module, built via live DOM discovery (scratchpad scripts, not part
of the suite) - no QA-sheet rows exist for this page. Reuses the same
live `CorporateRate` API and the same documented null-`HeadlineRate`
data gap as Corporate Rate Finder, so this module's calculation-
validation anchor reuses that module's already-confirmed-good
Bangladesh/2024 combination (see
pages/wta/calculator_cit_page.py docstring)."""
import pytest
import requests

from pages.wta.calculator_menu import CalculatorMenu
from pages.wta.calculator_cit_page import CitCalculatorPage, CORPORATE_RATE_API
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - CIT Calculator"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > CIT Calculator", kind="navigate")
    cit = CitCalculatorPage(page)
    CalculatorMenu(page).open_item("CIT Calculator", ready_locator=cit.instructions_heading)
    return cit


def _select_bd_2024(case, page, cit):
    case.click(cit.domestic_jurisdiction_combobox(), "'Domestic Jurisdiction' select")
    cit.open_and_pick(cit.domestic_jurisdiction_combobox(), "Bangladesh")
    case.click(cit.tax_year_combobox(), "'Tax Year' select")
    cit.open_and_pick(cit.tax_year_combobox(), "01 July 2024")
    page.wait_for_timeout(500)


@pytest.mark.smoke
def test_cit_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "CIT_01", FEATURE, "CIT Calculator opens from the Calculators dropdown",
        description="Clicking 'CIT Calculator' in the Calculators dropdown must land on /wta/CitCalculator "
                     "with the 'Initial Information' panel and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > CIT Calculator\n2. Verify the URL and instructions banner",
    )
    cit = _login_and_open(case, page)
    case.step(2, "Verify URL and instructions banner")
    url_ok = "/wta/CitCalculator" in page.url
    banner_ok = case.verify_visible(cit.instructions_heading, "'How to complete this calculation' heading")
    ok = url_ok and banner_ok
    case.check("CIT Calculator page loads with its instructions banner", ok,
               expected="url contains /wta/CitCalculator, banner visible",
               actual=f"url={page.url}, banner={banner_ok}")

    actual = ("CIT Calculator opened correctly with its instructions banner visible." if ok else
              "CIT Calculator did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_cit_02_initial_state_defaults_and_disabled_actions(page, result):
    case = Case(
        page, "CIT_02", FEATURE, "Initial state: 'By Jurisdiction' checked, action buttons present but disabled",
        description="On first load, 'By Jurisdiction' must be the checked mode, and Generate Memo/Get "
                     "Forms/Add to Project must be present but disabled (confirmed live: unlike WHT "
                     "Router, these buttons exist from the start here, just disabled).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open CIT Calculator\n"
              "2. Verify 'By Jurisdiction' is checked and all 3 action buttons are disabled",
    )
    cit = _login_and_open(case, page)
    case.step(2, "Verify default mode and disabled actions")
    mode_ok = page.locator("input[type='radio']").first.is_checked()
    gm_disabled = not cit.generate_memo_button.is_enabled()
    gf_disabled = not cit.get_forms_button.is_enabled()
    atp_disabled = not cit.add_to_project_button.is_enabled()
    ok = mode_ok and gm_disabled and gf_disabled and atp_disabled
    case.check("'By Jurisdiction' checked and all action buttons disabled initially", ok,
               expected="mode=checked, all 3 buttons disabled",
               actual=f"mode_checked={mode_ok}, gm_disabled={gm_disabled}, gf_disabled={gf_disabled}, "
                      f"atp_disabled={atp_disabled}")

    actual = ("CIT Calculator correctly starts on 'By Jurisdiction' with all action buttons disabled." if ok else
              "The initial state did not match expectations.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_03_domestic_jurisdiction_lists_real_countries(page, result):
    case = Case(
        page, "CIT_03", FEATURE, "'Domestic Jurisdiction' lists real countries",
        description="Opening 'Domestic Jurisdiction' must list real country names including Bangladesh.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open CIT Calculator\n2. Open 'Domestic Jurisdiction'\n"
              "3. Verify real countries are listed",
    )
    cit = _login_and_open(case, page)
    case.step(2, "Open 'Domestic Jurisdiction'")
    case.click(cit.domestic_jurisdiction_combobox(), "'Domestic Jurisdiction' select")
    options = cit.open_listbox_options(cit.domestic_jurisdiction_combobox())

    case.step(3, "Verify real countries are listed")
    count = options.count()
    all_text = [options.nth(i).inner_text() for i in range(count)]
    ok = count > 50 and "Bangladesh" in all_text
    case.check("'Domestic Jurisdiction' lists real countries including Bangladesh", ok,
               expected="> 50 options including Bangladesh", actual=f"count={count}")

    actual = (f"'Domestic Jurisdiction' correctly lists {count} real countries." if ok else
              f"'Domestic Jurisdiction' did not list the expected real countries (count={count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_04_tax_year_lists_real_date_ranges(page, result):
    case = Case(
        page, "CIT_04", FEATURE, "'Tax Year' lists real date-range options",
        description="After selecting a Domestic Jurisdiction, 'Tax Year' must list real date-range options "
                     "(e.g. '01 July 2024 - 30 June 2025'), not plain year numbers.",
        precondition="User is logged in, Bangladesh selected as Domestic Jurisdiction.",
        test_data="Domestic Jurisdiction: Bangladesh",
        steps="1. Log in, open CIT Calculator, select Bangladesh\n2. Open 'Tax Year'\n"
              "3. Verify real date-range options are listed",
    )
    cit = _login_and_open(case, page)
    case.click(cit.domestic_jurisdiction_combobox(), "'Domestic Jurisdiction' select")
    cit.open_and_pick(cit.domestic_jurisdiction_combobox(), "Bangladesh")
    case.step(2, "Open 'Tax Year'")
    case.click(cit.tax_year_combobox(), "'Tax Year' select")
    options = cit.open_listbox_options(cit.tax_year_combobox())

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
def test_cit_05_no_rate_data_jurisdiction_shows_blocking_message(page, result):
    case = Case(
        page, "CIT_05", FEATURE, "A jurisdiction/year with no rate data shows a blocking message",
        description="Selecting Australia / 01 July 2023-30 June 2024 (a confirmed live null-HeadlineRate "
                     "combination, same documented data gap as Corporate Rate Finder's CRF_09) must show a "
                     "modal reading 'No data found for this jurisdiction. You may try for another "
                     "jurisdiction.' (Cancel-only) - this is real, documented application behavior, not an "
                     "automation bug.",
        precondition="User is logged in.",
        test_data="Domestic Jurisdiction: Australia, Tax Year: 01 July 2023 - 30 June 2024",
        steps="1. Log in, open CIT Calculator, select Australia / 2023-2024\n"
              "2. Verify the 'No data found' blocking modal appears",
    )
    cit = _login_and_open(case, page)
    case.click(cit.domestic_jurisdiction_combobox(), "'Domestic Jurisdiction' select")
    cit.open_and_pick(cit.domestic_jurisdiction_combobox(), "Australia")
    case.step(2, "Select Tax Year 01 July 2023 - 30 June 2024")
    case.click(cit.tax_year_combobox(), "'Tax Year' select")
    cit.open_and_pick(cit.tax_year_combobox(), "01 July 2023")

    case.step(3, "Verify the 'No data found' blocking modal")
    cit.message_modal.first.wait_for(state="visible", timeout=5000)
    modal_text = cit.message_modal.inner_text()
    message_ok = "No data found for this jurisdiction." in modal_text
    cancel_only = cit.message_modal_cancel.count() == 1
    ok = message_ok and cancel_only
    case.check("The no-rate-data modal shows the expected message with only Cancel", ok,
               expected="message present, 1 Cancel button", actual=f"modal_text={modal_text!r}")
    cit.message_modal_cancel.click()

    actual = ("Selecting a jurisdiction/year with no rate data correctly triggered the real blocking "
              "message." if ok else
              f"The no-rate-data validation did not behave as expected (modal_text={modal_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_cit_06_bd_2024_taxable_income_computes_total_cit(page, result):
    case = Case(
        page, "CIT_06", FEATURE, "Entering Taxable Income for BD/2024 computes the correct Total CIT",
        description="With Bangladesh / 01 July 2024-30 June 2025 selected and Taxable Income=100,000 "
                     "entered (then blurred), Total CIT must compute to 55,000 = 100,000 x 55% (the known, "
                     "live-confirmed Bangladesh/2024 HeadlineRate).",
        precondition="User is logged in.",
        test_data="Domestic Jurisdiction: Bangladesh, Tax Year: 2024-2025, Taxable Income: 100000",
        steps="1. Log in, open CIT Calculator, select Bangladesh/2024-2025\n"
              "2. Enter Taxable Income=100000 and blur the field\n"
              "3. Verify Total CIT computes to 55,000",
    )
    cit = _login_and_open(case, page)
    _select_bd_2024(case, page, cit)

    case.step(2, "Enter Taxable Income=100000 and blur the field")
    case.click(cit.taxable_income_input(), "'Taxable Income' field")
    cit.enter_taxable_income("100000")

    case.step(3, "Verify Total CIT computes to 55,000")
    total_cit = cit.field("Total CIT").input_value().replace(",", "")
    ok = total_cit == "55000"
    case.check("Total CIT computes to the expected value", ok, expected="55000", actual=total_cit)

    actual = (f"Total CIT correctly computed to {total_cit} (100,000 x 55%)." if ok else
              f"Total CIT did not compute as expected (got {total_cit!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_cit_07_results_match_independent_api_calculation(page, result):
    case = Case(
        page, "CIT_07", FEATURE, "Total tax due and Nominal ETR match an independent API-sourced calculation",
        description="With Bangladesh/2024-2025/Taxable Income=100,000, Total tax due and Nominal ETR must "
                     "match an independent calculation using the live CorporateRate API's own HeadlineRate "
                     "for BD/2024 - not compared against the UI itself.",
        precondition="User is logged in.",
        test_data="Domestic Jurisdiction: Bangladesh, Tax Year: 2024-2025, Taxable Income: 100000",
        steps="1. Log in, open CIT Calculator, select Bangladesh/2024-2025, enter Taxable Income=100000\n"
              "2. Independently fetch the live CorporateRate API for BD/2024\n"
              "3. Verify Total tax due and Nominal ETR match the independently-fetched rate",
    )
    cit = _login_and_open(case, page)
    _select_bd_2024(case, page, cit)
    case.click(cit.taxable_income_input(), "'Taxable Income' field")
    cit.enter_taxable_income("100000")

    case.step(2, "Independently fetch the live CorporateRate API for BD/2024")
    resp = requests.get(CORPORATE_RATE_API, params={"country": "BD", "year": 2024}, timeout=15)
    api_ok = resp.status_code == 200
    body = resp.json() if api_ok else {}
    headline_rate = body.get("HeadlineRate", {}).get("RangeRate", [{}])[0].get("Value") if api_ok else None
    expected_total_due = round(100000 * (headline_rate or 0) / 100, 2)

    case.step(3, "Verify Total tax due and Nominal ETR match the independently-fetched rate")
    total_due = cit.total_tax_due_input().input_value().replace(",", "")
    etr = cit.nominal_etr_input().input_value().replace(",", "")
    ok = (api_ok and headline_rate is not None and float(total_due) == expected_total_due
          and float(etr) == headline_rate)
    case.check("Total tax due and Nominal ETR match the independently-fetched API rate", ok,
               expected=f"total_due={expected_total_due}, etr={headline_rate}",
               actual=f"total_due={total_due}, etr={etr}")

    actual = (f"Total tax due ({total_due}) and Nominal ETR ({etr}) correctly matched the independently-"
              f"fetched live API rate ({headline_rate}%)." if ok else
              f"Results did not match the independent API calculation (ui total_due={total_due}/etr={etr}, "
              f"expected total_due={expected_total_due}/etr={headline_rate}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_08_action_buttons_enabled_after_calculation(page, result):
    case = Case(
        page, "CIT_08", FEATURE, "Generate Memo/Get Forms/Add to Project become enabled once the calculation completes",
        description="After a successful BD/2024/100,000 calculation, the 3 action buttons must become "
                     "enabled (they're present but disabled before the calculation completes).",
        precondition="User is logged in, BD/2024-2025/100,000 calculated.",
        test_data="-",
        steps="1. Log in, open CIT Calculator, complete BD/2024-2025/100,000\n"
              "2. Verify the 3 action buttons are enabled",
    )
    cit = _login_and_open(case, page)
    _select_bd_2024(case, page, cit)
    case.click(cit.taxable_income_input(), "'Taxable Income' field")
    cit.enter_taxable_income("100000")

    case.step(2, "Verify the 3 action buttons are enabled")
    gm_ok = cit.generate_memo_button.is_enabled()
    gf_ok = cit.get_forms_button.is_enabled()
    atp_ok = cit.add_to_project_button.is_enabled()
    ok = gm_ok and gf_ok and atp_ok
    case.check("All 3 action buttons are enabled after calculation", ok,
               expected="all 3 enabled", actual=f"gm={gm_ok}, gf={gf_ok}, atp={atp_ok}")

    actual = ("All 3 action buttons correctly became enabled after calculation." if ok else
              f"Action buttons did not enable as expected (gm={gm_ok}, gf={gf_ok}, atp={atp_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_09_no_surtax_message_for_jurisdiction_without_surtax(page, result):
    case = Case(
        page, "CIT_09", FEATURE, "The Surtax/Surcharge section shows 'No surtax applicable' when none exists",
        description="For Bangladesh/2024-2025, the Surtax/Surcharge Rate section must show '* No surtax "
                     "applicable' - a real, documented application behavior, not a missing feature.",
        precondition="User is logged in, Bangladesh/2024-2025 selected.",
        test_data="-",
        steps="1. Log in, open CIT Calculator, select Bangladesh/2024-2025\n"
              "2. Verify the 'No surtax applicable' message is visible",
    )
    cit = _login_and_open(case, page)
    _select_bd_2024(case, page, cit)

    case.step(2, "Verify the 'No surtax applicable' message is visible")
    ok = case.verify_visible(cit.no_surtax_message, "'No surtax applicable' message")
    case.check("'No surtax applicable' is shown for Bangladesh/2024-2025", ok,
               expected="visible", actual=f"visible={ok}")

    actual = ("The 'No surtax applicable' message is correctly shown for this jurisdiction/year." if ok else
              "The expected 'No surtax applicable' message was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_cit_10_mode_toggle_switches_to_entity_fields(page, result):
    case = Case(
        page, "CIT_10", FEATURE, "Switching to 'By Entity' swaps in Corporate Group/Entity fields",
        description="Clicking 'By Entity' must swap 'Domestic Jurisdiction' for 'Corporate Group' and "
                     "'Entity in Residence states' fields (confirmed live: this module's own naming, not "
                     "'Source Company' like other Calculator sub-pages).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open CIT Calculator\n2. Click 'By Entity'\n"
              "3. Verify 'Corporate Group' and 'Entity in Residence states' fields are visible",
    )
    cit = _login_and_open(case, page)
    case.step(2, "Click 'By Entity'")
    case.click(cit.mode_by_entity, "'By Entity' radio")

    case.step(3, "Verify entity-mode fields are visible")
    group_ok = case.verify_visible(cit.corporate_group_combobox(), "'Corporate Group' select")
    company_ok = case.verify_visible(cit.entity_combobox(), "'Entity in Residence states' select")
    ok = group_ok and company_ok
    case.check("'By Entity' mode shows Corporate Group/Entity fields", ok,
               expected="both visible", actual=f"group={group_ok}, entity={company_ok}")

    actual = ("Switching to 'By Entity' correctly swapped in the entity-based fields." if ok else
              "Switching to 'By Entity' did not show the expected fields.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_11_corporate_group_lists_real_entity_charts(page, result):
    case = Case(
        page, "CIT_11", FEATURE, "'Corporate Group' lists this account's real entity charts",
        description="In 'By Entity' mode, opening 'Corporate Group' must list this account's real, "
                     "previously-created entity charts.",
        precondition="User is logged in, 'By Entity' mode selected.",
        test_data="-",
        steps="1. Log in, open CIT Calculator, switch to 'By Entity'\n"
              "2. Open 'Corporate Group'\n3. Verify at least one real entity chart is listed",
    )
    cit = _login_and_open(case, page)
    case.click(cit.mode_by_entity, "'By Entity' radio")
    case.step(2, "Open 'Corporate Group'")
    case.click(cit.corporate_group_combobox(), "'Corporate Group' select")
    options = cit.open_listbox_options(cit.corporate_group_combobox())

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
def test_cit_12_start_over_shows_confirm_dialog(page, result):
    case = Case(
        page, "CIT_12", FEATURE, "'Start over' shows a confirmation dialog",
        description="Clicking 'Start over' must show a confirmation dialog reading 'Are you sure to reset "
                     "all your selections?' with Cancel/Yes actions.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open CIT Calculator\n2. Click 'Start over'\n3. Verify the confirmation dialog",
    )
    cit = _login_and_open(case, page)
    case.step(2, "Click 'Start over'")
    case.click(cit.start_over_button, "'Start over' button")

    case.step(3, "Verify the confirmation dialog")
    ok = case.verify_visible(cit.start_over_confirm_heading, "Start Over confirmation text")
    case.check("'Start over' shows the expected confirmation dialog", ok,
               expected="'Are you sure to reset all your selections?' visible", actual=f"visible={ok}")
    if ok:
        cit.start_over_confirm_cancel.click()

    actual = ("'Start over' correctly showed a confirmation dialog before resetting." if ok else
              "'Start over' did not show the expected confirmation dialog.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_cit_13_start_over_yes_resets_domestic_jurisdiction(page, result):
    case = Case(
        page, "CIT_13", FEATURE, "Confirming 'Start over' (Yes) resets the Domestic Jurisdiction selection",
        description="Confirming 'Start over' with 'Yes' must reset the Domestic Jurisdiction select back to "
                     "its 'Select' placeholder state.",
        precondition="User is logged in, Bangladesh selected as Domestic Jurisdiction.",
        test_data="Domestic Jurisdiction: Bangladesh",
        steps="1. Log in, open CIT Calculator, select Bangladesh\n2. Click 'Start over' then 'Yes'\n"
              "3. Verify Domestic Jurisdiction resets to 'Select'",
    )
    cit = _login_and_open(case, page)
    case.click(cit.domestic_jurisdiction_combobox(), "'Domestic Jurisdiction' select")
    cit.open_and_pick(cit.domestic_jurisdiction_combobox(), "Bangladesh")

    case.step(2, "Click 'Start over' then 'Yes'")
    cit.start_over_and_confirm()

    case.step(3, "Verify Domestic Jurisdiction resets to 'Select'")
    text = cit.domestic_jurisdiction_combobox().inner_text()
    ok = text.strip() == "Select"
    case.check("Domestic Jurisdiction resets to the 'Select' placeholder", ok, expected="Select", actual=text)

    actual = ("Confirming 'Start over' correctly reset the selection to its placeholder state." if ok else
              f"Confirming 'Start over' did not reset the selection as expected (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual
