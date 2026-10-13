"""World Tax Analyzer > Information workspace (/wta/Information).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: region tabs (Asia Pacific/Americas/Europe/MEA), a
    "Search countries" box, a per-country checklist, a "Check All"
    checkbox, a "Search categories" box, a "Depth-" 1/2/3/4 control, and an
    expandable category tree (e.g. "Liability to Tax" -> "Residence" ->
    "Treaty rules for residence" -> ...).
  - The right panel shows "Select Jurisdictions and Categories" until BOTH
    a jurisdiction and a category are selected - selecting a jurisdiction
    alone is confirmed NOT enough to clear the placeholder.
  - Checking a parent category (e.g. "Liability to Tax") expands it in
    place to show its children, rather than immediately rendering content.
  - The country search box shows 'No countries found matching "..."' for a
    non-existent country.

Every click/fill/check below goes through `case.*` (red-highlight + the
per-step evidence screenshot gallery)."""
import pytest

from pages.information_page import InformationPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Information"


def _login(case, page):
    perform_login(case, page)


@pytest.mark.smoke
def test_information_01_page_loads(page, result):
    case = Case(
        page, "Information_01", FEATURE, "Information workspace loads with the Jurisdictions and Categories panel",
        description="The /wta/Information page must show the left jurisdiction/category panel and the "
                     "'Select Jurisdictions and Categories' placeholder in the content area.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in\n2. Navigate to Information (already the post-login landing page)\n"
              "3. Verify the panel heading and placeholder text are visible",
    )
    _login(case, page)
    info = InformationPage(page)
    case.step(2, "Verify the Information workspace is loaded")
    heading_ok = case.verify_visible(info.heading, "'Select Jurisdictions and Categories' heading")
    placeholder_ok = case.verify_visible(info.placeholder_text, "left-panel instruction text")
    ok = info.is_loaded() and heading_ok and placeholder_ok
    case.check("Information workspace shows its panel heading and placeholder", ok,
               expected="heading + placeholder visible on /wta/Information", actual=ok,
               locator=info.heading)

    actual = ("The Information workspace loaded on /wta/Information with the 'Select Jurisdictions and "
              "Categories' heading and instruction text visible." if ok else
              f"The Information workspace did not load as expected. URL: {page.url}")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_information_02_region_tabs_switch_country_list(page, result):
    case = Case(
        page, "Information_02", FEATURE, "Switching region tabs changes the visible country list",
        description="Clicking the 'Americas' region tab must show Americas countries and hide "
                     "Asia Pacific-only countries (e.g. 'Australia').",
        precondition="User is logged in and on the Information workspace, 'Asia Pacific' selected by default.",
        test_data="-",
        steps="1. Log in\n2. Verify 'Australia' (Asia Pacific) is visible\n3. Click the 'Americas' tab\n"
              "4. Verify 'Australia' is no longer visible in the list",
    )
    _login(case, page)
    info = InformationPage(page)
    case.step(2, "Verify an Asia Pacific country is visible by default")
    australia_before = case.verify_visible(info.jurisdiction.country_row_visible("Australia"), "'Australia' row")

    case.step(3, "Switch to the 'Americas' region tab")
    case.click(info.jurisdiction.region_tab("Americas"), "'Americas' region tab")
    page.wait_for_timeout(500)

    case.step(4, "Verify Australia is no longer listed")
    australia_after = info.jurisdiction.country_row_visible("Australia").is_visible()
    ok = australia_before and not australia_after
    case.check("'Australia' is visible under Asia Pacific and hidden after switching to Americas", ok,
               expected="visible then hidden", actual=f"before={australia_before}, after={australia_after}")

    actual = ("Switching from 'Asia Pacific' to 'Americas' changed the rendered country list (Australia "
              "disappeared)." if ok else
              f"Switching region tabs did not change the country list as expected "
              f"(Australia visible before={australia_before}, after={australia_after}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_information_03_country_search_filters_list(page, result):
    case = Case(
        page, "Information_03", FEATURE, "Country search filters the jurisdiction list",
        description="Typing a country name into 'Search countries' must narrow the list to matches; a "
                     "non-existent name must show a 'No countries found' message.",
        precondition="User is logged in and on the Information workspace.",
        test_data="Match: 'Japan' / No match: 'zzzznotarealcountry'",
        steps="1. Log in\n2. Search for 'Japan', verify it is shown and 'Australia' is filtered out\n"
              "3. Search for a bogus name, verify the 'No countries found' message appears",
    )
    _login(case, page)
    info = InformationPage(page)

    case.step(2, "Search for an existing country ('Japan')")
    case.fill(info.jurisdiction.search_countries, "Japan", "Search countries box")
    page.wait_for_timeout(500)
    japan_visible = info.jurisdiction.country_row_visible("Japan").is_visible()
    australia_hidden = not info.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("Searching 'Japan' shows Japan and filters out Australia", japan_visible and australia_hidden,
               expected="Japan visible, Australia hidden",
               actual=f"japan_visible={japan_visible}, australia_hidden={australia_hidden}")

    case.step(3, "Search for a country that does not exist")
    case.fill(info.jurisdiction.search_countries, "zzzznotarealcountry", "Search countries box")
    page.wait_for_timeout(500)
    no_match_ok = case.verify_visible(info.jurisdiction.no_countries_message, "'No countries found' message")
    case.check("A non-existent search term shows a 'No countries found' message", no_match_ok,
               expected="message visible", actual=no_match_ok)

    ok = japan_visible and australia_hidden and no_match_ok
    actual = ("The country search box correctly filtered the list for a real match and showed a "
              "'No countries found' message for a bogus search term." if ok else
              "The country search box did not filter/message as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_information_04_jurisdiction_alone_does_not_render_content(page, result):
    case = Case(
        page, "Information_04", FEATURE, "Selecting only a jurisdiction (no category) keeps the placeholder",
        description="Checking a country's checkbox without also selecting a category must NOT replace the "
                     "'Select Jurisdictions and Categories' placeholder - both are required.",
        precondition="User is logged in and on the Information workspace.",
        test_data="Country: Australia",
        steps="1. Log in\n2. Check the 'Australia' checkbox only\n"
              "3. Verify the placeholder instruction text is still shown",
    )
    _login(case, page)
    info = InformationPage(page)

    case.step(2, "Select Australia's jurisdiction checkbox only")
    case.click(info.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    page.wait_for_timeout(800)

    case.step(3, "Verify the placeholder is still shown (a category is also required)")
    still_placeholder = case.verify_visible(info.placeholder_text, "left-panel instruction text")
    ok = still_placeholder
    case.check("Placeholder remains visible after selecting a jurisdiction with no category", ok,
               expected="placeholder still visible", actual=still_placeholder,
               locator=info.placeholder_text)

    actual = ("Selecting Australia's jurisdiction checkbox alone left the 'Select Jurisdictions and "
              "Categories' placeholder in place, confirming a category selection is also required to "
              "render content." if ok else
              "Selecting a jurisdiction alone unexpectedly rendered content without a category also "
              "being selected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_information_05_category_tree_expands_on_selection(page, result):
    case = Case(
        page, "Information_05", FEATURE, "Checking a parent category expands its child categories",
        description="Checking the 'Liability to Tax' parent category must expand the tree in place to "
                     "reveal its children (e.g. 'Residence').",
        precondition="User is logged in and on the Information workspace.",
        test_data="Category: Liability to Tax",
        steps="1. Log in\n2. Check the 'Liability to Tax' category checkbox\n"
              "3. Verify a child category ('Residence') becomes visible",
    )
    _login(case, page)
    info = InformationPage(page)

    case.step(2, "Check the 'Liability to Tax' parent category")
    residence_before = info.category.is_category_visible("Residence")
    case.click(info.category.category_checkbox("Liability to Tax"), "'Liability to Tax' category checkbox")
    page.wait_for_timeout(700)

    case.step(3, "Verify the 'Residence' child category is now visible")
    residence_after = case.verify_visible(info.category.category_label("Residence"), "'Residence' child category")
    ok = (not residence_before) and residence_after
    case.check("'Residence' is hidden before and visible after expanding 'Liability to Tax'", ok,
               expected="hidden then visible", actual=f"before={residence_before}, after={residence_after}")

    actual = ("Checking 'Liability to Tax' expanded the category tree, revealing the child category "
              "'Residence'." if ok else
              f"Checking 'Liability to Tax' did not expand the expected child category "
              f"(before={residence_before}, after={residence_after}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_information_06_check_all_selects_every_category(page, result):
    case = Case(
        page, "Information_06", FEATURE, "'Check All' selects every category (not the country list)",
        description="Clicking the 'Check All' checkbox (which sits in the CATEGORY tree, right above the "
                     "'Depth-' control) must check every category checkbox, including nested children, "
                     "while leaving the country checklist untouched.",
        precondition="User is logged in and on the Information workspace.",
        test_data="-",
        steps="1. Log in\n2. Click 'Check All'\n"
              "3. Verify the 'Liability to Tax' and a nested child category ('Residence') are both checked\n"
              "4. Verify the 'Australia' country checkbox is still unchecked (Check All only affects categories)",
    )
    _login(case, page)
    info = InformationPage(page)

    case.step(2, "Click 'Check All'")
    case.click(info.category.check_all_categories, "'Check All' checkbox (category tree)")
    page.wait_for_timeout(700)

    case.step(3, "Verify categories, including a nested child, are checked")
    parent_checked = info.category.category_checkbox("Liability to Tax").is_checked()
    child_checked = info.category.category_checkbox("Residence").is_checked()
    categories_ok = parent_checked and child_checked
    case.check("'Liability to Tax' and its child 'Residence' are checked after 'Check All'", categories_ok,
               expected="both checked", actual=f"parent={parent_checked}, child={child_checked}",
               locator=info.category.category_checkbox("Liability to Tax"))

    case.step(4, "Verify the country checklist was not affected")
    australia_untouched = not info.jurisdiction.is_country_checked("Australia")
    case.check("'Australia' remains unchecked - 'Check All' only applies to categories", australia_untouched,
               expected="unchecked", actual=not australia_untouched,
               locator=info.jurisdiction.country_checkbox("Australia"))

    ok = categories_ok and australia_untouched
    actual = ("Clicking 'Check All' checked every category (including nested children like 'Residence' "
              "under 'Liability to Tax') and left the country checklist untouched." if ok else
              f"'Check All' did not behave as expected (categories_ok={categories_ok}, "
              f"australia_untouched={australia_untouched}).")
    result(case, actual, ok)
    assert ok, actual
