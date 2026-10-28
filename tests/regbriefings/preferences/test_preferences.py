"""RegBriefings > Preferences (overlay modal, no dedicated URL).

New parent module (RegBriefings), built via live DOM discovery - no
QA-sheet reference exists. This is the last of the 6 RegBriefings
sub-features. Preferences opens as an overlay on whatever RegBriefings
page is currently showing (confirmed live, see
pages/regbriefings/preferences_page.py docstring) and controls the
real, shared account's brief-type subscriptions (which directly drive
My Briefs' aggregation, see tests/regbriefings/mybriefs/test_my_briefs.py
MyBriefs_03) and jurisdiction interests.

**Real shared-account caution, applied throughout this file**: this is
the SAME real account used across the whole project, not a disposable
test account. The one test that clicks "Save" (PREFS_07) captures the
full original Briefs-tab checkbox state first, changes only one
checkbox, saves, verifies the change, then restores the exact original
state and saves again - leaving the account unchanged when the test
ends, same self-cleaning discipline as the Tools Projects module.
"Reset to Default" is never clicked in this suite - the Jurisdictions
tab's checklist has dozens of countries per region, and reliably
capturing/restoring its exact original state is both riskier and far
less valuable than the much simpler, fully-reversible 3-checkbox Briefs
tab test."""
import pytest

from pages.regbriefings.regbriefings_common import RegBriefingsNav
from pages.regbriefings.preferences_page import PreferencesPage
from utils.auth import perform_login
from utils.case import Case

FEATURE = "RegBriefings Preferences"

BRIEF_LABELS = ["World Tax Brief", "Transfer Pricing Brief", "Tax Treaty Brief"]


def _login_and_open(case, page):
    perform_login(case, page)
    case.action("Opening RegBriefings > Preferences", kind="navigate")
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    prefs = PreferencesPage(page)
    case.click(nav.nav_preferences, "'Preferences' sidebar link")
    page.wait_for_timeout(1200)
    case.verify_visible(prefs.select_product_heading, "'Select Product' heading")
    return nav, prefs


