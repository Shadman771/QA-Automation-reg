"""TPA > BEPS > BEPS Mapper (/tpa/beps). See pages/tpa/tpa_beps_mapper_page.py
for the full confirmed-live business-purpose and DOM-shape notes - this
page maps BEPS Action/Pillar items to where they are actually covered
across Transfer Pricing Analyzer / World Tax Analyzer for a selected
jurisdiction, and its Pillars/Categories panel is an accordion (expand on
click), not a flat checkbox list like every other TPA/WTA category tree."""
import pytest

from pages.tpa.tpa_beps_mapper_page import TpaBepsMapperPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA BEPS Mapper"

FIXTURE_ACTION = "Action 1: Tax Challenges Arising from Digitalisation"
FIXTURE_LEAF = "Digital economy transactions-General"


def _login_and_open(case, page):
    perform_login(case, page)
    mapper = TpaBepsMapperPage(page)
    case.action("Navigating to /tpa/beps", kind="navigate")
    mapper.goto()
    return mapper


@pytest.mark.smoke
def test_bepsmapper_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "BepsMapper_01", FEATURE, "BEPS Mapper loads with its own 'choose actions' placeholder",
        description="The page must load with the 'Jurisdictions, Pillars and Categories' heading and the "
                     "'Use the left panel to choose actions.' placeholder - page-specific wording, distinct "
                     "from every other WTA/TPA jurisdiction-only page's 'Select Jurisdiction' wording.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open BEPS Mapper\n2. Verify the heading and placeholder are visible",
    )
    mapper = _login_and_open(case, page)
    case.step(2, "Verify the heading and placeholder are visible")
    heading_ok = case.verify_visible(mapper.heading, "'Jurisdictions, Pillars and Categories' heading")
    placeholder_ok = case.verify_visible(mapper.placeholder_text, "'Use the left panel to choose actions.' placeholder")
    ok = heading_ok and placeholder_ok
    case.check("Heading and placeholder are visible before any selection", ok,
               expected="both visible", actual=f"heading={heading_ok}, placeholder={placeholder_ok}")

    actual = ("BEPS Mapper correctly loaded with its own placeholder wording." if ok else
              "BEPS Mapper did not load with the expected heading/placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_bepsmapper_02_selecting_country_shows_removable_chip(page, result):
    case = Case(
        page, "BepsMapper_02", FEATURE, "Selecting a country shows a removable selection chip",
        description="Checking 'Australia' must render a selected-jurisdiction 'pill' (flag + name + a 'Remove' "
                     "button) next to the 'BEPS Mapper' page heading - confirmed live this page renders "
                     "selections as removable chips, not just a checked checkbox.",
        precondition="User is logged in and on BEPS Mapper.",
        test_data="Country: Australia",
        steps="1. Log in and open BEPS Mapper\n2. Check 'Australia'\n3. Verify the removable 'Australia' chip renders",
    )
    mapper = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(mapper.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the removable 'Australia' chip renders")
    ok = case.verify_visible(mapper.selected_country_chip("Australia"), "'Australia' selection chip")
    case.check("A removable 'Australia' chip is shown after selection", ok, expected="visible", actual=ok)

    actual = ("Selecting Australia correctly rendered a removable selection chip." if ok else
              "The removable 'Australia' chip did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_bepsmapper_03_expanding_action_reveals_tpa_and_wta_sections(page, result):
    case = Case(
        page, "BepsMapper_03", FEATURE, "Expanding an Action reveals its Transfer Pricing Analyzer / World Tax Analyzer mapping",
        description=f"With 'Australia' selected, clicking '{FIXTURE_ACTION}' must expand it to reveal a "
                     f"'Transfer Pricing Analyzer' sub-section containing '{FIXTURE_LEAF}' as a checkable leaf "
                     "item - the real business purpose of this page (mapping a BEPS topic to where it's "
                     "covered across the app).",
        precondition="User is logged in, on BEPS Mapper, with 'Australia' selected.",
        test_data=f"Country: Australia, Action: {FIXTURE_ACTION}",
        steps=f"1. Log in, open BEPS Mapper, select Australia\n2. Click '{FIXTURE_ACTION}'\n"
              f"3. Verify '{FIXTURE_LEAF}' becomes visible",
    )
    mapper = _login_and_open(case, page)
    case.click(mapper.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(1500)

    case.step(2, f"Click '{FIXTURE_ACTION}'")
    case.click(mapper.action_label(FIXTURE_ACTION), f"'{FIXTURE_ACTION}' tree node")
    page.wait_for_timeout(1500)

    case.step(3, f"Verify '{FIXTURE_LEAF}' becomes visible")
    ok = mapper.is_leaf_visible(FIXTURE_LEAF)
    case.check(f"'{FIXTURE_LEAF}' is visible after expanding the Action", ok, expected="visible", actual=ok)

    actual = (f"Expanding the Action correctly revealed '{FIXTURE_LEAF}'." if ok else
              f"'{FIXTURE_LEAF}' did not become visible after expanding the Action.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsmapper_04_leaf_checkbox_can_be_toggled(page, result):
    case = Case(
        page, "BepsMapper_04", FEATURE, "A leaf mapping item's checkbox can be checked and unchecked",
        description=f"With the Action expanded, '{FIXTURE_LEAF}' checkbox (the <p> label's preceding-sibling "
                     "<input>, not a <label> wrapper) must toggle to checked, then back to unchecked.",
        precondition="User is logged in, on BEPS Mapper, Australia selected, the Action expanded.",
        test_data=f"Country: Australia, leaf item: {FIXTURE_LEAF}",
        steps=f"1. Log in, open BEPS Mapper, select Australia, expand '{FIXTURE_ACTION}'\n"
              f"2. Click the '{FIXTURE_LEAF}' checkbox\n3. Verify it is checked\n"
              "4. Click it again\n5. Verify it is unchecked",
    )
    mapper = _login_and_open(case, page)
    case.click(mapper.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(1500)
    case.click(mapper.action_label(FIXTURE_ACTION), f"'{FIXTURE_ACTION}' tree node")
    page.wait_for_timeout(1500)

    case.step(2, f"Click the '{FIXTURE_LEAF}' checkbox")
    leaf_cb = mapper.leaf_checkbox(FIXTURE_LEAF)
    case.click(leaf_cb, f"'{FIXTURE_LEAF}' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify it is checked")
    checked_ok = leaf_cb.is_checked()
    case.check(f"'{FIXTURE_LEAF}' checkbox is checked", checked_ok, expected=True, actual=checked_ok)

    case.step(4, "Click it again")
    case.click(leaf_cb, f"'{FIXTURE_LEAF}' checkbox (uncheck)")
    page.wait_for_timeout(500)

    case.step(5, "Verify it is unchecked")
    unchecked_ok = not leaf_cb.is_checked()
    case.check(f"'{FIXTURE_LEAF}' checkbox is unchecked", unchecked_ok, expected=False, actual=leaf_cb.is_checked())

    ok = checked_ok and unchecked_ok
    actual = (f"'{FIXTURE_LEAF}' checkbox correctly toggled checked then unchecked." if ok else
              f"Toggling '{FIXTURE_LEAF}' did not behave as expected (checked={checked_ok}, unchecked={unchecked_ok}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsmapper_05_action_with_no_wta_coverage_shows_not_covered_text(page, result):
    case = Case(
        page, "BepsMapper_05", FEATURE, "An Action with no WTA coverage shows 'Not Covered in World Tax Analyzer (WTA)'",
        description=f"Expanding '{FIXTURE_ACTION}' must reveal a 'World Tax Analyzer' sub-section reading "
                     "'Not Covered in World Tax Analyzer (WTA)' - confirmed live, real documented application "
                     "behavior (the mapping result can legitimately be 'not covered at all' in a given module), "
                     "not missing data to be treated as a defect.",
        precondition="User is logged in, on BEPS Mapper, Australia selected.",
        test_data=f"Country: Australia, Action: {FIXTURE_ACTION}",
        steps=f"1. Log in, open BEPS Mapper, select Australia\n2. Click '{FIXTURE_ACTION}'\n"
              "3. Verify the 'Not Covered in World Tax Analyzer (WTA)' text is visible",
    )
    mapper = _login_and_open(case, page)
    case.click(mapper.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(1500)
    case.step(2, f"Click '{FIXTURE_ACTION}'")
    case.click(mapper.action_label(FIXTURE_ACTION), f"'{FIXTURE_ACTION}' tree node")
    page.wait_for_timeout(1500)

    case.step(3, "Verify the 'Not Covered in World Tax Analyzer (WTA)' text is visible")
    ok = case.verify_visible(mapper.not_covered_in_wta_text(), "'Not Covered in World Tax Analyzer (WTA)' text")
    case.check("'Not Covered in World Tax Analyzer (WTA)' is shown for this Action", ok, expected="visible", actual=ok)

    actual = ("The documented 'Not Covered in World Tax Analyzer (WTA)' text correctly appeared." if ok else
              "The 'Not Covered in World Tax Analyzer (WTA)' text did not appear as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_bepsmapper_06_search_box_filters_country_list(page, result):
    case = Case(
        page, "BepsMapper_06", FEATURE, "The 'Search countries' box filters the country list",
        description="Typing 'Austra' into 'Search countries' must keep 'Australia' visible - same reused "
                     "JurisdictionPanel behavior confirmed live for this page's country list.",
        precondition="User is logged in and on BEPS Mapper.",
        test_data="Search term: Austra",
        steps="1. Log in and open BEPS Mapper\n2. Type 'Austra' into 'Search countries'\n"
              "3. Verify 'Australia' is still visible",
    )
    mapper = _login_and_open(case, page)
    case.step(2, "Type 'Austra' into 'Search countries'")
    case.fill(mapper.jurisdiction.search_countries, "Austra", "'Search countries' input")
    page.wait_for_timeout(600)

    case.step(3, "Verify 'Australia' is still visible")
    ok = case.verify_visible(mapper.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    case.check("'Australia' remains visible after searching 'Austra'", ok, expected="visible", actual=ok)

    actual = ("The search box correctly filtered to show 'Australia'." if ok else
              "'Australia' was not visible after searching 'Austra'.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_bepsmapper_07_direct_deep_link_works(page, result):
    case = Case(
        page, "BepsMapper_07", FEATURE, "A direct deep link to /tpa/beps loads the page",
        description="Navigating straight to /tpa/beps must load with the 'Use the left panel to choose "
                     "actions.' placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/beps\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/beps")
    mapper = TpaBepsMapperPage(page)
    mapper.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(mapper.placeholder_text, "'Use the left panel to choose actions.' placeholder")
    case.check("Direct deep link to /tpa/beps loads with the placeholder", ok, expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/beps correctly loaded." if ok else
              "The direct deep link to /tpa/beps did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
