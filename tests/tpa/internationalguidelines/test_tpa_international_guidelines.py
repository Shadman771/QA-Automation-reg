"""TPA > Information > International Guidelines (/tpa/InternationalGuideline).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. See TPA/TPA_BUSINESS_EXPLORATION.md and
pages/tpa/tpa_international_guidelines_page.py for the full real-shape
writeup (the "Guideline" EU/OECD/UN selector reuses CategoryTree's own
DOM shape, not JurisdictionPanel's)."""
import pytest

from pages.tpa.tpa_international_guidelines_page import (
    TpaInternationalGuidelinesPage, GUIDELINE_BODIES, INTERNATIONAL_GUIDELINES_CATEGORIES,
)
from pages.wta.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA International Guidelines"


def _login_and_open(case, page):
    perform_login(case, page)
    ig = TpaInternationalGuidelinesPage(page)
    case.action("Navigating to /tpa/InternationalGuideline", kind="navigate")
    ig.goto()
    return ig


@pytest.mark.smoke
def test_internationalguidelines_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "InternationalGuidelines_01", FEATURE,
        "International Guidelines loads with the guideline/category placeholder",
        description="The page must load with the 'Use the left panel to choose guideline and categories.' "
                     "placeholder shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open International Guidelines\n2. Verify the placeholder text is visible",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(ig.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("International Guidelines loaded with the placeholder visible." if ok else
              "International Guidelines did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_internationalguidelines_02_all_three_guideline_bodies_listed(page, result):
    case = Case(
        page, "InternationalGuidelines_02", FEATURE, "All 3 guideline bodies (EU/OECD/UN) are listed",
        description="The 'Guideline' selector must list EU, OECD and UN.",
        precondition="User is logged in and on International Guidelines.",
        test_data="-",
        steps="1. Log in and open International Guidelines\n2. Verify EU, OECD and UN are each visible",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Verify each guideline body is visible")
    missing = [g for g in GUIDELINE_BODIES if not case.verify_visible(ig.guideline.category_label(g), f"'{g}' guideline body")]
    ok = not missing
    case.check("All 3 guideline bodies are visible", ok, expected="all 3 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 3 guideline bodies were visible." if ok else f"Missing guideline bodies: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_internationalguidelines_03_all_seventeen_categories_listed(page, result):
    case = Case(
        page, "InternationalGuidelines_03", FEATURE, "All 17 top-level categories are listed",
        description="The category checklist must show all 17 known International Guidelines topics.",
        precondition="User is logged in and on International Guidelines.",
        test_data="-",
        steps="1. Log in and open International Guidelines\n2. Verify each of the 17 categories is visible",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Verify each category label is visible")
    # Confirmed live: "Information exchange" has 2 DOM matches here (one
    # hidden, one visible) - the same "mounted but hidden" duplicate
    # pattern documented elsewhere in this project (e.g. rsuite dropdown
    # items, pages/regbriefings/preferences_page.py::country_checkbox()).
    # ".first" is NOT reliably the visible one (confirmed live: index 0 is
    # the hidden match here) - scan for whichever match is actually
    # visible instead of assuming DOM order.
    def _visible_category_label(name):
        candidates = ig.category.category_label(name)
        for i in range(candidates.count()):
            if candidates.nth(i).is_visible():
                return candidates.nth(i)
        return candidates.first

    missing = [c for c in INTERNATIONAL_GUIDELINES_CATEGORIES
               if not case.verify_visible(_visible_category_label(c), f"'{c}' category")]
    ok = not missing
    case.check("All 17 categories are visible", ok, expected="all 17 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 17 categories were visible." if ok else f"Missing categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_internationalguidelines_04_guideline_only_keeps_placeholder(page, result):
    case = Case(
        page, "InternationalGuidelines_04", FEATURE, "Selecting only a guideline body keeps the placeholder",
        description="Checking 'OECD' without also checking a category must NOT render content.",
        precondition="User is logged in and on International Guidelines.",
        test_data="Guideline: OECD",
        steps="1. Log in and open International Guidelines\n2. Check 'OECD' only\n"
              "3. Verify the placeholder is still shown",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Select 'OECD' only")
    case.click(ig.guideline.category_checkbox("OECD"), "'OECD' checkbox")
    page.wait_for_timeout(800)

    case.step(3, "Verify the placeholder is still visible")
    ok = case.verify_visible(ig.placeholder_text, "left-panel instruction text")
    case.check("Placeholder is still visible with only a guideline body selected", ok, expected="visible", actual=ok)

    actual = ("Selecting only a guideline body correctly kept the placeholder visible." if ok else
              "The placeholder disappeared after selecting only a guideline body.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_internationalguidelines_05_guideline_and_category_renders_real_content(page, result):
    case = Case(
        page, "InternationalGuidelines_05", FEATURE,
        "Selecting a guideline body and a category renders real content",
        description="Checking 'OECD' AND the 'Basic rule' category must expand into real nested sub-topics "
                     "('Global business and the arm's length principle'), not the placeholder.",
        precondition="User is logged in and on International Guidelines.",
        test_data="Guideline: OECD / Category: Basic rule",
        steps="1. Log in and open International Guidelines\n2. Check 'OECD'\n3. Check 'Basic rule'\n"
              "4. Verify the nested sub-topic renders",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Select 'OECD'")
    case.click(ig.guideline.category_checkbox("OECD"), "'OECD' checkbox")
    page.wait_for_timeout(400)
    case.step(3, "Select the 'Basic rule' category")
    case.click(ig.category.category_checkbox("Basic rule"), "'Basic rule' category checkbox")
    wait_for_content(ig.sub_topic_heading("Global business and the arm’s length principle"))

    case.step(4, "Verify the nested sub-topic content renders")
    ok = case.verify_visible(ig.sub_topic_heading("Global business and the arm’s length principle"),
                              "'Global business and the arm’s length principle' sub-topic")
    case.check("Real nested sub-topic content renders for OECD/Basic rule", ok, expected="visible", actual=ok)

    actual = ("Selecting OECD + Basic rule correctly rendered real nested sub-topic content." if ok else
              "Selecting a guideline body and category did not render the expected content.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_internationalguidelines_06_export_control_present(page, result):
    case = Case(
        page, "InternationalGuidelines_06", FEATURE, "The 'Export:' control is present once content renders",
        description="With OECD/Basic rule selected, the 'Export:' control must be visible.",
        precondition="User is logged in, OECD/Basic rule selected.",
        test_data="Guideline: OECD / Category: Basic rule",
        steps="1. Log in, open International Guidelines, select OECD/Basic rule\n"
              "2. Verify the 'Export:' control is visible",
    )
    ig = _login_and_open(case, page)
    case.click(ig.guideline.category_checkbox("OECD"), "'OECD' checkbox")
    page.wait_for_timeout(400)
    case.click(ig.category.category_checkbox("Basic rule"), "'Basic rule' category checkbox")
    wait_for_content(ig.sub_topic_heading("Global business and the arm’s length principle"))

    case.step(2, "Verify the 'Export:' control is visible")
    ok = case.verify_visible(ig.export_label, "'Export:' control")
    case.check("'Export:' control is visible once content renders", ok, expected="visible", actual=ok)

    actual = ("The 'Export:' control is correctly visible." if ok else "The 'Export:' control was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_internationalguidelines_07_compare_button_present(page, result):
    case = Case(
        page, "InternationalGuidelines_07", FEATURE,
        "The 'Compare jurisdiction(s) against Guideline(s)' button is present once content renders",
        description="With OECD/Basic rule selected, the 'Compare jurisdiction(s) against Guideline(s)' button "
                     "must be visible - a different label from National Rules' own 'Compare with other years'.",
        precondition="User is logged in, OECD/Basic rule selected.",
        test_data="Guideline: OECD / Category: Basic rule",
        steps="1. Log in, open International Guidelines, select OECD/Basic rule\n"
              "2. Verify the compare button is visible",
    )
    ig = _login_and_open(case, page)
    case.click(ig.guideline.category_checkbox("OECD"), "'OECD' checkbox")
    page.wait_for_timeout(400)
    case.click(ig.category.category_checkbox("Basic rule"), "'Basic rule' category checkbox")
    wait_for_content(ig.sub_topic_heading("Global business and the arm’s length principle"))

    case.step(2, "Verify the compare button is visible")
    ok = case.verify_visible(ig.compare_button, "'Compare jurisdiction(s) against Guideline(s)' button")
    case.check("Compare button is visible once content renders", ok, expected="visible", actual=ok)

    actual = ("The compare button is correctly visible." if ok else "The compare button was not found.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_internationalguidelines_08_check_all_selects_every_guideline_body(page, result):
    case = Case(
        page, "InternationalGuidelines_08", FEATURE, "'Check All' selects every guideline body",
        description="Clicking the Guideline panel's 'Check All' must check EU, OECD and UN all at once.",
        precondition="User is logged in and on International Guidelines.",
        test_data="-",
        steps="1. Log in and open International Guidelines\n2. Click the Guideline panel's 'Check All'\n"
              "3. Verify EU, OECD and UN are all checked",
    )
    ig = _login_and_open(case, page)
    case.step(2, "Click the Guideline panel's 'Check All'")
    case.click(ig.guideline.check_all_categories, "Guideline 'Check All' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify every guideline body is checked")
    unchecked = [g for g in GUIDELINE_BODIES if not ig.guideline.category_checkbox(g).is_checked()]
    ok = not unchecked
    case.check("Every guideline body is checked after 'Check All'", ok,
               expected="all 3 checked", actual=f"unchecked: {unchecked}" if unchecked else "all checked")

    actual = ("'Check All' correctly checked every guideline body." if ok else
              f"'Check All' left these unchecked: {unchecked}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_internationalguidelines_09_direct_deep_link_works(page, result):
    case = Case(
        page, "InternationalGuidelines_09", FEATURE,
        "A direct deep link to /tpa/InternationalGuideline loads the page",
        description="Navigating straight to /tpa/InternationalGuideline must load with the placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/InternationalGuideline\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/InternationalGuideline")
    ig = TpaInternationalGuidelinesPage(page)
    ig.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(ig.placeholder_text, "left-panel instruction text")
    case.check("Direct deep link to /tpa/InternationalGuideline loads with the placeholder", ok,
               expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/InternationalGuideline correctly loaded." if ok else
              "The direct deep link to /tpa/InternationalGuideline did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
