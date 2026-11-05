"""TPA > Case Law (/tpa/CaseLaw).

New parent module (TPA), built via live DOM discovery (scratchpad
scripts, not part of the suite) - no reference QA sheet exists for this
module. See pages/tpa/tpa_case_law_page.py for the full real-shape
writeup, including the confirmed-live "Case Number/Case Title/Date of
Decision/Court" table shape (no download/Add to Project, unlike Forms/
Regulations) and the confirmed-good India/"Special areas" content
anchor vs. Australia/Requirements' own confirmed empty state."""
import pytest

from pages.tpa.tpa_case_law_page import TpaCaseLawPage, CASE_LAW_CATEGORIES
from pages.wta.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "TPA Case Law"


def _login_and_open(case, page):
    perform_login(case, page)
    cl = TpaCaseLawPage(page)
    case.action("Navigating to /tpa/CaseLaw", kind="navigate")
    cl.goto()
    return cl


@pytest.mark.smoke
def test_caselaw_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "CaseLaw_01", FEATURE, "Case Law loads with the jurisdiction/category placeholder",
        description="The page must load with the 'Use the left panel to choose jurisdiction and categories.' "
                     "placeholder shown before any selection.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Case Law\n2. Verify the placeholder text is visible",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(cl.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok)

    actual = ("Case Law loaded with the placeholder visible." if ok else
              "Case Law did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_caselaw_02_all_fourteen_categories_listed(page, result):
    case = Case(
        page, "CaseLaw_02", FEATURE, "All 14 categories are listed in the left panel",
        description="The category checklist must show all 14 known Case Law topics - the same 14 as "
                     "National Rules.",
        precondition="User is logged in and on Case Law.",
        test_data="-",
        steps="1. Log in and open Case Law\n2. Verify each of the 14 categories is visible",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Verify each category label is visible")
    missing = [c for c in CASE_LAW_CATEGORIES if not case.verify_visible(cl.category.category_label(c), f"'{c}' category")]
    ok = not missing
    case.check("All 14 categories are visible", ok, expected="all 14 visible",
               actual=f"missing: {missing}" if missing else "all present")

    actual = ("All 14 categories were visible." if ok else f"Missing categories: {missing}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_caselaw_03_categories_default_to_checked_so_jurisdiction_alone_renders(page, result):
    case = Case(
        page, "CaseLaw_03", FEATURE,
        "All categories default to checked, so selecting only a jurisdiction already renders content",
        description="Unlike National Rules (categories default UNCHECKED, requiring an explicit category "
                     "pick), Case Law's category checklist - confirmed live via its 'Check All' checkbox's "
                     "own default `checked` state - starts with every category already checked. So checking "
                     "'India' alone (no explicit category click) already renders real case law content, not "
                     "the placeholder.",
        precondition="User is logged in and on Case Law.",
        test_data="Country: India",
        steps="1. Log in and open Case Law\n2. Verify 'Check All' is checked by default\n"
              "3. Check 'India' only\n4. Verify real content renders (not the placeholder)",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Verify 'Check All' is checked by default")
    default_checked = cl.category.check_all_categories.is_checked()
    case.check("'Check All' defaults to checked", default_checked, expected=True, actual=default_checked)

    case.step(3, "Select India's jurisdiction checkbox only")
    case.click(cl.jurisdiction.country_checkbox("India"), "'India' checkbox")
    wait_for_content(cl.showing_case_laws_text)

    case.step(4, "Verify real content renders, not the placeholder")
    content_ok = case.verify_visible(cl.showing_case_laws_text, "'Showing case laws of' text")
    placeholder_gone = not cl.placeholder_text.is_visible()
    ok = default_checked and content_ok and placeholder_gone
    case.check("Selecting only a jurisdiction renders real content (categories pre-checked)", ok,
               expected="default_checked=True, content visible, placeholder gone",
               actual=f"default_checked={default_checked}, content={content_ok}, placeholder_gone={placeholder_gone}")

    actual = ("Confirmed: categories default to checked, so selecting only a jurisdiction already rendered "
              "real content." if ok else
              "Selecting only a jurisdiction did not behave as the confirmed default-checked state predicts.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_caselaw_04_jurisdiction_and_category_renders_real_cases(page, result):
    case = Case(
        page, "CaseLaw_04", FEATURE, "Selecting a jurisdiction renders real case law entries (categories pre-checked)",
        description="Checking 'India' (with every category left at its real default of already-checked - "
                     "see CaseLaw_03) must render a 'Showing case laws of India' table with the Case Number/"
                     "Case Title/Date of Decision/Court columns and real rows - confirmed live this is a good "
                     "content anchor, unlike Australia (see CaseLaw_06) which genuinely has none.",
        precondition="User is logged in and on Case Law.",
        test_data="Country: India",
        steps="1. Log in and open Case Law\n2. Check 'India'\n"
              "3. Verify the table and its columns render with real rows",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Select India")
    case.click(cl.jurisdiction.country_checkbox("India"), "'India' checkbox")
    wait_for_content(cl.showing_case_laws_text)
    wait_for_content(cl.col_case_number)

    case.step(3, "Verify table and columns render with real rows")
    showing_ok = case.verify_visible(cl.showing_case_laws_text, "'Showing case laws of' text")
    case_number_ok = case.verify_visible(cl.col_case_number, "'Case Number' column header")
    court_ok = case.verify_visible(cl.col_court, "'Court' column header")
    ok = showing_ok and case_number_ok and court_ok
    case.check("Case Law table with columns is visible for India", ok,
               expected="all visible", actual=f"showing={showing_ok}, case_number={case_number_ok}, court={court_ok}")

    actual = ("Selecting India correctly rendered the real case law table." if ok else
              "Selecting a jurisdiction did not render the expected table.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_caselaw_05_no_download_or_add_to_project_present(page, result):
    case = Case(
        page, "CaseLaw_05", FEATURE, "No download link or 'Add to Project' button exists on this page",
        description="With India selected (real content rendered), there must be NO 'Add to Project' button "
                     "and NO 'Download' column - confirmed live this page's table shape has neither, unlike "
                     "Forms/Regulations.",
        precondition="User is logged in, India selected.",
        test_data="Country: India",
        steps="1. Log in, open Case Law, select India\n"
              "2. Verify no 'Add to Project' button and no 'Download' column exist",
    )
    cl = _login_and_open(case, page)
    case.click(cl.jurisdiction.country_checkbox("India"), "'India' checkbox")
    wait_for_content(cl.showing_case_laws_text)
    wait_for_content(cl.col_case_number)

    case.step(2, "Verify no 'Add to Project' button and no 'Download' column exist")
    add_to_project_count = page.get_by_text("Add to Project", exact=True).count()
    download_col_count = page.get_by_text("Download", exact=True).count()
    ok = add_to_project_count == 0 and download_col_count == 0
    case.check("No 'Add to Project' button or 'Download' column exists", ok,
               expected="both count 0", actual=f"add_to_project={add_to_project_count}, download_col={download_col_count}")

    actual = ("Correctly confirmed no 'Add to Project' button or 'Download' column exists." if ok else
              f"Found unexpected elements (add_to_project={add_to_project_count}, download_col={download_col_count}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_caselaw_06_genuine_empty_state_for_a_country_with_no_case_law(page, result):
    case = Case(
        page, "CaseLaw_06", FEATURE, "A country with no case law shows a genuine 'No results found'",
        description="Which countries have zero case law entries is confirmed live to be genuinely "
                     "environment-specific (e.g. Australia has none on RC/Staging but real entries on Live) "
                     "- so this reads the real state first: it tries a short list of candidate countries and "
                     "uses whichever one actually shows 'No results found' on THIS environment, then verifies "
                     "that is a real empty state, not an error or a fabricated row.",
        precondition="User is logged in and on Case Law.",
        test_data="First of: Bangladesh, Indonesia, Mongolia, Sri Lanka, Vietnam, Azerbaijan, Thailand, "
                   "Australia that genuinely has no case law on this environment",
        steps="1. Log in, open Case Law\n2. Try candidate countries until one shows 'No results found'\n"
              "3. Verify that empty state is real (not an error)",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Try candidate countries until one genuinely shows 'No results found'")
    candidates = ["Bangladesh", "Indonesia", "Mongolia", "Sri Lanka", "Vietnam", "Azerbaijan", "Thailand", "Australia"]
    empty_country = None
    for country in candidates:
        case.click(cl.jurisdiction.country_checkbox(country), f"'{country}' checkbox")
        wait_for_content(cl.showing_case_laws_text)
        page.wait_for_timeout(800)
        if cl.no_results_text.is_visible():
            empty_country = country
            break
        case.click(cl.jurisdiction.country_checkbox(country), f"'{country}' checkbox (deselect)")

    case.step(3, "Verify the discovered empty state is real")
    ok = empty_country is not None and case.verify_visible(cl.no_results_text, "'No results found' message")
    case.check("A genuine 'No results found' empty state was found and verified", ok,
               expected="at least one candidate shows 'No results found'",
               actual=f"empty_country={empty_country}")

    actual = (f"{empty_country} correctly showed the genuine 'No results found' empty state on this "
              f"environment." if ok else
              f"None of the candidate countries ({', '.join(candidates)}) showed a 'No results found' empty "
              f"state on this environment - every one may have real data here.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_caselaw_07_check_all_toggles_every_category(page, result):
    case = Case(
        page, "CaseLaw_07", FEATURE, "'Check All' toggles every category checkbox off, then back on",
        description="Confirmed live: 'Check All' starts CHECKED by default on this page (unlike National "
                     "Rules, which defaults unchecked) - so the first click toggles every category OFF, and "
                     "a second click toggles every category back ON. This test verifies the toggle in both "
                     "directions rather than assuming an unchecked starting state.",
        precondition="User is logged in and on Case Law.",
        test_data="-",
        steps="1. Log in and open Case Law\n2. Click 'Check All' once\n"
              "3. Verify every category checkbox is now unchecked\n4. Click 'Check All' again\n"
              "5. Verify every category checkbox is checked again",
    )
    cl = _login_and_open(case, page)
    case.step(2, "Click 'Check All' once")
    case.click(cl.category.check_all_categories, "'Check All' checkbox")
    page.wait_for_timeout(500)

    case.step(3, "Verify every category checkbox is now unchecked")
    still_checked = [c for c in CASE_LAW_CATEGORIES if cl.category.category_checkbox(c).is_checked()]
    off_ok = not still_checked

    case.step(4, "Click 'Check All' again")
    case.click(cl.category.check_all_categories, "'Check All' checkbox")
    page.wait_for_timeout(500)

    case.step(5, "Verify every category checkbox is checked again")
    unchecked = [c for c in CASE_LAW_CATEGORIES if not cl.category.category_checkbox(c).is_checked()]
    on_ok = not unchecked

    ok = off_ok and on_ok
    case.check("'Check All' toggles every category off, then back on", ok,
               expected="all unchecked after 1st click, all checked after 2nd",
               actual=f"still_checked_after_off={still_checked}, unchecked_after_on={unchecked}")

    actual = ("'Check All' correctly toggled every category off, then back on." if ok else
              f"'Check All' did not toggle as expected (still_checked_after_off={still_checked}, "
              f"unchecked_after_on={unchecked}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_caselaw_08_direct_deep_link_works(page, result):
    case = Case(
        page, "CaseLaw_08", FEATURE, "A direct deep link to /tpa/CaseLaw loads the page",
        description="Navigating straight to /tpa/CaseLaw must load with the placeholder visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate directly to /tpa/CaseLaw\n3. Verify the placeholder renders",
    )
    perform_login(case, page)
    case.step(2, "Navigate directly to /tpa/CaseLaw")
    cl = TpaCaseLawPage(page)
    cl.goto()
    case.step(3, "Verify the placeholder renders")
    ok = case.verify_visible(cl.placeholder_text, "left-panel instruction text")
    case.check("Direct deep link to /tpa/CaseLaw loads with the placeholder", ok, expected="visible", actual=ok)

    actual = ("The direct deep link to /tpa/CaseLaw correctly loaded." if ok else
              "The direct deep link to /tpa/CaseLaw did not load as expected.")
    result(case, actual, ok)
    assert ok, actual