@pytest.mark.smoke
def test_prefs_01_opens_as_overlay_on_briefs_tab(page, result):
    case = Case(
        page, "Prefs_01", FEATURE, "Preferences opens as an overlay, defaulting to the 'Briefs' tab",
        description="Clicking 'Preferences' must open an overlay modal (NOT navigate to a new URL) "
                     "defaulting to the 'Briefs' tab with 'Select Product' and all 3 brief-type "
                     "checkboxes visible.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n"
              "2. Verify the URL did NOT change and the Briefs tab's content is visible",
    )
    url_before = None
    perform_login(case, page)
    nav = RegBriefingsNav(page)
    nav.open_tab()
    page.wait_for_timeout(1000)
    url_before = page.url
    prefs = PreferencesPage(page)
    case.step(2, "Click Preferences and verify it opens as an overlay on the Briefs tab")
    case.click(nav.nav_preferences, "'Preferences' sidebar link")
    page.wait_for_timeout(1200)

    url_unchanged = page.url == url_before
    content_ok = case.verify_visible(prefs.select_product_heading, "'Select Product' heading")
    ok = url_unchanged and content_ok
    case.check("Preferences opens as an overlay on the 'Briefs' tab, URL unchanged", ok,
               expected=f"url unchanged ({url_before}), 'Select Product' visible",
               actual=f"url={page.url}, content={content_ok}")
    prefs.cancel_button.click()
    page.wait_for_timeout(500)

    actual = ("Preferences correctly opened as an overlay on the 'Briefs' tab without changing the URL."
              if ok else "Preferences did not open as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_prefs_02_switching_to_jurisdictions_tab(page, result):
    case = Case(
        page, "Prefs_02", FEATURE, "Switching to the 'Jurisdictions' tab shows the jurisdiction panel",
        description="Clicking 'Jurisdictions' must show 'Select Jurisdiction' with 4 region tabs (Asia "
                     "Pacific/Americas/Europe/MEA) - same shape as WTA's JurisdictionPanel.",
        precondition="User is logged in, Preferences open on the 'Briefs' tab.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n2. Click the 'Jurisdictions' tab\n"
              "3. Verify 'Select Jurisdiction' and all 4 region tabs are visible",
    )
    nav, prefs = _login_and_open(case, page)
    case.step(2, "Click the 'Jurisdictions' tab")
    case.click(prefs.jurisdictions_tab, "'Jurisdictions' tab")
    page.wait_for_timeout(1000)

    case.step(3, "Verify 'Select Jurisdiction' and all 4 region tabs are visible")
    heading_ok = case.verify_visible(prefs.select_jurisdiction_heading, "'Select Jurisdiction' heading")
    missing_regions = [r for r in ["Asia Pacific", "Americas", "Europe", "MEA"]
                        if not case.verify_visible(prefs.region_tab(r), f"'{r}' region tab")]
    ok = heading_ok and not missing_regions
    case.check("The 'Jurisdictions' tab shows its expected panel", ok,
               expected="heading visible, all 4 region tabs visible",
               actual=f"heading={heading_ok}, missing_regions={missing_regions}")
    prefs.cancel_button.click()
    page.wait_for_timeout(500)

    actual = ("The 'Jurisdictions' tab correctly showed its expected panel." if ok else
              f"The 'Jurisdictions' tab did not show the expected panel (missing: {missing_regions}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_prefs_03_briefs_checkboxes_reflect_real_account_state(page, result):
    case = Case(
        page, "Prefs_03", FEATURE, "The 3 Briefs checkboxes reflect the real account's actual subscription state",
        description="Each of the 3 Briefs checkboxes must be in a definite checked/unchecked state (not "
                     "missing or indeterminate) - this is the real source of truth My Briefs reads from "
                     "(see MyBriefs_03).",
        precondition="User is logged in, Preferences open on the 'Briefs' tab.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n2. Verify each of the 3 Briefs checkboxes has a "
              "definite checked state",
    )
    nav, prefs = _login_and_open(case, page)
    case.step(2, "Verify each of the 3 Briefs checkboxes has a definite checked state")
    states = {}
    errors = []
    for label in BRIEF_LABELS:
        try:
            states[label] = prefs.brief_checkbox(label).is_checked()
        except Exception as e:
            errors.append(f"{label}: {e}")
    ok = len(states) == 3 and not errors
    case.check("All 3 Briefs checkboxes have a definite, readable state", ok,
               expected="3 readable checkbox states", actual=f"states={states}, errors={errors}")
    prefs.cancel_button.click()
    page.wait_for_timeout(500)

    actual = (f"All 3 Briefs checkboxes correctly reported their real state: {states}." if ok else
              f"Could not read all 3 Briefs checkboxes' state (errors={errors}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_prefs_04_jurisdiction_country_checkbox_present_and_readable(page, result):
    case = Case(
        page, "Prefs_04", FEATURE, "A real jurisdiction checkbox (Australia) is present and readable",
        description="On the 'Jurisdictions' tab, the visible 'Australia' country checkbox must be present "
                     "and have a definite checked state - confirmed live every region's checklist is "
                     "mounted in the DOM at once (hidden, not removed), so this must resolve to exactly "
                     "the one currently-visible match, not a strict-mode-ambiguous multi-match.",
        precondition="User is logged in, Preferences open on the 'Jurisdictions' tab.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences, switch to 'Jurisdictions'\n"
              "2. Verify the 'Australia' checkbox is present with a definite state",
    )
    nav, prefs = _login_and_open(case, page)
    case.click(prefs.jurisdictions_tab, "'Jurisdictions' tab")
    page.wait_for_timeout(1000)

    case.step(2, "Verify the 'Australia' checkbox is present with a definite state")
    try:
        checked = prefs.country_checkbox("Australia").is_checked()
        ok = True
    except Exception as e:
        checked = None
        ok = False
    case.check("The 'Australia' jurisdiction checkbox is present and readable", ok,
               expected="a single, readable checkbox", actual=f"checked={checked}")
    prefs.cancel_button.click()
    page.wait_for_timeout(500)

    actual = (f"The 'Australia' jurisdiction checkbox was correctly present (checked={checked})." if ok else
              "The 'Australia' jurisdiction checkbox could not be read unambiguously.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_prefs_05_cancel_closes_overlay_without_changes(page, result):
    case = Case(
        page, "Prefs_05", FEATURE, "'Cancel' closes the Preferences overlay",
        description="Clicking 'Cancel' must close the overlay and return to the underlying page (the "
                     "overlay is no longer visible, and the underlying sidebar is clickable again).",
        precondition="User is logged in, Preferences open.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n2. Click 'Cancel'\n"
              "3. Verify the overlay is closed and the sidebar is usable again",
    )
    nav, prefs = _login_and_open(case, page)
    case.step(2, "Click 'Cancel'")
    case.click(prefs.cancel_button, "'Cancel' button")
    page.wait_for_timeout(800)

    case.step(3, "Verify the overlay is closed and the sidebar is usable again")
    overlay_gone = prefs.select_product_heading.count() == 0 or not prefs.select_product_heading.first.is_visible()
    sidebar_ok = case.verify_visible(nav.nav_my_briefs, "'My Briefs' sidebar link")
    ok = overlay_gone and sidebar_ok
    case.check("'Cancel' closes the overlay and the sidebar becomes usable again", ok,
               expected="overlay closed, sidebar usable", actual=f"overlay_gone={overlay_gone}, sidebar_ok={sidebar_ok}")

    actual = ("'Cancel' correctly closed the Preferences overlay." if ok else
              "'Cancel' did not close the Preferences overlay as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_prefs_06_reset_to_default_and_save_buttons_present(page, result):
    case = Case(
        page, "Prefs_06", FEATURE, "'Reset to Default' and 'Save' buttons are present",
        description="Both 'Reset to Default' and 'Save' must be visible alongside 'Cancel' - structural "
                     "presence only, neither is clicked here (see module docstring for why 'Reset to "
                     "Default' is never exercised in this suite).",
        precondition="User is logged in, Preferences open.",
        test_data="-",
        steps="1. Log in, open RegBriefings > Preferences\n"
              "2. Verify 'Reset to Default' and 'Save' are both visible",
    )
    nav, prefs = _login_and_open(case, page)
    case.step(2, "Verify 'Reset to Default' and 'Save' are both visible")
    reset_ok = case.verify_visible(prefs.reset_to_default_button, "'Reset to Default' button")
    save_ok = case.verify_visible(prefs.save_button, "'Save' button")
    ok = reset_ok and save_ok
    case.check("'Reset to Default' and 'Save' are both visible", ok,
               expected="both visible", actual=f"reset={reset_ok}, save={save_ok}")
    prefs.cancel_button.click()
    page.wait_for_timeout(500)

    actual = ("Both 'Reset to Default' and 'Save' are correctly visible." if ok else
              "One or both of 'Reset to Default'/'Save' were not visible.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_prefs_07_toggling_a_brief_subscription_and_saving_persists_then_is_restored(page, result):
    case = Case(
        page, "Prefs_07", FEATURE, "Toggling a Briefs checkbox and saving actually persists the change",
        description="Unchecking 'Transfer Pricing Brief' and clicking Save must actually persist (verified "
                     "by reopening Preferences fresh) - then the test restores the EXACT original state of "
                     "all 3 checkboxes and saves again, leaving the real shared account unchanged when the "
                     "test ends (see module docstring).",
        precondition="User is logged in.",
        test_data="Toggle: Transfer Pricing Brief",
        steps="1. Log in, open Preferences, capture the original state of all 3 checkboxes\n"
              "2. Toggle 'Transfer Pricing Brief' and Save\n"
              "3. Reopen Preferences fresh and verify the toggle persisted\n"
              "4. Restore the exact original state of all 3 checkboxes and Save again",
    )
    nav, prefs = _login_and_open(case, page)
    case.step(1, "Capture the original state of all 3 checkboxes")
    original_state = {label: prefs.brief_checkbox(label).is_checked() for label in BRIEF_LABELS}

    case.step(2, "Toggle 'Transfer Pricing Brief' and Save")
    target_label = "Transfer Pricing Brief"
    case.click(prefs.brief_checkbox(target_label), f"'{target_label}' checkbox")
    expected_after_toggle = not original_state[target_label]
    case.click(prefs.save_button, "'Save' button")
    page.wait_for_timeout(1500)

    case.step(3, "Reopen Preferences fresh and verify the toggle persisted")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    nav2 = RegBriefingsNav(page)
    case.click(nav2.nav_preferences, "'Preferences' sidebar link (reopened)")
    page.wait_for_timeout(1200)
    prefs2 = PreferencesPage(page)
    persisted_state = prefs2.brief_checkbox(target_label).is_checked()
    toggle_ok = persisted_state == expected_after_toggle

    case.step(4, "Restore the exact original state of all 3 checkboxes and Save again")
    for label in BRIEF_LABELS:
        current = prefs2.brief_checkbox(label).is_checked()
        if current != original_state[label]:
            case.click(prefs2.brief_checkbox(label), f"'{label}' checkbox (restoring)")
    case.click(prefs2.save_button, "'Save' button (restoring original state)")
    page.wait_for_timeout(1500)

    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    nav3 = RegBriefingsNav(page)
    nav3.nav_preferences.click()
    page.wait_for_timeout(1200)
    prefs3 = PreferencesPage(page)
    restored_state = {label: prefs3.brief_checkbox(label).is_checked() for label in BRIEF_LABELS}
    restore_ok = restored_state == original_state
    prefs3.cancel_button.click()
    page.wait_for_timeout(500)

    ok = toggle_ok and restore_ok
    case.check("Toggling persisted, then the original state was exactly restored", ok,
               expected=f"toggle persisted to {expected_after_toggle}, restored state == {original_state}",
               actual=f"persisted={persisted_state}, restored={restored_state}")

    actual = ("The toggle correctly persisted after Save, and the original account state was exactly "
              "restored afterward." if ok else
              f"Save did not behave as expected (toggle_ok={toggle_ok}, restore_ok={restore_ok}, "
              f"original={original_state}, persisted={persisted_state}, restored={restored_state}).")
    result(case, actual, ok)
    assert ok, actual
