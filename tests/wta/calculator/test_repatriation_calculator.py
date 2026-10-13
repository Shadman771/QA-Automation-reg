"""Calculators > Repatriation Calculator (/wta/RepCalculator).

Source test cases: Calculator_Repatriation Calculator_20..62 in the
provided QA sheet. Reviewed against the live application and substantially
expanded per the "no fixed test-count cap" directive: real field-level
masking validation (via actual keystrokes, not `.fill()`), a real
API-sourced calculation-validation anchor (AU->SG Portfolio Dividend
Treaty Rate, see pages/calculator_repatriation_page.py docstring) with an
independent Python recomputation of the Withholding tax amount/Total Tax
Due rather than comparing the UI to itself, two real negative-validation
modals (same-jurisdiction selection; no-treaty entity pairing) the sheet
did not anticipate, dependency-chain testing (action-button enabled
states, mode-toggle resets, income-stream switching), and both "By
Jurisdiction" and "By Entity" modes end-to-end."""
import os

import pytest

from pages.calculator_menu import CalculatorMenu
from pages.calculator_repatriation_page import RepatriationCalculatorPage, REPATRIATION_TREATY_API
from pages.tools_menu import ToolsMenu
from pages.tools_projects_page import ProjectsPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - Repatriation Calculator"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > Repatriation Calculator", kind="navigate")
    CalculatorMenu(page).open_item("Repatriation Calculator")
    return RepatriationCalculatorPage(page)


def _complete_au_sg_dividends_7pct(case, page, rc, amount="100000"):
    """Shared setup used by several tests: AU -> SG, Dividends, 7% holding,
    the module's calculation-validation anchor combination."""
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.fill("")
    amt.press_sequentially(amount, delay=10)
    page.wait_for_timeout(500)
    case.click(rc.income_stream_combobox(), "'Select Income Stream' select")
    rc.open_and_pick(rc.income_stream_combobox(), "Dividends")
    case.click(rc.holding_percent_combobox(), "'Select holding %' select")
    hp_options = rc.open_listbox_options(rc.holding_percent_combobox())
    hp_options.filter(has_text="7%").first.click()
    page.wait_for_timeout(1500)


