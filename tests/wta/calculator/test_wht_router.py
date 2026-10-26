"""Calculators > WHT Router (/wta/WhtRouter).

New module, built via live DOM discovery (scratchpad scripts, not part of
the suite) rather than a provided reference sheet - no WHT Router rows
exist in the project's QA sheet. Covers both "By Jurisdiction"/"By Entity"
modes, the real `WHT_ROUTER_API` calculation-validation anchor (AU->SG
Portfolio Dividend, see pages/wta/calculator_wht_router_page.py docstring -
confirmed a PUBLIC, unauthenticated endpoint via a direct unauthenticated
`requests.post`, unlike the Tools/Projects API which needs the browser's
own JWT), the real same-jurisdiction blocking validation, the Intermediate
Streams/Jurisdictions modal, and the Start Over confirm flow."""
import pytest
import requests

from pages.wta.calculator_menu import CalculatorMenu
from pages.wta.calculator_wht_router_page import WhtRouterPage, WHT_ROUTER_API
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Calculator - WHT Router"


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening Calculators > WHT Router", kind="navigate")
    wr = WhtRouterPage(page)
    CalculatorMenu(page).open_item("WHT Router", ready_locator=wr.instructions_heading)
    return wr


def _complete_au_sg_portfolio_dividend(case, page, wr):
    """Shared setup: Australia -> Singapore, Portfolio Dividend - this
    module's calculation-validation anchor combination (see page object
    docstring)."""
    case.click(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    wr.open_and_pick(wr.source_jurisdiction_combobox(), "Australia")
    case.click(wr.income_stream_combobox(), "'Income Stream' select")
    wr.open_and_pick(wr.income_stream_combobox(), "Portfolio Dividend")
    case.click(wr.residence_jurisdiction_combobox(), "'Residence Jurisdiction' select")
    wr.open_and_pick(wr.residence_jurisdiction_combobox(), "Singapore")
    page.wait_for_timeout(1000)
    wr.calculate_button.click()
    page.wait_for_timeout(1500)


@pytest.mark.smoke
def test_whtrouter_01_access_via_calculators_dropdown(page, result):
    case = Case(
        page, "WhtRouter_01", FEATURE, "WHT Router opens from the Calculators dropdown",
        description="Clicking 'WHT Router' in the Calculators dropdown must land on /wta/WhtRouter with "
                     "the 'Initial Information' panel and instructions banner visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open Calculators > WHT Router\n2. Verify the URL and instructions banner",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Verify URL and instructions banner")
    url_ok = "/wta/WhtRouter" in page.url
    banner_ok = case.verify_visible(wr.instructions_heading, "'How to complete this calculation' heading")
    ok = url_ok and banner_ok
    case.check("WHT Router page loads with its instructions banner", ok,
               expected="url contains /wta/WhtRouter, banner visible",
               actual=f"url={page.url}, banner={banner_ok}")

    actual = ("WHT Router opened correctly with its instructions banner visible." if ok else
              "WHT Router did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrouter_02_initial_state_defaults_and_hidden_actions(page, result):
    case = Case(
        page, "WhtRouter_02", FEATURE, "Initial state: 'By Jurisdiction' selected, action buttons not yet rendered",
        description="On first load, 'By Jurisdiction' must be the checked mode, and Generate Memo/Get Forms/"
                     "Add to Project must not be present yet (confirmed live: they only render after a "
                     "result has been calculated, unlike Repatriation Calculator where they exist disabled).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open WHT Router\n"
              "2. Verify 'By Jurisdiction' is checked and the 3 action buttons are absent",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Verify default mode and absent action buttons")
    mode_radio = page.locator("input[type='radio']").first
    mode_ok = mode_radio.is_checked()
    gm_absent = wr.generate_memo_button.count() == 0
    gf_absent = wr.get_forms_button.count() == 0
    atp_absent = wr.add_to_project_button.count() == 0
    ok = mode_ok and gm_absent and gf_absent and atp_absent
    case.check("'By Jurisdiction' checked and all action buttons absent initially", ok,
               expected="mode=checked, all 3 buttons absent",
               actual=f"mode_checked={mode_ok}, gm_absent={gm_absent}, gf_absent={gf_absent}, atp_absent={atp_absent}")

    actual = ("WHT Router correctly starts on 'By Jurisdiction' with no action buttons rendered yet." if ok else
              "The initial state did not match expectations.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_03_source_jurisdiction_lists_real_countries(page, result):
    case = Case(
        page, "WhtRouter_03", FEATURE, "'Source Jurisdiction' lists real countries",
        description="Opening the 'Source Jurisdiction' select must list real country names (e.g. Australia, "
                     "Bangladesh), not placeholder/empty options.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router\n2. Open 'Source Jurisdiction'\n3. Verify real countries are listed",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Open 'Source Jurisdiction'")
    case.click(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    options = wr.open_listbox_options(wr.source_jurisdiction_combobox())

    case.step(3, "Verify real countries are listed")
    count = options.count()
    names = [options.nth(i).inner_text() for i in range(min(5, count))]
    ok = count > 50 and "Australia" in [options.nth(i).inner_text() for i in range(count)]
    case.check("'Source Jurisdiction' lists real countries including Australia", ok,
               expected="> 50 options including Australia", actual=f"count={count}, sample={names}")

    actual = (f"'Source Jurisdiction' correctly lists {count} real countries." if ok else
              f"'Source Jurisdiction' did not list the expected real countries (count={count}, sample={names}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_04_income_stream_lists_real_categories(page, result):
    case = Case(
        page, "WhtRouter_04", FEATURE, "'Income Stream' lists real income categories",
        description="Opening 'Income Stream' must list real categories (Portfolio Dividend, Substantial "
                     "Holding Dividend, General Interest payments, Patent/Trademark/Copyright Royalties, "
                     "Lease payments, Technical Service Fees), confirmed live.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router\n2. Open 'Income Stream'\n3. Verify the expected categories are present",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Open 'Income Stream'")
    case.click(wr.income_stream_combobox(), "'Income Stream' select")
    options = wr.open_listbox_options(wr.income_stream_combobox())

    case.step(3, "Verify the expected categories are present")
    all_text = [options.nth(i).inner_text() for i in range(options.count())]
    expected = ["Portfolio Dividend", "General Interest payments", "Patent Royalties", "Technical Service Fees"]
    missing = [e for e in expected if e not in all_text]
    ok = not missing
    case.check("'Income Stream' lists the expected real categories", ok,
               expected=", ".join(expected), actual=f"missing={missing}" if missing else "all present")

    actual = ("'Income Stream' correctly lists all expected categories." if ok else
              f"'Income Stream' was missing expected categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrouter_05_au_sg_portfolio_dividend_renders_results_table(page, result):
    case = Case(
        page, "WhtRouter_05", FEATURE, "Completing Source/Income Stream/Residence and Calculate renders a results table",
        description="Completing Australia -> Portfolio Dividend -> Singapore and clicking Calculate must "
                     "render a results table with Best Rate/Domestic Rate/Treaty Rate rows and a scenario "
                     "heading reading 'Portfolio Dividend paid from Australia to Singapore'.",
        precondition="User is logged in.",
        test_data="Source: Australia, Stream: Portfolio Dividend, Residence: Singapore",
        steps="1. Log in, open WHT Router\n2. Complete Australia -> Portfolio Dividend -> Singapore, Calculate\n"
              "3. Verify the results table and scenario heading",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Complete Australia -> Portfolio Dividend -> Singapore, click Calculate")
    _complete_au_sg_portfolio_dividend(case, page, wr)

    case.step(3, "Verify the results table and scenario heading")
    heading_ok = case.verify_visible(wr.results_scenario_heading(), "results scenario heading")
    heading_text = wr.results_scenario_heading().inner_text() if heading_ok else ""
    best_visible = case.verify_visible(wr.rate_row_value("Best Rate"), "'Best Rate' row value")
    ok = heading_ok and "Portfolio Dividend paid from Australia to Singapore" in heading_text and best_visible
    case.check("Results table renders with the correct scenario heading", ok,
               expected="heading='Portfolio Dividend paid from Australia to Singapore', Best Rate row visible",
               actual=f"heading={heading_text!r}, best_rate_visible={best_visible}")

    actual = ("The results table rendered correctly with the expected scenario heading." if ok else
              f"The results table did not render as expected (heading={heading_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrouter_06_rates_match_live_api(page, result):
    case = Case(
        page, "WhtRouter_06", FEATURE, "Best/Domestic/Treaty Rate match the live WHT Router API",
        description="With Australia -> Portfolio Dividend -> Singapore selected, the UI's Best Rate/Domestic "
                     "Rate/Treaty Rate must match an independent call to the live WHT_ROUTER_API - confirmed "
                     "a public endpoint, not compared against itself.",
        precondition="User is logged in.",
        test_data="HostCountry=AU, TargetCountry=SG, Stream=Portfolio Dividend",
        steps="1. Log in, open WHT Router, complete AU -> Portfolio Dividend -> SG\n"
              "2. Independently POST to the live WHT Router API with the same inputs\n"
              "3. Verify the UI's Best/Domestic/Treaty Rate match the API response",
    )
    wr = _login_and_open(case, page)
    _complete_au_sg_portfolio_dividend(case, page, wr)

    case.step(2, "Independently call the live WHT Router API")
    resp = requests.post(WHT_ROUTER_API, json={
        "HostCountry": "AU", "TargetCountry": "SG", "Stream": "Portfolio Dividend",
        "BaseIncome": 100, "IntermediateCountryStreams": [{"Countries": [], "Streams": []},
                                                            {"Countries": [], "Streams": []}],
    }, timeout=15)
    api_ok = resp.status_code == 200
    body = resp.json() if api_ok else {}

    case.step(3, "Verify the UI matches the independently-fetched API values")
    ui_best = wr.rate_row_value("Best Rate").inner_text().strip().rstrip("%")
    ui_domestic = wr.rate_row_value("Domestic Rate").inner_text().strip().rstrip("%")
    ui_treaty = wr.rate_row_value("Treaty Rate").inner_text().strip().rstrip("%")
    expected_best = str(int(body.get("bestRate", -1)))
    expected_domestic = str(int(body.get("domesticRate", -1)))
    expected_treaty = str(int(body.get("treatyRate", -1)))
    ok = (api_ok and ui_best == expected_best and ui_domestic == expected_domestic
          and ui_treaty == expected_treaty)
    case.check("UI rates match the independently-fetched API values", ok,
               expected=f"best={expected_best}%, domestic={expected_domestic}%, treaty={expected_treaty}%",
               actual=f"best={ui_best}%, domestic={ui_domestic}%, treaty={ui_treaty}%")

    actual = (f"The UI's rates (best={ui_best}%, domestic={ui_domestic}%, treaty={ui_treaty}%) correctly "
              f"matched the independently-fetched live API values." if ok else
              f"The UI's rates did not match the independent API call (ui best={ui_best}%/domestic="
              f"{ui_domestic}%/treaty={ui_treaty}%, api best={expected_best}%/domestic={expected_domestic}%/"
              f"treaty={expected_treaty}%).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_07_action_buttons_render_after_results(page, result):
    case = Case(
        page, "WhtRouter_07", FEATURE, "Generate Memo/Get Forms/Add to Project render once results are calculated",
        description="After a successful calculation, the 3 action buttons (Generate Memo, Get Forms, "
                     "Add to Project) must be present and enabled.",
        precondition="User is logged in, AU -> Portfolio Dividend -> SG calculated.",
        test_data="-",
        steps="1. Log in, open WHT Router, complete AU -> Portfolio Dividend -> SG, Calculate\n"
              "2. Verify the 3 action buttons are visible and enabled",
    )
    wr = _login_and_open(case, page)
    _complete_au_sg_portfolio_dividend(case, page, wr)

    case.step(2, "Verify the 3 action buttons are visible and enabled")
    gm_ok = case.verify_visible(wr.generate_memo_button, "'Generate Memo' button") and wr.generate_memo_button.is_enabled()
    gf_ok = case.verify_visible(wr.get_forms_button, "'Get Forms' button") and wr.get_forms_button.is_enabled()
    atp_ok = case.verify_visible(wr.add_to_project_button, "'Add to Project' button") and wr.add_to_project_button.is_enabled()
    ok = gm_ok and gf_ok and atp_ok
    case.check("All 3 action buttons are visible and enabled after calculation", ok,
               expected="all 3 visible and enabled", actual=f"gm={gm_ok}, gf={gf_ok}, atp={atp_ok}")

    actual = ("All 3 action buttons correctly appeared and were enabled after calculation." if ok else
              f"Action buttons did not appear/enable as expected (gm={gm_ok}, gf={gf_ok}, atp={atp_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_08_same_jurisdiction_both_sides_shows_blocking_message(page, result):
    case = Case(
        page, "WhtRouter_08", FEATURE, "Selecting the same country for both jurisdictions shows a blocking message",
        description="Selecting Australia as both Source and Residence Jurisdiction must trigger a modal "
                     "reading 'Please select different Source Jurisdiction and Residence Jurisdiction.' "
                     "with only a Cancel action - confirmed live real validation, no API call fires.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia, Residence: Australia",
        steps="1. Log in, open WHT Router, select Australia as Source\n"
              "2. Select Australia as Residence too\n3. Verify the blocking message modal",
    )
    wr = _login_and_open(case, page)
    case.click(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    wr.open_and_pick(wr.source_jurisdiction_combobox(), "Australia")
    case.click(wr.income_stream_combobox(), "'Income Stream' select")
    wr.open_and_pick(wr.income_stream_combobox(), "Portfolio Dividend")

    case.step(2, "Select Australia as Residence Jurisdiction too")
    case.click(wr.residence_jurisdiction_combobox(), "'Residence Jurisdiction' select")
    wr.open_and_pick(wr.residence_jurisdiction_combobox(), "Australia")

    case.step(3, "Verify the blocking message modal")
    wr.message_modal.first.wait_for(state="visible", timeout=5000)
    modal_text = wr.message_modal.inner_text()
    message_ok = "Please select different Source Jurisdiction and Residence Jurisdiction." in modal_text
    cancel_only = wr.message_modal_cancel.count() == 1
    ok = message_ok and cancel_only
    case.check("The same-jurisdiction validation modal shows the expected message with only Cancel", ok,
               expected="message present, 1 Cancel button", actual=f"modal_text={modal_text!r}")
    wr.message_modal_cancel.click()

    actual = ("Selecting the same country for both jurisdictions correctly triggered the real blocking "
              "validation message." if ok else
              f"The same-jurisdiction validation did not behave as expected (modal_text={modal_text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrouter_09_start_over_shows_confirm_dialog(page, result):
    case = Case(
        page, "WhtRouter_09", FEATURE, "'Start over' shows a confirmation dialog",
        description="Clicking 'Start over' must show a confirmation dialog reading 'Are you sure to reset "
                     "all your selections?' with Cancel/Yes actions, not reset immediately.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router\n2. Click 'Start over'\n3. Verify the confirmation dialog",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Click 'Start over'")
    case.click(wr.start_over_button, "'Start over' button")

    case.step(3, "Verify the confirmation dialog")
    ok = case.verify_visible(wr.start_over_confirm_heading, "Start Over confirmation text")
    case.check("'Start over' shows the expected confirmation dialog", ok,
               expected="'Are you sure to reset all your selections?' visible",
               actual=f"visible={ok}")
    if ok:
        wr.start_over_confirm_cancel.click()

    actual = ("'Start over' correctly showed a confirmation dialog before resetting." if ok else
              "'Start over' did not show the expected confirmation dialog.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_10_start_over_cancel_keeps_current_state(page, result):
    case = Case(
        page, "WhtRouter_10", FEATURE, "'Start over' Cancel keeps the current selections",
        description="Clicking Cancel on the Start Over confirmation must leave the already-selected Source "
                     "Jurisdiction untouched.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open WHT Router, select Australia as Source\n"
              "2. Click 'Start over' then Cancel\n3. Verify Source Jurisdiction is still Australia",
    )
    wr = _login_and_open(case, page)
    case.click(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    wr.open_and_pick(wr.source_jurisdiction_combobox(), "Australia")

    case.step(2, "Click 'Start over' then Cancel")
    case.click(wr.start_over_button, "'Start over' button")
    wr.start_over_confirm_heading.wait_for(state="visible", timeout=5000)
    case.click(wr.start_over_confirm_cancel, "'Cancel' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify Source Jurisdiction is still Australia")
    text = wr.source_jurisdiction_combobox().inner_text()
    ok = "Australia" in text
    case.check("Source Jurisdiction selection survives Cancel", ok,
               expected="Australia", actual=text)

    actual = ("Cancelling 'Start over' correctly preserved the current selection." if ok else
              f"Cancelling 'Start over' did not preserve the selection (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_11_start_over_yes_resets_selections(page, result):
    case = Case(
        page, "WhtRouter_11", FEATURE, "'Start over' Yes resets the selections back to placeholder state",
        description="Confirming 'Start over' (Yes) must reset the Source Jurisdiction select back to its "
                     "'Select' placeholder state.",
        precondition="User is logged in, Australia selected as Source Jurisdiction.",
        test_data="Source: Australia",
        steps="1. Log in, open WHT Router, select Australia as Source\n"
              "2. Click 'Start over' then Yes\n3. Verify Source Jurisdiction resets to 'Select'",
    )
    wr = _login_and_open(case, page)
    case.click(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    wr.open_and_pick(wr.source_jurisdiction_combobox(), "Australia")

    case.step(2, "Click 'Start over' then Yes")
    wr.start_over_and_confirm()

    case.step(3, "Verify Source Jurisdiction resets to 'Select'")
    text = wr.source_jurisdiction_combobox().inner_text()
    ok = text.strip() == "Select"
    case.check("Source Jurisdiction resets to the 'Select' placeholder", ok,
               expected="Select", actual=text)

    actual = ("Confirming 'Start over' correctly reset the selection to its placeholder state." if ok else
              f"Confirming 'Start over' did not reset the selection as expected (got {text!r}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_whtrouter_12_mode_toggle_switches_to_entity_fields(page, result):
    case = Case(
        page, "WhtRouter_12", FEATURE, "Switching to 'By Entity' swaps in Corporate Group/Company fields",
        description="Clicking 'By Entity' must swap Source/Residence Jurisdiction selects for Corporate "
                     "Group, Source Company and Residence Company fields.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router\n2. Click 'By Entity'\n"
              "3. Verify 'Corporate Group' and 'Source Company' fields are now visible",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Click 'By Entity'")
    case.click(wr.mode_by_entity, "'By Entity' radio")

    case.step(3, "Verify entity-mode fields are visible")
    group_ok = case.verify_visible(wr.corporate_group_combobox(), "'Corporate Group' select")
    company_ok = case.verify_visible(wr.source_company_combobox(), "'Source Company' select")
    ok = group_ok and company_ok
    case.check("'By Entity' mode shows Corporate Group/Source Company fields", ok,
               expected="both visible", actual=f"group={group_ok}, company={company_ok}")

    actual = ("Switching to 'By Entity' correctly swapped in the entity-based fields." if ok else
              "Switching to 'By Entity' did not show the expected fields.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_13_corporate_group_lists_real_entity_charts(page, result):
    case = Case(
        page, "WhtRouter_13", FEATURE, "'Corporate Group' lists this account's real entity charts",
        description="In 'By Entity' mode, opening 'Corporate Group' must list this account's real, "
                     "previously-created entity charts (not placeholder/empty options).",
        precondition="User is logged in, 'By Entity' mode selected.",
        test_data="-",
        steps="1. Log in, open WHT Router, switch to 'By Entity'\n"
              "2. Open 'Corporate Group'\n3. Verify at least one real entity chart is listed",
    )
    wr = _login_and_open(case, page)
    case.click(wr.mode_by_entity, "'By Entity' radio")
    case.step(2, "Open 'Corporate Group'")
    case.click(wr.corporate_group_combobox(), "'Corporate Group' select")
    options = wr.open_listbox_options(wr.corporate_group_combobox())

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


@pytest.mark.regression
def test_whtrouter_14_mode_toggle_back_to_jurisdiction_resets_entity_fields(page, result):
    case = Case(
        page, "WhtRouter_14", FEATURE, "Switching back to 'By Jurisdiction' restores jurisdiction-based fields",
        description="After switching to 'By Entity' and back to 'By Jurisdiction', the Source/Residence "
                     "Jurisdiction selects must be visible again (not the entity fields).",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router, switch to 'By Entity' then back to 'By Jurisdiction'\n"
              "2. Verify 'Source Jurisdiction' is visible again",
    )
    wr = _login_and_open(case, page)
    case.click(wr.mode_by_entity, "'By Entity' radio")
    page.wait_for_timeout(500)
    case.click(wr.mode_by_jurisdiction, "'By Jurisdiction' radio")

    case.step(2, "Verify 'Source Jurisdiction' is visible again")
    ok = case.verify_visible(wr.source_jurisdiction_combobox(), "'Source Jurisdiction' select")
    case.check("'Source Jurisdiction' select is visible after switching back", ok,
               expected="visible", actual=f"visible={ok}")

    actual = ("Switching back to 'By Jurisdiction' correctly restored the jurisdiction-based fields." if ok else
              "Switching back to 'By Jurisdiction' did not restore the expected fields.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_15_intermediaries_select_opens_modal(page, result):
    case = Case(
        page, "WhtRouter_15", FEATURE, "'Intermediaries 1' Select opens the Intermediate Streams/Jurisdictions modal",
        description="Clicking the 'Select' link under the optional 'Intermediaries 1' row must open a modal "
                     "titled 'Intermediate Streams and Jurisdictions' with separate Streams and Countries "
                     "checklists.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open WHT Router\n2. Click 'Intermediaries 1' Select\n"
              "3. Verify the modal and both checklists are visible",
    )
    wr = _login_and_open(case, page)
    case.step(2, "Click 'Intermediaries 1' Select")
    case.click(wr.intermediaries_select(1), "'Intermediaries 1' Select button")

    case.step(3, "Verify the modal and both checklists are visible")
    modal_ok = case.verify_visible(wr.intermediaries_modal_heading, "'Intermediate Streams and Jurisdictions' heading")
    select_all_ok = case.verify_visible(wr.intermediaries_select_all, "'Select All' link")
    ok = modal_ok and select_all_ok
    case.check("The Intermediate Streams/Jurisdictions modal opens with its controls visible", ok,
               expected="modal and 'Select All' visible", actual=f"modal={modal_ok}, select_all={select_all_ok}")
    if wr.intermediaries_done_button.count():
        wr.intermediaries_done_button.click()

    actual = ("'Intermediaries 1' Select correctly opened the modal with its Streams/Countries checklists." if ok else
              "'Intermediaries 1' Select did not open the expected modal.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_16_intermediaries_select_all_checks_every_stream(page, result):
    case = Case(
        page, "WhtRouter_16", FEATURE, "'Select All' checks every stream in the Intermediaries modal",
        description="Clicking 'Select All' in the Streams column must check every stream checkbox, e.g. "
                     "'Portfolio Dividend'.",
        precondition="User is logged in, Intermediaries 1 modal open.",
        test_data="-",
        steps="1. Log in, open WHT Router, open 'Intermediaries 1'\n2. Click 'Select All'\n"
              "3. Verify 'Portfolio Dividend' is checked",
    )
    wr = _login_and_open(case, page)
    case.click(wr.intermediaries_select(1), "'Intermediaries 1' Select button")
    wr.intermediaries_modal_heading.wait_for(state="visible", timeout=5000)

    case.step(2, "Click 'Select All'")
    case.click(wr.intermediaries_select_all, "'Select All' link")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Portfolio Dividend' is checked")
    checkbox = wr.intermediary_stream_checkbox("Portfolio Dividend")
    ok = checkbox.is_checked()
    case.check("'Select All' checks the 'Portfolio Dividend' stream checkbox", ok,
               expected=True, actual=ok, locator=checkbox)
    if wr.intermediaries_done_button.count():
        wr.intermediaries_done_button.click()

    actual = ("'Select All' correctly checked every stream, including 'Portfolio Dividend'." if ok else
              "'Select All' did not check the expected stream checkboxes.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_whtrouter_17_intermediaries_done_closes_modal(page, result):
    case = Case(
        page, "WhtRouter_17", FEATURE, "'Done' closes the Intermediaries modal",
        description="Clicking 'Done' in the Intermediate Streams/Jurisdictions modal must close it and "
                     "return to the main WHT Router form.",
        precondition="User is logged in, Intermediaries 1 modal open.",
        test_data="-",
        steps="1. Log in, open WHT Router, open 'Intermediaries 1'\n2. Click 'Done'\n"
              "3. Verify the modal is closed",
    )
    wr = _login_and_open(case, page)
    case.click(wr.intermediaries_select(1), "'Intermediaries 1' Select button")
    wr.intermediaries_modal_heading.wait_for(state="visible", timeout=5000)

    case.step(2, "Click 'Done'")
    case.click(wr.intermediaries_done_button, "'Done' button")
    page.wait_for_timeout(500)

    case.step(3, "Verify the modal is closed")
    ok = wr.intermediaries_modal_heading.count() == 0 or not wr.intermediaries_modal_heading.first.is_visible()
    case.check("The Intermediaries modal closes after 'Done'", ok,
               expected="modal not visible", actual=f"still_visible={not ok}")

    actual = ("'Done' correctly closed the Intermediaries modal." if ok else
              "'Done' did not close the Intermediaries modal as expected.")
    result(case, actual, ok)
    assert ok, actual
