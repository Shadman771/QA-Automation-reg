"""Pillar 2 > Forms (/wta/PillarTwoForms).

Manually verified against the live application first (scripts/discover_wta.py):
  - Left panel: jurisdiction list only (no categories).
  - Selecting a jurisdiction alone renders a 'Showing forms of <Country>'
    table (Title / Description / Applies to tax year ending on / Download
    / Project) with an 'English' download link and an 'Add to Project'
    button per row. For Australia there are 2 known rows (NAT 0656-06.2025,
    NAT 0656-6.2011)."""
import os

import pytest

from pages.pillar2_forms_page import PillarTwoFormsPage
from pages.wta_common import wait_for_content
from utils.auth import perform_login
from utils.case import Case

FEATURE = "WTA Pillar2 Forms"


def _login_and_open(case, page):
    perform_login(case, page)
    forms = PillarTwoFormsPage(page)
    case.action("Navigating to /wta/PillarTwoForms", kind="navigate")
    forms.goto()
    return forms


@pytest.mark.smoke
def test_p2forms_01_page_loads_with_placeholder(page, result):
    case = Case(
        page, "P2Forms_01", FEATURE, "Pillar 2 > Forms loads with the jurisdiction placeholder",
        description="The page must load showing the left-panel instruction text.",
        precondition="User is logged in.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Forms\n2. Verify the placeholder text is visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Verify the placeholder is visible")
    ok = case.verify_visible(forms.placeholder_text, "left-panel instruction text")
    case.check("Placeholder instruction text is visible", ok, expected="visible", actual=ok,
               locator=forms.placeholder_text)

    actual = ("Pillar 2 > Forms loaded with the placeholder visible." if ok else
              "Pillar 2 > Forms did not show the expected placeholder.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_p2forms_02_selecting_jurisdiction_renders_forms_table(page, result):
    case = Case(
        page, "P2Forms_02", FEATURE, "Selecting a jurisdiction renders the forms table",
        description="Checking 'Australia' must render a 'Showing forms of Australia' table with the "
                     "expected columns.",
        precondition="User is logged in and on Pillar 2 > Forms.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > Forms\n2. Check 'Australia'\n"
              "3. Verify the forms table and its column headers are visible",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_text)

    case.step(3, "Verify table and columns")
    showing_ok = case.verify_visible(forms.showing_text, "'Showing forms of' text")
    title_ok = case.verify_visible(forms.col_title, "'Title' column header")
    download_ok = case.verify_visible(forms.col_download, "'Download' column header")
    project_ok = case.verify_visible(forms.col_project, "'Project' column header")
    ok = showing_ok and title_ok and download_ok and project_ok
    case.check("Forms table with Title/Download/Project columns is visible", ok,
               expected="all visible",
               actual=f"showing={showing_ok}, title={title_ok}, download={download_ok}, project={project_ok}")

    actual = ("Selecting Australia rendered the forms table with the expected columns." if ok else
              "The forms table or its columns did not render as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2forms_03_download_link_and_add_to_project_present(page, result):
    case = Case(
        page, "P2Forms_03", FEATURE, "Each form row has a Download link and an Add to Project button",
        description="For Australia, at least one row must show an 'English' download link and an "
                     "'Add to Project' button.",
        precondition="User is logged in, Australia selected on Pillar 2 > Forms.",
        test_data="Country: Australia",
        steps="1. Log in, open Pillar 2 > Forms, select Australia\n"
              "2. Verify an 'English' download link and an 'Add to Project' button are visible",
    )
    forms = _login_and_open(case, page)
    forms.jurisdiction.country_checkbox("Australia").click()
    wait_for_content(forms.showing_text)

    case.step(2, "Verify download link and Add to Project button")
    download_ok = case.verify_visible(forms.download_links.first, "'English' download link")
    add_ok = case.verify_visible(forms.add_to_project_buttons.first, "'Add to Project' button")
    ok = download_ok and add_ok
    case.check("A download link and an 'Add to Project' button are present", ok,
               expected="both visible", actual=f"download={download_ok}, add_to_project={add_ok}")

    actual = ("Each form row exposed a download link and an 'Add to Project' action." if ok else
              "A form row was missing its download link or 'Add to Project' action.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2forms_04_region_tab_switch_hides_out_of_region_country(page, result):
    case = Case(
        page, "P2Forms_04", FEATURE, "Switching region tabs hides out-of-region countries",
        description="Clicking 'Americas' must hide 'Australia' (Asia Pacific) from the jurisdiction list.",
        precondition="User is logged in and on Pillar 2 > Forms.",
        test_data="-",
        steps="1. Log in and open Pillar 2 > Forms\n2. Click the 'Americas' region tab\n"
              "3. Verify 'Australia' is no longer listed",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Click the 'Americas' region tab")
    case.click(forms.jurisdiction.region_tab("Americas"), "'Americas' region tab")
    page.wait_for_timeout(500)

    case.step(3, "Verify Australia is hidden")
    ok = not forms.jurisdiction.country_row_visible("Australia").is_visible()
    case.check("'Australia' is not listed under 'Americas'", ok, expected="hidden", actual=not ok)

    actual = ("Switching to 'Americas' hid 'Australia' from the jurisdiction list." if ok else
              "Switching region tabs did not hide the out-of-region country as expected.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_p2forms_05_download_link_triggers_real_file_download(page, result):
    case = Case(
        page, "P2Forms_05", FEATURE, "The 'English' download link triggers a real, non-empty file download",
        description="With Australia selected, clicking the first 'English' download link must trigger a real "
                     "download with no failure and a non-zero size - P2Forms_03 only proved the link is visible, "
                     "not that it actually downloads anything.",
        precondition="User is logged in, Australia selected on Pillar 2 > Forms.",
        test_data="Country: Australia",
        steps="1. Log in and open Pillar 2 > Forms\n2. Select Australia\n"
              "3. Click the first 'English' download link\n"
              "4. Verify a real, non-empty file download completed",
    )
    forms = _login_and_open(case, page)
    case.step(2, "Select Australia")
    case.click(forms.jurisdiction.country_checkbox("Australia"), "'Australia' checkbox")
    wait_for_content(forms.showing_text)

    case.step(3, "Click the first 'English' download link")
    with page.expect_download(timeout=15000) as dl_info:
        case.click(forms.download_links.first, "'English' download link")
    download = dl_info.value

    case.step(4, "Verify the download")
    filename = download.suggested_filename
    failure = download.failure()
    path = download.path()
    size = os.path.getsize(path) if path else 0
    ok = failure is None and size > 0
    case.check("The 'English' download link produces a real, non-empty file with no failure", ok,
               expected="failure=None, size>0", actual=f"failure={failure}, filename={filename!r}, size={size}")

    actual = (f"The download link correctly downloaded '{filename}' ({size} bytes)." if ok else
              f"The download link did not produce a valid download (failure={failure}, filename={filename!r}, "
              f"size={size}).")
    result(case, actual, ok)
    assert ok, actual
