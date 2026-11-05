"""TPA > Information > National Rules (/tpa/NationalRules).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. Reuses pages/wta/wta_common.py's JurisdictionPanel/CategoryTree
unmodified (confirmed live: identical DOM shape to WTA's own
Information/Pillar2 Information pages). See
TPA/TPA_BUSINESS_EXPLORATION.md for the full business inventory."""
import pytest

from pages.tpa.tpa_national_rules_page import TpaNationalRulesPage, NATIONAL_RULES_CATEGORIES
from pages.wta.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA National Rules"


def _login_and_open(case, page):
    perform_login(case, page)
    nr = TpaNationalRulesPage(page)
    case.action("Navigating to /tpa/NationalRules", kind="navigate")
    nr.goto()
    return nr


@pytest.mark.smoke
def test_nationalrules_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "NationalRules_01", FEATURE, "National Rules loads with the jurisdiction/category placeholder",
        description="The page must load with the 'Use the left panel to choose jurisdictions and categories.' "
                     "placeholder shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open National Rules\n2. Verify the placeholder text is visible",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(nr.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("National Rules loaded with the jurisdiction/category placeholder visible." if ok else
              "National Rules did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_nationalrules_02_all_fourteen_categories_listed(page, result):
    case = Case(
        page, "NationalRules_02", FEATURE, "All 14 categories are listed in the left panel",
        description="The category checklist must show all 14 known National Rules topics.",
        precondition="User is logged in and on National Rules.",
        test_data="-",
        steps="1. Log in and open National Rules\n2. Verify each of the 14 categories is visible",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Verify each category label is visible")
    missing = [c for c in NATIONAL_RULES_CATEGORIES if not case.verify_visible(nr.category.category_label(c), f"'{c}' category")]
    ok = not missing
    case.check("All 14 categories are visible", ok, expected="all 14 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 14 categories were visible in the left panel." if ok else
              f"Missing categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_03_jurisdiction_only_keeps_placeholder(page, result):
    case = Case(
        page, "NationalRules_03", FEATURE, "Selecting only a jurisdiction keeps the placeholder",
        description="Checking a country without also checking a category must NOT render content.",
        precondition="User is logged in and on National Rules.",
        test_data="Country: Australia",
        steps="1. Log in and open National Rules\n2. Check 'Australia' only\n"
              "3. Verify the placeholder is still shown",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Select Australia's jurisdiction checkbox only")
    case.click(nr.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(800)

    case.step(3, "Verify the placeholder is still visible")
    ok = case.verify_visible(nr.placeholder_text, "left-panel instruction text")
    case.check("Placeholder is still visible with only a jurisdiction selected", ok, expected="visible", actual=ok)

    actual = ("Selecting only a jurisdiction correctly kept the placeholder visible." if ok else
              "The placeholder disappeared after selecting only a jurisdiction.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_nationalrules_04_jurisdiction_and_category_renders_real_content(page, result):
    case = Case(
        page, "NationalRules_04", FEATURE, "Selecting a jurisdiction and a category renders real content",
        description="Checking 'Australia' AND the 'Requirements' category must render real sub-topic content "
                     "('Scope of transfer pricing rules'), not the placeholder.",
        precondition="User is logged in and on National Rules.",
        test_data="Country: Australia / Category: Requirements",
        steps="1. Log in and open National Rules\n2. Check 'Australia'\n3. Check 'Requirements'\n"
              "4. Verify the 'Scope of transfer pricing rules' sub-topic renders",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(nr.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)
    case.step(3, "Select the 'Requirements' category")
    case.click(nr.category.category_checkbox("Requirements"), "'Requirements' category checkbox")
    wait_for_content(nr.sub_topic_heading("Scope of transfer pricing rules"))

    case.step(4, "Verify the sub-topic content renders")
    ok = case.verify_visible(nr.sub_topic_heading("Scope of transfer pricing rules"), "'Scope of transfer pricing rules' sub-topic")
    case.check("Real sub-topic content renders for Australia/Requirements", ok, expected="visible", actual=ok)

    actual = ("Selecting Australia + Requirements correctly rendered real sub-topic content." if ok else
              "Selecting a jurisdiction and category did not render the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_05_export_control_present(page, result):
    case = Case(
        page, "NationalRules_05", FEATURE, "The 'Export:' control is present once content renders",
        description="With Australia/Requirements selected, the 'Export:' control must be visible with its "
                     "icon-only download buttons.",
        precondition="User is logged in, Australia/Requirements selected.",
        test_data="Country: Australia / Category: Requirements",
        steps="1. Log in, open National Rules, select Australia/Requirements\n"
              "2. Verify the 'Export:' control is visible",
    )
    nr = _login_and_open(case, page)
    case.click(nr.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)
    case.click(nr.category.category_checkbox("Requirements"), "'Requirements' category checkbox")
    wait_for_content(nr.sub_topic_heading("Scope of transfer pricing rules"))

    case.step(2, "Verify the 'Export:' control is visible")
    ok = case.verify_visible(nr.export_label, "'Export:' control")
    case.check("'Export:' control is visible once content renders", ok, expected="visible", actual=ok)

    actual = ("The 'Export:' control is correctly visible once content renders." if ok else
              "The 'Export:' control was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_06_compare_with_other_years_button_present(page, result):
    case = Case(
        page, "NationalRules_06", FEATURE, "The 'Compare with other years' button is present once content renders",
        description="With Australia/Requirements selected, the 'Compare with other years' button must be visible.",
        precondition="User is logged in, Australia/Requirements selected.",
        test_data="Country: Australia / Category: Requirements",
        steps="1. Log in, open National Rules, select Australia/Requirements\n"
              "2. Verify the 'Compare with other years' button is visible",
    )
    nr = _login_and_open(case, page)
    case.click(nr.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)
    case.click(nr.category.category_checkbox("Requirements"), "'Requirements' category checkbox")
    wait_for_content(nr.sub_topic_heading("Scope of transfer pricing rules"))

    case.step(2, "Verify the 'Compare with other years' button is visible")
    ok = case.verify_visible(nr.compare_years_button, "'Compare with other years' button")
    case.check("'Compare with other years' button is visible once content renders", ok, expected="visible", actual=ok)

    actual = ("The 'Compare with other years' button is correctly visible." if ok else
              "The 'Compare with other years' button was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_07_each_subtopic_has_a_commentary_button(page, result):
    case = Case(
        page, "NationalRules_07", FEATURE, "Each rendered sub-topic has its own 'Commentary' button",
        description="With Australia/Requirements selected (3 known real sub-topics: 'Scope of transfer pricing "
                     "rules', 'OECD Guidelines', 'Related party definition'), there must be at least 3 "
                     "'Commentary' buttons - one per sub-topic, not a single page-level button.",
        precondition="User is logged in, Australia/Requirements selected.",
        test_data="Country: Australia / Category: Requirements",
        steps="1. Log in, open National Rules, select Australia/Requirements\n"
              "2. Verify at least 3 'Commentary' buttons are present",
    )
    nr = _login_and_open(case, page)
    case.click(nr.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(400)
    case.click(nr.category.category_checkbox("Requirements"), "'Requirements' category checkbox")
    wait_for_content(nr.sub_topic_heading("Scope of transfer pricing rules"))
    # The sub-topic headings render slightly before their own "Commentary"
    # buttons finish mounting (confirmed live: a race, not a missing
    # feature) - wait for the button itself too, not just the heading.
    wait_for_content(nr.commentary_buttons)

    case.step(2, "Verify at least 3 'Commentary' buttons are present")
    count = nr.commentary_buttons.count()
    ok = count >= 3
    case.check("At least 3 'Commentary' buttons are present", ok, expected=">= 3", actual=f"count={count}")

    actual = (f"National Rules correctly shows {count} 'Commentary' button(s) for Australia/Requirements." if ok else
              f"Expected at least 3 'Commentary' buttons, found {count}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_08_check_all_selects_every_category(page, result):
    case = Case(
        page, "NationalRules_08", FEATURE, "'Check All' selects every category checkbox",
        description="Clicking 'Check All' must check every one of the 14 category checkboxes.",
        precondition="User is logged in and on National Rules.",
        test_data="-",
        steps="1. Log in and open National Rules\n2. Click 'Check All'\n"
              "3. Verify every category checkbox is checked",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Click 'Check All'")
    case.click(nr.category.check_all_categories, "'Check All' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify every category checkbox is checked")
    unchecked = [c for c in NATIONAL_RULES_CATEGORIES
                 if not nr.category.category_checkbox(c).is_checked()]
    ok = not unchecked
    case.check("Every category checkbox is checked after 'Check All'", ok,
               expected="all 14 checked", actual=f"unchecked: {unchecked}" if unchecked else "all checked")

    actual = ("'Check All' correctly checked every category." if ok else
              f"'Check All' left these unchecked: {unchecked}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_09_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "NationalRules_09", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Switching from 'Asia Pacific' (default) to 'Europe' must hide 'Australia' (an Asia "
                     "Pacific country) from the visible list.",
        precondition="User is logged in and on National Rules.",
        test_data="-",
        steps="1. Log in and open National Rules\n2. Click the 'Europe' region tab\n"
              "3. Verify 'Australia' is no longer visible",
    )
    nr = _login_and_open(case, page)
    case.step(2, "Click the 'Europe' region tab")
    case.click(nr.jurisdiction.region_tab("Europe"), "'Europe' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify 'Australia' is no longer visible")
    ok = not nr.jurisdiction.country_checkbox("Australia").is_visible()
    case.check("'Australia' is hidden after switching to 'Europe'", ok, expected="not visible", actual=f"visible={not ok}")

    actual = ("Switching to 'Europe' correctly hid 'Australia'." if ok else
              "'Australia' was still visible after switching to 'Europe'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_nationalrules_10_direct_deep_link_works(page, result):
    case = Case(
        page, "NationalRules_10", FEATURE, "A direct deep link to /tpa/NationalRules loads the page",
        description="Navigating straight to /tpa/NationalRules must load with the placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/NationalRules\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/NationalRules")
    nr = TpaNationalRulesPage(page)
    nr.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(nr.placeholder_text, "left-panel instruction text")
    case.check("Direct deep link to /tpa/NationalRules loads with the placeholder", ok, expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/NationalRules correctly loaded." if ok else
              "The direct deep link to /tpa/NationalRules did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