@pytest.mark.smoke
def test_repcalc_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "RepCalc_01", FEATURE, "Repatriation Calculator opens from the Calculators dropdown",
        description="Clicking 'Repatriation Calculator' in the Calculators dropdown must land on "
                     "/wta/RepCalculator with the heading and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > Repatriation Calculator\n"
              "2. Verify the URL, page heading and instructions banner",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Verify URL, heading and instructions banner")
    url_ok = "/wta/RepCalculator" in page.url
    # Scoped to <p> - an unscoped get_by_text also matches the (hidden)
    # Calculators dropdown's own menu item text, per the rsuite
    # "every dropdown item stays mounted" gotcha (see CLAUDE.md).
    heading_ok = case.verify_visible(page.locator("p").filter(has_text="Repatriation Calculator").first, "page heading")
    banner_ok = case.verify_visible(rc.instructions_heading, "instructions banner")
    ok = url_ok and heading_ok and banner_ok
    case.check("Repatriation Calculator page loads with heading and instructions", ok,
               expected="url contains /wta/RepCalculator, heading+banner visible",
               actual=f"url={page.url}, heading={heading_ok}, banner={banner_ok}")

    actual = ("Repatriation Calculator opened correctly with its heading and instructions visible." if ok else
              "Repatriation Calculator did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_02_initial_state_defaults_and_disabled_actions(page, result):
    case = Case(
        page, "RepCalc_02", FEATURE, "Initial state: 'By Jurisdiction' selected, action buttons disabled",
        description="On first load, 'By Jurisdiction' must be the checked mode and Generate Memo/Get Forms/"
                     "Add to Project must all be disabled until enough of the form is completed.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Repatriation Calculator\n"
              "2. Verify 'By Jurisdiction' is checked and all 3 action buttons are disabled",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Verify default mode and disabled actions")
    mode_radio = page.locator("input[type='radio'][name='interactiveOption']").first
    mode_ok = mode_radio.is_checked()
    gm_disabled = rc.generate_memo_button.is_disabled()
    gf_disabled = rc.get_forms_button.is_disabled()
    atp_disabled = rc.add_to_project_button.is_disabled()
    ok = mode_ok and gm_disabled and gf_disabled and atp_disabled
    case.check("'By Jurisdiction' checked and all action buttons disabled initially", ok,
               expected="mode=checked, all 3 buttons disabled",
               actual=f"mode_checked={mode_ok}, gm={gm_disabled}, gf={gf_disabled}, atp={atp_disabled}")

    actual = ("The calculator correctly starts on 'By Jurisdiction' with all action buttons disabled." if ok else
              "The initial state did not match expectations.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_03_source_jurisdiction_lists_real_countries_and_is_searchable(page, result):
    case = Case(
        page, "RepCalc_03", FEATURE, "Source Jurisdiction dropdown lists real countries and supports search",
        description="Opening the Source Jurisdiction select must show a real, searchable country list "
                     "(120 countries confirmed live); typing 'austra' must filter it to just Australia.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Search term: austra",
        steps="1. Log in and open Repatriation Calculator\n2. Open the Source Jurisdiction select\n"
              "3. Type 'austra' into its search box\n4. Verify the list filters to just Australia",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Open the Source Jurisdiction select")
    cb = rc.row_combobox("Source Jurisdiction")
    case.click(cb, "'Source Jurisdiction' select")
    page.wait_for_timeout(500)
    full_count = page.locator(f"[id='{cb.get_attribute('aria-controls')}'] [role='option']").count()

    case.step(3, "Search for 'austra'")
    search_box = page.locator(".rs-picker-search-bar-input, input[placeholder='Search']")
    case.fill(search_box.first, "austra", "jurisdiction search box")
    page.wait_for_timeout(500)

    case.step(4, "Verify the filtered list")
    filtered = page.locator(f"[id='{cb.get_attribute('aria-controls')}'] [role='option']")
    filtered_texts = filtered.all_inner_texts()
    ok = full_count >= 100 and filtered_texts == ["Australia"]
    case.check("Country list starts large and search filters to exactly 'Australia'", ok,
               expected="full_count>=100, filtered=['Australia']",
               actual=f"full_count={full_count}, filtered={filtered_texts}")

    actual = (f"Source Jurisdiction listed {full_count} real countries and correctly filtered to just "
              f"Australia when searched." if ok else
              f"The jurisdiction list/search did not behave as expected (full_count={full_count}, "
              f"filtered={filtered_texts}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_04_selecting_source_jurisdiction_sets_currency_badge(page, result):
    case = Case(
        page, "RepCalc_04", FEATURE, "Selecting a Source Jurisdiction sets the Repatriation Amount currency badge",
        description="Before any selection the amount field shows a '--' placeholder badge; selecting "
                     "Australia as Source Jurisdiction must update it to 'AUD' - a real dependent-field effect.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Country: Australia",
        steps="1. Log in and open Repatriation Calculator\n2. Verify the currency badge starts as '--'\n"
              "3. Select Australia as Source Jurisdiction\n4. Verify the currency badge becomes 'AUD'",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Verify the initial currency badge")
    badge = page.locator("tr", has_text="Repatriation Amount").locator("span.rs-input-group-addon").first
    before = badge.inner_text()

    case.step(3, "Select Australia as Source Jurisdiction")
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")

    case.step(4, "Verify the currency badge updated to AUD")
    after = badge.inner_text()
    ok = before == "--" and after == "AUD"
    case.check("Currency badge updates from '--' to 'AUD' after selecting Australia", ok,
               expected="before='--', after='AUD'", actual=f"before={before!r}, after={after!r}",
               locator=badge)

    actual = (f"The currency badge correctly updated from '{before}' to '{after}' as a dependent effect of "
              f"the Source Jurisdiction selection." if ok else
              f"The currency badge did not update as expected (before={before!r}, after={after!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_05_both_jurisdictions_render_relief_panel(page, result):
    case = Case(
        page, "RepCalc_05", FEATURE, "Selecting both jurisdictions renders the 'Relief from double taxation' panel",
        description="With Australia (source) and Singapore (residence) selected, a 'Relief from double "
                     "taxation: Singapore' panel must render.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Source: Australia, Residence: Singapore",
        steps="1. Log in and open Repatriation Calculator\n2. Select Australia then Singapore\n"
              "3. Verify the Relief panel heading",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.step(2, "Select Singapore as Residence Jurisdiction")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")

    case.step(3, "Verify the Relief panel heading")
    ok = case.verify_visible(page.get_by_text("Relief from double taxation: Singapore", exact=True), "Relief panel heading")
    case.check("'Relief from double taxation: Singapore' panel is visible", ok, expected="visible", actual=ok)

    actual = ("Selecting both jurisdictions correctly rendered the Relief panel." if ok else
              "The Relief panel did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_06_relief_methods_match_real_treaty_data(page, result):
    case = Case(
        page, "RepCalc_06", FEATURE, "Relief methods listed match the real AU-SG treaty data",
        description="The Relief panel's 'Relief methods' list for Australia/Singapore must show both "
                     "'Exemption' and 'Credit' - confirmed live, real treaty content, not placeholder text.",
        precondition="User is logged in, Australia+Singapore selected on Repatriation Calculator.",
        test_data="Source: Australia, Residence: Singapore",
        steps="1. Log in, open Repatriation Calculator, select Australia and Singapore\n"
              "2. Verify the Relief methods list shows 'Exemption' and 'Credit'",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")

    case.step(2, "Verify the Relief methods list")
    exemption_ok = case.verify_visible(page.get_by_text("Exemption", exact=True), "'Exemption' relief method")
    credit_ok = case.verify_visible(page.get_by_text("Credit", exact=True), "'Credit' relief method")
    ok = exemption_ok and credit_ok
    case.check("Relief methods list shows 'Exemption' and 'Credit'", ok, expected="both visible",
               actual=f"exemption={exemption_ok}, credit={credit_ok}")

    actual = ("The Relief methods list correctly showed both 'Exemption' and 'Credit' for AU/SG." if ok else
              "The Relief methods list did not show the expected real treaty content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_07_get_forms_enabled_once_source_jurisdiction_selected(page, result):
    case = Case(
        page, "RepCalc_07", FEATURE, "'Get Forms' becomes enabled once a Source Jurisdiction is selected",
        description="'Get Forms' must stay disabled with nothing selected, and become enabled as soon as "
                     "a Source Jurisdiction alone is picked - confirmed live this does NOT require a "
                     "Residence Jurisdiction too (unlike Generate Memo/Add to Project, which need the full "
                     "calculation chain); it stays enabled once Residence is added as well.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Source: Australia, Residence: Singapore",
        steps="1. Log in, open Repatriation Calculator\n2. Verify 'Get Forms' starts disabled\n"
              "3. Select Australia as Source Jurisdiction\n4. Verify 'Get Forms' becomes enabled\n"
              "5. Select Singapore as Residence Jurisdiction and verify it stays enabled",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Verify 'Get Forms' starts disabled")
    starts_disabled = rc.get_forms_button.is_disabled()
    case.check("'Get Forms' is disabled with nothing selected", starts_disabled,
               expected=True, actual=starts_disabled, locator=rc.get_forms_button)

    case.step(3, "Select Australia as Source Jurisdiction")
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")

    case.step(4, "Verify 'Get Forms' becomes enabled")
    now_enabled = not rc.get_forms_button.is_disabled()
    case.check("'Get Forms' becomes enabled once Source Jurisdiction alone is selected", now_enabled,
               expected=True, actual=now_enabled, locator=rc.get_forms_button)

    case.step(5, "Select Singapore as Residence Jurisdiction")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    still_enabled = not rc.get_forms_button.is_disabled()
    case.check("'Get Forms' remains enabled once Residence Jurisdiction is also selected", still_enabled,
               expected=True, actual=still_enabled, locator=rc.get_forms_button)

    ok = starts_disabled and now_enabled and still_enabled
    actual = ("'Get Forms' correctly enabled as soon as Source Jurisdiction alone was selected, and stayed "
              "enabled once Residence Jurisdiction was added too." if ok else
              f"'Get Forms' enabled-state did not follow the expected dependency chain "
              f"(starts_disabled={starts_disabled}, now_enabled={now_enabled}, still_enabled={still_enabled}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_08_same_jurisdiction_both_sides_shows_blocking_message(page, result):
    case = Case(
        page, "RepCalc_08", FEATURE, "Selecting the same country for both jurisdictions shows a blocking message",
        description="Selecting 'Australia' as both Source and Residence Jurisdiction must trigger a modal "
                     "reading 'Source and Residence Jurisdiction must be different.' with only a Cancel "
                     "action - confirmed live real validation, not a crash or silent no-op.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia, Residence: Australia",
        steps="1. Log in, open Repatriation Calculator, select Australia as Source\n"
              "2. Select Australia as Residence too\n3. Verify the blocking message modal",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")

    case.step(2, "Select Australia as Residence Jurisdiction too")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Australia")

    case.step(3, "Verify the blocking message modal")
    wait_ok = rc.message_modal.first.wait_for(state="visible", timeout=5000) or True
    modal_text = rc.message_modal.inner_text()
    message_ok = "Source and Residence Jurisdiction must be different." in modal_text
    cancel_only = rc.message_modal_cancel.count() == 1
    ok = message_ok and cancel_only
    case.check("The same-jurisdiction validation modal shows the expected message with only Cancel", ok,
               expected="message present, 1 Cancel button", actual=f"modal_text={modal_text!r}")
    rc.message_modal_cancel.click()

    actual = ("Selecting the same country for both jurisdictions correctly triggered the real blocking "
              "validation message." if ok else
              f"The same-jurisdiction validation did not behave as expected (modal_text={modal_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_09_amount_field_strips_negative_sign(page, result):
    case = Case(
        page, "RepCalc_09", FEATURE, "Repatriation Amount rejects a negative sign (real keystrokes)",
        description="Typing '-5000' (as real keystrokes, not .fill()) into Repatriation Amount must strip "
                     "the minus sign - the field never holds a negative value.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Typed: -5000",
        steps="1. Log in and open Repatriation Calculator\n2. Type '-5000' into Repatriation Amount\n"
              "3. Verify the minus sign was stripped",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Type '-5000' into Repatriation Amount")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.press_sequentially("-5000", delay=20)
    page.wait_for_timeout(400)

    case.step(3, "Verify the value has no negative sign")
    value = amt.input_value()
    ok = "-" not in value and value.strip() != ""
    case.check("Repatriation Amount never holds a negative value", ok,
               expected="no '-' in value", actual=value, locator=amt)

    actual = (f"Typing '-5000' correctly produced a non-negative value ('{value}')." if ok else
              f"The amount field did not strip the negative sign as expected (value={value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_10_amount_field_strips_non_digit_characters(page, result):
    case = Case(
        page, "RepCalc_10", FEATURE, "Repatriation Amount strips non-digit characters",
        description="Typing 'abc123' (real keystrokes) must leave only the digits ('123').",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Typed: abc123",
        steps="1. Log in and open Repatriation Calculator\n2. Type 'abc123' into Repatriation Amount\n"
              "3. Verify only '123' remains",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Type 'abc123' into Repatriation Amount")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.press_sequentially("abc123", delay=20)
    page.wait_for_timeout(400)

    case.step(3, "Verify only digits remain")
    value = amt.input_value()
    ok = value == "123"
    case.check("Only the digits '123' remain after typing 'abc123'", ok, expected="123", actual=value,
               locator=amt)

    actual = (f"Typing 'abc123' correctly left only the digits ('{value}')." if ok else
              f"The amount field did not strip non-digit characters as expected (value={value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_11_amount_field_treats_zero_as_empty(page, result):
    case = Case(
        page, "RepCalc_11", FEATURE, "Repatriation Amount treats '0' as no value",
        description="Typing '0' alone must leave the field empty, confirming zero is rejected as a valid "
                     "repatriation amount rather than being accepted as a literal zero.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Typed: 0",
        steps="1. Log in and open Repatriation Calculator\n2. Type '0' into Repatriation Amount\n"
              "3. Verify the field is empty",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Type '0' into Repatriation Amount")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.press_sequentially("0", delay=20)
    page.wait_for_timeout(400)

    case.step(3, "Verify the field is empty")
    value = amt.input_value()
    ok = value == ""
    case.check("Typing '0' leaves Repatriation Amount empty", ok, expected="''", actual=repr(value),
               locator=amt)

    actual = ("Typing '0' correctly left the amount field empty, confirming zero is treated as no value."
              if ok else f"The amount field did not clear on '0' as expected (value={value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_12_amount_field_accepts_decimals(page, result):
    case = Case(
        page, "RepCalc_12", FEATURE, "Repatriation Amount accepts decimal values",
        description="Typing '12.345' must be accepted as-is (decimal repatriation amounts are valid).",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Typed: 12.345",
        steps="1. Log in and open Repatriation Calculator\n2. Type '12.345' into Repatriation Amount\n"
              "3. Verify the decimal value is retained",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Type '12.345' into Repatriation Amount")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.press_sequentially("12.345", delay=20)
    page.wait_for_timeout(400)

    case.step(3, "Verify the decimal value")
    value = amt.input_value()
    ok = value == "12.345"
    case.check("Decimal value '12.345' is retained", ok, expected="12.345", actual=value, locator=amt)

    actual = (f"Typing '12.345' was correctly retained as a decimal value." if ok else
              f"The amount field did not accept the decimal value as expected (value={value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_13_amount_field_formats_large_values_with_separators(page, result):
    case = Case(
        page, "RepCalc_13", FEATURE, "Repatriation Amount formats large values with thousands separators",
        description="Typing '1000000000' (one billion) must be accepted and displayed as "
                     "'1,000,000,000' - confirmed live there is no artificial maximum blocking this.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Typed: 1000000000",
        steps="1. Log in and open Repatriation Calculator\n2. Type '1000000000' into Repatriation Amount\n"
              "3. Verify it is formatted with thousands separators",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Type '1000000000' into Repatriation Amount")
    amt = rc.amount_input()
    case.click(amt, "'Repatriation Amount' field")
    amt.press_sequentially("1000000000", delay=15)
    page.wait_for_timeout(400)

    case.step(3, "Verify thousands-separator formatting")
    value = amt.input_value()
    ok = value == "1,000,000,000"
    case.check("Large value is formatted with thousands separators", ok,
               expected="1,000,000,000", actual=value, locator=amt)

    actual = (f"A one-billion repatriation amount was correctly formatted as '{value}'." if ok else
              f"The large amount was not formatted as expected (value={value!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_14_income_stream_lists_real_categories(page, result):
    case = Case(
        page, "RepCalc_14", FEATURE, "Income Stream dropdown lists the 5 real categories",
        description="The Select Income Stream dropdown must list exactly: Dividends, Interest, Royalties, "
                     "Lease Payments, Technical Service Fees.",
        precondition="User is logged in, both jurisdictions and an amount set on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select Australia, Singapore and an amount\n"
              "2. Open the Select Income Stream dropdown\n3. Verify all 5 categories are listed",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    rc.amount_input().press_sequentially("10000", delay=10)
    page.wait_for_timeout(500)

    case.step(2, "Open the Select Income Stream dropdown")
    options = rc.open_listbox_options(rc.income_stream_combobox())
    texts = options.all_inner_texts()

    case.step(3, "Verify all 5 categories are listed")
    expected = ["Dividends", "Interest", "Royalties", "Lease Payments", "Technical Service Fees"]
    ok = texts == expected
    case.check("Income Stream dropdown lists exactly the 5 expected categories", ok,
               expected=expected, actual=texts)

    actual = (f"The Income Stream dropdown correctly listed all 5 categories: {texts}." if ok else
              f"The Income Stream dropdown did not list the expected categories (got {texts}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_15_amount_and_stream_render_results_table(page, result):
    case = Case(
        page, "RepCalc_15", FEATURE, "Entering amount and income stream renders the results table",
        description="With Australia/Singapore/100,000/Dividends set, a results table with a "
                     "'What is the % of holding in the company?' selector must render.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Source: Australia, Residence: Singapore, Amount: 100000, Stream: Dividends",
        steps="1. Log in, open Repatriation Calculator\n2. Select Australia, Singapore, enter 100000, select Dividends\n"
              "3. Verify the results table with the holding % selector renders",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    rc.amount_input().press_sequentially("100000", delay=10)
    page.wait_for_timeout(500)
    case.click(rc.income_stream_combobox(), "'Select Income Stream' select")
    rc.open_and_pick(rc.income_stream_combobox(), "Dividends")

    case.step(2, "Verify the results table and holding % selector")
    ok = case.verify_visible(page.get_by_text("What is the % of holding in the company?", exact=True),
                              "holding % question label")
    case.check("The results table with the holding % question is visible", ok, expected="visible", actual=ok)

    actual = ("The results table correctly rendered with the holding % selector." if ok else
              "The results table did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_16_holding_percent_limited_to_1_through_7(page, result):
    case = Case(
        page, "RepCalc_16", FEATURE, "Holding % selector is limited to exactly 1% through 7%",
        description="The 'What is the % of holding in the company?' dropdown must list exactly "
                     "['1%'..'7%'] - a real, confirmed-live data boundary, not a UI truncation.",
        precondition="User is logged in, Australia/Singapore/100000/Dividends set.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, complete the setup through Income Stream\n"
              "2. Open the holding % dropdown\n3. Verify it lists exactly 1% through 7%",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    rc.amount_input().press_sequentially("100000", delay=10)
    page.wait_for_timeout(500)
    case.click(rc.income_stream_combobox(), "'Select Income Stream' select")
    rc.open_and_pick(rc.income_stream_combobox(), "Dividends")

    case.step(2, "Open the holding % dropdown")
    options = rc.open_listbox_options(rc.holding_percent_combobox())
    texts = options.all_inner_texts()

    case.step(3, "Verify the exact option list")
    expected = [f"{i}%" for i in range(1, 8)]
    ok = texts == expected
    case.check("Holding % dropdown lists exactly 1% through 7%", ok, expected=expected, actual=texts)

    actual = (f"The holding % dropdown correctly listed exactly {texts}." if ok else
              f"The holding % dropdown did not match the expected 1%-7% range (got {texts}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_17_treaty_rate_matches_live_api(page, result):
    case = Case(
        page, "RepCalc_17", FEATURE, "The displayed Treaty Rate matches the live Treaty API",
        description="With Australia/Singapore/Dividends/7% selected, the UI must show 'Treaty Rate - 15.00%' "
                     "and 'Your holding type is Portfolio.' - independently verified against "
                     "GET /api/Treaty?hostCountryCode=AU&partnerCountryCode=SG "
                     "(WtrDomesticRates[Portfolio Dividend].Rate), not compared against itself.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="Source: Australia, Residence: Singapore, Stream: Dividends, Holding: 7%",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Independently fetch the Treaty API for AU/SG\n"
              "3. Verify the UI's Treaty Rate matches the API's Portfolio Dividend rate",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)

    case.step(2, "Independently fetch the Treaty API for AU/SG")
    resp = page.request.get(f"{REPATRIATION_TREATY_API}?hostCountryCode=AU&partnerCountryCode=SG")
    rates = resp.json().get("WtrDomesticRates", [])
    portfolio = next((r for r in rates if r.get("DisplayTitle") == "Portfolio Dividend"), None)
    expected_rate = portfolio["Rate"] if portfolio else None

    case.step(3, "Verify the UI matches the independently-fetched API rate")
    holding_type_ok = case.verify_visible(page.get_by_text("Your holding type is", exact=False), "holding type label")
    rate_text = page.get_by_text("Treaty Rate", exact=False).first.inner_text()
    expected_pct = f"{float(expected_rate.strip('%')):.2f}%" if expected_rate else None
    rate_ok = expected_pct is not None and expected_pct in rate_text
    ok = holding_type_ok and rate_ok
    case.check("UI Treaty Rate matches the independently-fetched API value", ok,
               expected=f"Treaty Rate - {expected_pct}", actual=rate_text)

    actual = (f"The UI's Treaty Rate ('{rate_text}') correctly matched the live API's independent value "
              f"({expected_pct})." if ok else
              f"The UI's Treaty Rate did not match the independently-fetched API value (ui={rate_text!r}, "
              f"api={expected_pct!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_18_wht_amount_matches_independent_calculation(page, result):
    case = Case(
        page, "RepCalc_18", FEATURE, "Withholding tax amount matches an independent Python calculation",
        description="With amount=100,000, Treaty Rate=15.00% and a user-entered Exchange Rate of 1.2, the "
                     "computed Withholding tax amount AND Total Tax Due must both equal "
                     "100,000 x 0.15 x 1.2 = 18,000 - calculated independently in Python from the known "
                     "inputs, not read back from the application and compared to itself.",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data="Amount: 100000, Treaty Rate: 15%, Exchange Rate: 1.2",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7% with amount 100000\n"
              "2. Enter Exchange Rate = 1.2\n"
              "3. Independently compute 100000 x 0.15 x 1.2\n"
              "4. Verify both the Withholding tax amount and Total Tax Due equal that value",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc, amount="100000")

    case.step(2, "Enter Exchange Rate = 1.2")
    exch = rc.exchange_rate_input()
    case.click(exch, "'Exchange Rate' field")
    exch.fill("")
    exch.press_sequentially("1.2", delay=15)
    page.wait_for_timeout(1000)

    case.step(3, "Independently compute the expected amount")
    expected_amount = round(100000 * 0.15 * 1.2)

    case.step(4, "Verify computed cells match the independent calculation")
    wht_value = rc.computed_wht_amount_input().input_value().replace(",", "")
    total_value = rc.total_tax_due_input().input_value().replace(",", "")
    ok = wht_value == str(expected_amount) and total_value == str(expected_amount)
    case.check("Withholding tax amount and Total Tax Due match the independent Python calculation", ok,
               expected=f"{expected_amount:,}", actual=f"wht={wht_value}, total={total_value}")

    actual = (f"The computed amounts ({wht_value}, {total_value}) correctly matched the independent "
              f"calculation of {expected_amount:,} (100,000 x 15% x 1.2)." if ok else
              f"The computed amounts did not match the independent calculation (expected "
              f"{expected_amount:,}, got wht={wht_value}, total={total_value}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_19_changing_exchange_rate_recalculates_live(page, result):
    case = Case(
        page, "RepCalc_19", FEATURE, "Changing the Exchange Rate live-recalculates the computed amounts",
        description="After computing with Exchange Rate=1.2 (18,000), changing it to 2.0 must update the "
                     "Withholding tax amount/Total Tax Due to 100,000 x 0.15 x 2.0 = 30,000 without "
                     "requiring any other field to be re-entered.",
        precondition="User is logged in, AU->SG/Dividends/7%/Exchange Rate=1.2 completed.",
        test_data="Exchange Rate changed from 1.2 to 2.0",
        steps="1. Log in, open Repatriation Calculator, complete the setup with Exchange Rate 1.2\n"
              "2. Change the Exchange Rate to 2.0\n"
              "3. Verify the computed amounts update to 30,000",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc, amount="100000")
    exch = rc.exchange_rate_input()
    exch.fill("")
    exch.press_sequentially("1.2", delay=15)
    page.wait_for_timeout(800)

    case.step(2, "Change Exchange Rate to 2.0")
    exch.fill("")
    exch.press_sequentially("2.0", delay=15)
    page.wait_for_timeout(1000)

    case.step(3, "Verify the recalculated amounts")
    expected_amount = round(100000 * 0.15 * 2.0)
    wht_value = rc.computed_wht_amount_input().input_value().replace(",", "")
    total_value = rc.total_tax_due_input().input_value().replace(",", "")
    ok = wht_value == str(expected_amount) and total_value == str(expected_amount)
    case.check("Changing the Exchange Rate live-recalculates the computed amounts", ok,
               expected=f"{expected_amount:,}", actual=f"wht={wht_value}, total={total_value}")

    actual = (f"Changing the Exchange Rate correctly recalculated the amounts to {expected_amount:,}." if ok
              else f"The recalculation did not match expectations (expected {expected_amount:,}, got "
                   f"wht={wht_value}, total={total_value}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_20_rates_panel_shows_real_treaty_article_text(page, result):
    case = Case(
        page, "RepCalc_20", FEATURE, "The Rates panel shows the real treaty article text",
        description="The 'Rates: Australia' panel must show 'Article 8 (1)' and the real treaty wording "
                     "mentioning 'shall not exceed 15 per centum of the gross amount of the dividends.'",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Verify the Rates panel shows Article 8(1) and the treaty wording",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)

    case.step(2, "Verify the Rates panel content")
    article_ok = case.verify_visible(page.get_by_text("Article 8", exact=False).first, "'Article 8 (1)' label")
    wording_ok = case.verify_visible(
        page.get_by_text("shall not exceed 15 per centum of the gross amount of the dividends", exact=False),
        "treaty article wording")
    ok = article_ok and wording_ok
    case.check("Rates panel shows the real Article 8(1) treaty text", ok, expected="both visible",
               actual=f"article={article_ok}, wording={wording_ok}")

    actual = ("The Rates panel correctly showed the real Article 8(1) treaty wording." if ok else
              "The Rates panel did not show the expected real treaty text.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_21_switching_income_stream_resets_holding_selection(page, result):
    case = Case(
        page, "RepCalc_21", FEATURE, "Switching Income Stream resets the holding %/rate selection",
        description="After selecting Dividends and a 7% holding (Treaty Rate 15.00%), switching Income "
                     "Stream to 'Interest' must clear the previous holding %/rate selection rather than "
                     "carry stale Dividend-specific data forward.",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data="Stream changed from Dividends to Interest",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Change Income Stream to 'Interest'\n"
              "3. Verify the Dividend-specific holding type text is no longer shown",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)
    dividends_type_visible_before = page.get_by_text("Your holding type is", exact=False).count() > 0

    case.step(2, "Change Income Stream to 'Interest'")
    case.click(rc.income_stream_combobox(), "'Select Income Stream' select")
    rc.open_and_pick(rc.income_stream_combobox(), "Interest")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the stale holding-type text is gone")
    stale_text_gone = page.get_by_text("Your holding type is", exact=False).count() == 0
    ok = dividends_type_visible_before and stale_text_gone
    case.check("Switching Income Stream clears the previous stream's holding selection", ok,
               expected="stale text gone after switch",
               actual=f"before={dividends_type_visible_before}, after_gone={stale_text_gone}")

    actual = ("Switching Income Stream correctly reset the previous selection's holding-type text." if ok else
              "Switching Income Stream did not reset the previous selection as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_22_generate_memo_and_add_to_project_enabled_only_after_full_chain(page, result):
    case = Case(
        page, "RepCalc_22", FEATURE, "'Generate Memo'/'Add to Project' enable only after the full chain completes",
        description="Both buttons must stay disabled through jurisdictions+amount+stream, and only become "
                     "enabled once a holding % is also selected (the full calculation chain).",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, complete jurisdictions+amount+stream only\n"
              "2. Verify Generate Memo/Add to Project are still disabled\n"
              "3. Select a holding %\n4. Verify both become enabled",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    rc.amount_input().press_sequentially("100000", delay=10)
    page.wait_for_timeout(500)
    case.click(rc.income_stream_combobox(), "'Select Income Stream' select")
    rc.open_and_pick(rc.income_stream_combobox(), "Dividends")

    case.step(2, "Verify both buttons are still disabled")
    still_disabled = rc.generate_memo_button.is_disabled() and rc.add_to_project_button.is_disabled()
    case.check("Generate Memo/Add to Project disabled before holding % is selected", still_disabled,
               expected=True, actual=still_disabled)

    case.step(3, "Select a holding %")
    case.click(rc.holding_percent_combobox(), "'Select holding %' select")
    hp_options = rc.open_listbox_options(rc.holding_percent_combobox())
    hp_options.filter(has_text="7%").first.click()
    page.wait_for_timeout(1000)

    case.step(4, "Verify both buttons are now enabled")
    now_enabled = not rc.generate_memo_button.is_disabled() and not rc.add_to_project_button.is_disabled()
    case.check("Generate Memo/Add to Project become enabled once holding % is selected", now_enabled,
               expected=True, actual=now_enabled)

    ok = still_disabled and now_enabled
    actual = ("'Generate Memo'/'Add to Project' correctly followed the full-chain dependency." if ok else
              "The buttons' enabled state did not follow the expected dependency chain.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_23_generate_memo_downloads_real_file(page, result):
    case = Case(
        page, "RepCalc_23", FEATURE, "'Generate Memo' downloads a real, non-empty .docx file",
        description="With AU->SG/Dividends/7% complete, clicking 'Generate Memo' must download a real, "
                     "non-empty .docx memo.",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Click 'Generate Memo'\n3. Verify a real, non-empty .docx download completed",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)

    case.step(2, "Click 'Generate Memo'")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(rc.generate_memo_button, "'Generate Memo' button")
    download = dl_info.value

    case.step(3, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and filename.lower().endswith(".docx") and size > 0
    case.check("Generate Memo produces a real, non-empty .docx file with no failure", ok,
               expected="failure=None, filename ends with .docx, size>0",
               actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"'Generate Memo' correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"'Generate Memo' did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_24_get_forms_modal_shows_real_form_list(page, result):
    case = Case(
        page, "RepCalc_24", FEATURE, "'Get Forms' opens a modal with the real, jurisdiction-specific form list",
        description="With Australia/Singapore selected, clicking 'Get Forms' must open a modal reading "
                     "'CIT Returns and WHT deduction/Treaty form of Australia.' with a real Title/"
                     "Description/Application Date/Last Reviewed/Download table.",
        precondition="User is logged in, Australia+Singapore selected on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select Australia and Singapore\n"
              "2. Click 'Get Forms'\n3. Verify the modal shows the real form list",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")

    case.step(2, "Click 'Get Forms'")
    case.click(rc.get_forms_button, "'Get Forms' button")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the modal content")
    heading_ok = case.verify_visible(
        page.get_by_text("CIT Returns and WHT deduction/Treaty form of Australia.", exact=True), "modal heading")
    row_ok = case.verify_visible(page.get_by_text("Form:", exact=False).first, "a real form row")
    ok = heading_ok and row_ok
    case.check("'Get Forms' modal shows the real jurisdiction-specific form list", ok,
               expected="heading + row visible", actual=f"heading={heading_ok}, row={row_ok}")

    actual = ("'Get Forms' correctly opened with the real, jurisdiction-specific form list." if ok else
              "The 'Get Forms' modal did not show the expected real content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_25_get_forms_download_link_downloads_real_file(page, result):
    case = Case(
        page, "RepCalc_25", FEATURE, "A form's download link in 'Get Forms' downloads a real, non-empty file",
        description="Inside the 'Get Forms' modal, clicking the first 'English' download link must trigger "
                     "a real, non-empty file download.",
        precondition="User is logged in, Australia+Singapore selected, 'Get Forms' modal open.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select Australia+Singapore, open 'Get Forms'\n"
              "2. Click the first 'English' download link\n3. Verify a real, non-empty download completed",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    case.click(rc.get_forms_button, "'Get Forms' button")
    page.wait_for_timeout(1000)

    case.step(2, "Click the first 'English' download link")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(page.get_by_text("English", exact=True).first, "'English' download link")
    download = dl_info.value

    case.step(3, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and size > 0
    case.check("The form's download link produces a real, non-empty file with no failure", ok,
               expected="failure=None, size>0", actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The form download link correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"The form download link did not produce a valid download (failure={failure}, "
              f"filename={filename!r}, size={size}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_26_get_forms_close_button_closes_modal(page, result):
    case = Case(
        page, "RepCalc_26", FEATURE, "The 'Get Forms' modal's Close button closes it",
        description="With the 'Get Forms' modal open, clicking 'Close' must close it.",
        precondition="User is logged in, Australia+Singapore selected, 'Get Forms' modal open.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select Australia+Singapore, open 'Get Forms'\n"
              "2. Click 'Close'\n3. Verify the modal is closed",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    case.click(rc.get_forms_button, "'Get Forms' button")
    page.wait_for_timeout(1000)

    case.step(2, "Click 'Close'")
    case.click(page.get_by_role("button", name="Close"), "'Close' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify the modal is closed")
    ok = page.get_by_text("CIT Returns and WHT deduction/Treaty form of Australia.", exact=True).count() == 0
    case.check("The 'Get Forms' modal is closed", ok, expected="not visible", actual=not ok)

    actual = "The 'Get Forms' modal's Close button correctly closed it." if ok else "The modal did not close as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_27_add_to_project_popup_shows_expected_elements(page, result):
    case = Case(
        page, "RepCalc_27", FEATURE, "'Add to Project' popup shows both name fields, both options and buttons",
        description="With AU->SG/Dividends/7% complete, clicking 'Add to Project' must open a popup with "
                     "'New Project'/'To an Existing Project' options, a 'Project Name' field "
                     "(`input[name='project']`) AND a separate required 'Title' field "
                     "(`input[name='name']`) - confirmed live these are two distinct required inputs "
                     "(both happen to share the same duplicate `id='name'`, a real markup defect), not one.",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Click 'Add to Project'\n3. Verify the popup's expected elements",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)

    case.step(2, "Click 'Add to Project'")
    case.click(rc.add_to_project_button, "'Add to Project' button")
    page.wait_for_timeout(800)

    case.step(3, "Verify the popup's elements")
    dialog = page.locator(".rs-modal, [role='dialog']").filter(has_text="Add to Project")
    new_ok = case.verify_visible(dialog.get_by_text("New Project", exact=True), "'New Project' option")
    existing_ok = case.verify_visible(dialog.get_by_text("To an Existing Project", exact=True), "'To an Existing Project' option")
    project_name_ok = case.verify_visible(dialog.locator("input[name='project']"), "'Project Name' input")
    title_ok = case.verify_visible(dialog.locator("input[name='name']"), "'Title' input")
    add_ok = case.verify_visible(dialog.get_by_role("button", name="Add"), "'Add' button")
    cancel_ok = case.verify_visible(dialog.get_by_role("button", name="Cancel"), "'Cancel' button")
    ok = new_ok and existing_ok and project_name_ok and title_ok and add_ok and cancel_ok
    case.check("Add to Project popup shows all expected elements", ok, expected="all 6 elements visible",
               actual=f"new={new_ok}, existing={existing_ok}, project_name={project_name_ok}, title={title_ok}, "
                      f"add={add_ok}, cancel={cancel_ok}")

    actual = "The 'Add to Project' popup correctly showed all expected elements." if ok else \
        "The 'Add to Project' popup was missing one or more expected elements."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_28_add_to_project_creates_new_project(page, result):
    import time
    tag = str(int(time.time()))
    project_name = f"RepCalcQA_{tag}"
    case = Case(
        page, "RepCalc_28", FEATURE, "'Add to Project' can create a new project from the calculation",
        description="With AU->SG/Dividends/7% complete, creating a uniquely-named new project via "
                     "'Add to Project' must succeed. Confirmed live the dialog has TWO required fields - "
                     "'Project Name' (`input[name='project']`) and 'Title' (`input[name='name']`) - both "
                     "must be filled; submitting fires 'POST .../api/Project/AddToProject' returning "
                     "`{\"isSuccess\":true}` (captured directly, since `page.request` calls bypass the "
                     "app's JWT bearer auth and get a 401 - the browser's own authenticated request is the "
                     "only reliable signal here). Cleanup re-uses the proven Tools > Projects delete flow "
                     "rather than an unauthenticated direct API call.",
        precondition="User is logged in, AU->SG/Dividends/7% completed on Repatriation Calculator.",
        test_data=f"Project name: {project_name}",
        steps="1. Log in, open Repatriation Calculator, complete AU->SG/Dividends/7%\n"
              "2. Open 'Add to Project', fill both 'Project Name' and 'Title', click 'Add'\n"
              "3. Verify the real AddToProject response\n"
              "4. Clean up via Tools > Projects",
    )
    rc = _login_and_open(case, page)
    _complete_au_sg_dividends_7pct(case, page, rc)
    case.click(rc.add_to_project_button, "'Add to Project' button")
    page.wait_for_timeout(800)
    dialog = page.locator(".rs-modal, [role='dialog']").filter(has_text="Add to Project")

    case.step(2, "Fill both required fields and submit")
    case.fill(dialog.locator("input[name='project']"), project_name, "'Project Name' input")
    case.fill(dialog.locator("input[name='name']"), project_name, "'Title' input")
    with page.expect_response(lambda r: r.url.rstrip("/").endswith("/Project/AddToProject")) as resp_info:
        case.click(dialog.get_by_role("button", name="Add"), "'Add' button")
    add_response = resp_info.value
    page.wait_for_timeout(1000)

    case.step(3, "Verify the real AddToProject response")
    status_ok = add_response.status == 200
    success_ok = add_response.json().get("isSuccess") is True
    ok = status_ok and success_ok
    case.check("'Add to Project' fires a 200 AddToProject call reporting isSuccess:true", ok,
               expected="status=200, isSuccess=true",
               actual=f"status={add_response.status}, body={add_response.json()}")

    case.step(4, "Clean up the created project via Tools > Projects")
    ToolsMenu(page).open_item("Projects")
    projects = ProjectsPage(page)
    if projects.project_exists(project_name):
        case.click(projects.row_action(project_name, "Delete"), f"'Delete' action for '{project_name}'")
        page.wait_for_timeout(500)
        case.click(projects.delete_confirm_button, "'Delete' confirm button")
        page.wait_for_timeout(1000)

    actual = (f"'Add to Project' correctly created project '{project_name}', confirmed via its real "
              f"AddToProject response ({add_response.json()})." if ok else
              f"'Add to Project' did not report success for '{project_name}' "
              f"(status={add_response.status}, body={add_response.json()}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_29_start_over_shows_confirm_dialog(page, result):
    case = Case(
        page, "RepCalc_29", FEATURE, "'Start over' shows a confirmation dialog before resetting",
        description="Clicking 'Start over' must show 'Are you sure to reset all your selections?' with "
                     "Cancel/Yes buttons, not reset immediately.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in and open Repatriation Calculator\n2. Click 'Start over'\n"
              "3. Verify the confirmation dialog",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Click 'Start over'")
    case.click(rc.start_over_button, "'Start over' button")
    page.wait_for_timeout(600)

    case.step(3, "Verify the confirmation dialog")
    message_ok = case.verify_visible(page.get_by_text("Are you sure to reset all your selections?", exact=True),
                                      "confirmation message")
    yes_ok = case.verify_visible(rc.start_over_confirm_yes, "'Yes' button")
    cancel_ok = case.verify_visible(rc.start_over_confirm_cancel, "'Cancel' button")
    ok = message_ok and yes_ok and cancel_ok
    case.check("'Start over' shows a confirmation dialog with Cancel/Yes", ok, expected="all 3 visible",
               actual=f"message={message_ok}, yes={yes_ok}, cancel={cancel_ok}")
    rc.start_over_confirm_cancel.click()

    actual = "'Start over' correctly showed a confirmation dialog before resetting." if ok else \
        "'Start over' did not show the expected confirmation dialog."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_30_start_over_cancel_keeps_current_state(page, result):
    case = Case(
        page, "RepCalc_30", FEATURE, "'Start over' > Cancel keeps the current selections",
        description="With Australia selected as Source Jurisdiction, clicking 'Start over' then 'Cancel' "
                     "must leave Australia still selected.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open Repatriation Calculator, select Australia as Source\n"
              "2. Click 'Start over' then 'Cancel'\n3. Verify Australia is still selected",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")

    case.step(2, "Click 'Start over' then 'Cancel'")
    case.click(rc.start_over_button, "'Start over' button")
    page.wait_for_timeout(500)
    case.click(rc.start_over_confirm_cancel, "'Cancel' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify Australia is still selected")
    ok = case.verify_visible(page.get_by_text("Australia", exact=True).first, "'Australia' still selected")
    case.check("Cancelling 'Start over' leaves the current selection intact", ok, expected="Australia visible",
               actual=ok)

    actual = "Cancelling 'Start over' correctly left the current selections intact." if ok else \
        "Cancelling 'Start over' did not preserve the current selections as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_31_start_over_yes_resets_to_placeholder_state(page, result):
    case = Case(
        page, "RepCalc_31", FEATURE, "'Start over' > Yes resets the form to its placeholder state",
        description="With AU->SG/100000 set, confirming 'Start over' must reset Source/Residence Jurisdiction "
                     "back to 'Select' and clear the Repatriation Amount.",
        precondition="User is logged in, Australia+Singapore+100000 set on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select Australia, Singapore and enter 100000\n"
              "2. Click 'Start over' then 'Yes'\n3. Verify the form reset to its placeholder state",
    )
    rc = _login_and_open(case, page)
    case.click(rc.row_combobox("Source Jurisdiction"), "'Source Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Source Jurisdiction"), "Australia")
    case.click(rc.row_combobox("Residence Jurisdiction"), "'Residence Jurisdiction' select")
    rc.open_and_pick(rc.row_combobox("Residence Jurisdiction"), "Singapore")
    rc.amount_input().press_sequentially("100000", delay=10)
    page.wait_for_timeout(500)

    case.step(2, "Click 'Start over' then 'Yes'")
    rc.start_over_and_confirm()

    case.step(3, "Verify the form reset")
    placeholder_ok = case.verify_visible(rc.instructions_heading, "instructions banner (placeholder state)")
    amount_gone = rc.amount_input().count() == 0 or rc.amount_input().input_value() == ""
    ok = placeholder_ok and amount_gone
    case.check("'Start over' > Yes resets the form to its placeholder state", ok,
               expected="placeholder visible, amount cleared", actual=f"placeholder={placeholder_ok}, amount_gone={amount_gone}")

    actual = "'Start over' > Yes correctly reset the form to its placeholder state." if ok else \
        "Confirming 'Start over' did not reset the form as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_repcalc_32_mode_toggle_switches_to_entity_fields(page, result):
    case = Case(
        page, "RepCalc_32", FEATURE, "Selecting 'By Entity' switches the form to Corporate Group/Company fields",
        description="Clicking 'By Entity' must replace Source/Residence Jurisdiction with Corporate Group "
                     "and Source/Residence Company fields.",
        precondition="User is logged in and on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in and open Repatriation Calculator\n2. Click 'By Entity'\n"
              "3. Verify Corporate Group/Source Company/Residence Company fields appear",
    )
    rc = _login_and_open(case, page)
    case.step(2, "Select 'By Entity'")
    case.click(rc.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(800)

    case.step(3, "Verify the entity-mode fields")
    cg_ok = case.verify_visible(page.get_by_text("Corporate Group", exact=True), "'Corporate Group' label")
    src_ok = case.verify_visible(page.get_by_text("Source Company", exact=True), "'Source Company' label")
    res_ok = case.verify_visible(page.get_by_text("Residence Company", exact=True), "'Residence Company' label")
    jur_gone = page.get_by_text("Source Jurisdiction", exact=True).count() == 0
    ok = cg_ok and src_ok and res_ok and jur_gone
    case.check("'By Entity' mode shows Corporate Group/Company fields instead of jurisdiction fields", ok,
               expected="all entity fields visible, jurisdiction fields gone",
               actual=f"cg={cg_ok}, src={src_ok}, res={res_ok}, jurisdiction_gone={jur_gone}")

    actual = "Selecting 'By Entity' correctly switched to the Corporate Group/Company fields." if ok else \
        "Selecting 'By Entity' did not switch the form fields as expected."
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_33_corporate_group_lists_real_entity_charts(page, result):
    case = Case(
        page, "RepCalc_33", FEATURE, "Corporate Group dropdown lists this account's real entity charts",
        description="The Corporate Group dropdown (By Entity mode) must list real, account-specific entity "
                     "charts, including the known 'Demo Entity Chart'.",
        precondition="User is logged in, 'By Entity' mode selected on Repatriation Calculator.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select 'By Entity'\n"
              "2. Open the Corporate Group dropdown\n3. Verify 'Demo Entity Chart' is listed",
    )
    rc = _login_and_open(case, page)
    case.click(rc.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(800)

    case.step(2, "Open the Corporate Group dropdown")
    cg_cb = rc.row_combobox("Corporate Group")
    options = rc.open_listbox_options(cg_cb)
    texts = options.all_inner_texts()

    case.step(3, "Verify 'Demo Entity Chart' is listed")
    ok = "Demo Entity Chart" in texts and len(texts) >= 5
    case.check("Corporate Group lists real entity charts including 'Demo Entity Chart'", ok,
               expected="'Demo Entity Chart' in list, >=5 charts total",
               actual=f"count={len(texts)}, has_demo={'Demo Entity Chart' in texts}")

    actual = (f"The Corporate Group dropdown correctly listed {len(texts)} real entity charts, including "
              f"'Demo Entity Chart'." if ok else
              f"The Corporate Group dropdown did not list the expected real entity charts (got {texts}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_34_source_and_residence_company_populate_from_selected_chart(page, result):
    case = Case(
        page, "RepCalc_34", FEATURE, "Source/Residence Company options populate from the selected entity chart",
        description="After selecting 'Demo Entity Chart' as Corporate Group, both Source Company and "
                     "Residence Company dropdowns must list that chart's real entities.",
        precondition="User is logged in, 'By Entity' mode + 'Demo Entity Chart' selected.",
        test_data="Corporate Group: Demo Entity Chart",
        steps="1. Log in, open Repatriation Calculator, select 'By Entity' and 'Demo Entity Chart'\n"
              "2. Open Source Company and Residence Company dropdowns\n"
              "3. Verify both list the same real entity set for that chart",
    )
    rc = _login_and_open(case, page)
    case.click(rc.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(800)
    cg_cb = rc.row_combobox("Corporate Group")
    case.click(cg_cb, "'Corporate Group' select")
    rc.open_and_pick(cg_cb, "Demo Entity Chart")

    case.step(2, "Open Source Company and Residence Company dropdowns")
    src_options = rc.open_listbox_options(rc.row_combobox("Source Company"))
    src_texts = src_options.all_inner_texts()
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    res_options = rc.open_listbox_options(rc.row_combobox("Residence Company"))
    res_texts = res_options.all_inner_texts()

    case.step(3, "Verify both populate with real entities")
    ok = len(src_texts) > 0 and src_texts == res_texts
    case.check("Source/Residence Company both list the same real entity set", ok,
               expected="non-empty, identical lists", actual=f"src_count={len(src_texts)}, equal={src_texts == res_texts}")

    actual = (f"Source and Residence Company both correctly populated with {len(src_texts)} real entities "
              f"from 'Demo Entity Chart'." if ok else
              "Source/Residence Company did not populate as expected from the selected entity chart.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_35_no_treaty_entity_pairing_shows_informational_warning(page, result):
    case = Case(
        page, "RepCalc_35", FEATURE, "A no-treaty entity pairing shows a real informational warning, not a crash",
        description="Selecting 'Rudyard William' as Source Company and '3rd party2 new' as Residence Company "
                     "(confirmed live: no treaty between their underlying countries) must show a modal "
                     "reading 'No treaty rate is available between ... Only domestic rate will apply.' - "
                     "distinct from the blocking same-jurisdiction message, this is informational and the "
                     "calculation proceeds using the domestic rate alone.",
        precondition="User is logged in, 'By Entity' + 'Demo Entity Chart' selected.",
        test_data="Source Company: Rudyard William, Residence Company: 3rd party2 new",
        steps="1. Log in, open Repatriation Calculator, select 'By Entity' and 'Demo Entity Chart'\n"
              "2. Select 'Rudyard William' as Source Company and '3rd party2 new' as Residence Company\n"
              "3. Verify the 'no treaty rate available' informational message",
    )
    rc = _login_and_open(case, page)
    case.click(rc.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(800)
    cg_cb = rc.row_combobox("Corporate Group")
    case.click(cg_cb, "'Corporate Group' select")
    rc.open_and_pick(cg_cb, "Demo Entity Chart")

    case.step(2, "Select the no-treaty entity pair")
    src_cb = rc.row_combobox("Source Company")
    case.click(src_cb, "'Source Company' select")
    rc.open_and_pick(src_cb, "Rudyard William")
    res_cb = rc.row_combobox("Residence Company")
    case.click(res_cb, "'Residence Company' select")
    rc.open_and_pick(res_cb, "3rd party2 new")
    page.wait_for_timeout(1000)

    case.step(3, "Verify the informational warning message")
    modal_text = rc.message_modal.inner_text() if rc.message_modal.count() else ""
    ok = "No treaty rate is available between" in modal_text and "Only domestic rate will apply" in modal_text
    case.check("The no-treaty entity pairing shows the real informational warning", ok,
               expected="'No treaty rate is available between...Only domestic rate will apply' present",
               actual=modal_text)
    if rc.message_modal_cancel.count():
        rc.message_modal_cancel.click()

    actual = ("The no-treaty entity pairing correctly showed the real informational warning message." if ok else
              f"The no-treaty pairing did not show the expected warning (modal_text={modal_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_repcalc_36_mode_toggle_back_to_jurisdiction_resets_entity_fields(page, result):
    case = Case(
        page, "RepCalc_36", FEATURE, "Switching back to 'By Jurisdiction' resets the entity-specific selections",
        description="After selecting 'By Entity' and 'Demo Entity Chart', switching back to "
                     "'By Jurisdiction' must show the jurisdiction fields again with no leftover entity "
                     "selection, rather than mixing state between modes.",
        precondition="User is logged in, 'By Entity' + 'Demo Entity Chart' selected.",
        test_data="-",
        steps="1. Log in, open Repatriation Calculator, select 'By Entity' and 'Demo Entity Chart'\n"
              "2. Switch back to 'By Jurisdiction'\n3. Verify the jurisdiction fields show no leftover entity data",
    )
    rc = _login_and_open(case, page)
    case.click(rc.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(800)
    cg_cb = rc.row_combobox("Corporate Group")
    case.click(cg_cb, "'Corporate Group' select")
    rc.open_and_pick(cg_cb, "Demo Entity Chart")

    case.step(2, "Switch back to 'By Jurisdiction'")
    case.click(rc.mode_by_jurisdiction, "'By Jurisdiction' radio")
    page.wait_for_timeout(800)

    case.step(3, "Verify jurisdiction fields with no leftover entity state")
    src_label_ok = case.verify_visible(page.get_by_text("Source Jurisdiction", exact=True), "'Source Jurisdiction' label")
    demo_gone = page.get_by_text("Demo Entity Chart", exact=True).count() == 0
    select_placeholder_ok = page.locator("tr", has_text="Source Jurisdiction").get_by_text("Select", exact=True).count() > 0
    ok = src_label_ok and demo_gone and select_placeholder_ok
    case.check("Switching back to 'By Jurisdiction' resets entity selections", ok,
               expected="jurisdiction fields shown, no leftover entity chart, placeholder 'Select'",
               actual=f"src_label={src_label_ok}, demo_gone={demo_gone}, placeholder={select_placeholder_ok}")

    actual = "Switching back to 'By Jurisdiction' correctly reset the entity-specific selections." if ok else \
        "Switching back to 'By Jurisdiction' left stale entity-mode state behind."
    result(case, actual, ok)
    assert ok, actual
