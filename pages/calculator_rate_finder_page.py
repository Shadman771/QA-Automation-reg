"""Calculators > Corporate Rate Finder (/wta/CorpRateFinder).

Manually verified against the live application first (scratchpad discovery
scripts, not part of the suite). Distinct from every other WTA module's
jurisdiction panel (pages/wta_common.py): both the country list AND the
year list are MULTI-select here, and BOTH panels render simultaneously
without any "Select a jurisdiction..." gating placeholder - a static
"How to find and compare rates" instructions banner is shown at all times,
selection or not, so it cannot be used as a proxy for "no results yet".

  - Country checkboxes reuse pages.wta_common.JurisdictionPanel exactly
    (same <label><input><img><span> structure, confirmed live).
  - Year checkboxes are a SEPARATE, differently-structured list:
    `<div class="reg-checkbox-container"><input type="checkbox"
    class="reg-checkbox" value="2025"><label>2025</label></div>` - looked
    up here by `input.reg-checkbox[value='<year>']` since the input has no
    `id`/`for` pairing with its label.
  - Selecting N countries x M years renders a results table with one ROW
    per selected year and one COLUMN per selected country (alphabetical),
    Year column sortable (toggles `?sort=year:asc|asc` in the URL).
  - "Show More" switches the SAME data into a taller/denser table variant
    (confirmed live: a different <table> markup, same cell values).
  - A country's table-header name (`span.reg-link-button`) opens an
    `.rs-modal-wrapper` titled "Corporate rate details for <Country>" with
    its own Tax Year/Type/Rate/Footnote table and its own "Export:"
    control - NOT a new page/tab (confirmed: clicking it never opens a
    popup, only a same-page modal - same rsuite modal pattern documented
    in CLAUDE.md for Treaties' `span.reg-link-button` cells).
  - "Export:" (both the main toolbar's and the modal's) is two icon
    buttons - confirmed via `GET .../api/CorporateRate?countryCodes=..&year=..`
    network capture that the underlying data is real; the first icon is
    the Excel/XLSX export, the second a print-preview action, matching the
    identical two-icon pattern already documented for Treaties pages.
  - REAL, LIVE-CONFIRMED DATA GAP: `HeadlineRate` (and every other rate
    field) is `null` for the large majority of country/year combinations
    checked (AU/IN/CN/SG/JP/US/CA/DE across multiple recent years all
    returned `HeadlineRate: null`) - the results table legitimately
    renders an empty value cell in that case, which is real application
    behavior, not a bug to hide. One confirmed live exception used as this
    suite's calculation-validation anchor: Bangladesh (`BD`) + tax year
    2024 has a real non-null `HeadlineRate` of `55` with footnote "This
    for the testingg .." (evidently seeded test data by the business
    team) - `GET https://regplusnest.api.kaz.com.bd/api/CorporateRate?
    countryCodes=BD&year=2024` is used as the independent source of truth
    the UI's "55%" cell is checked against, rather than re-deriving the
    value from the UI itself.
  - Same no-deep-link quirk as every Tools page (see pages/tools_menu.py):
    `page.goto()` to `/wta/CorpRateFinder` redirects to `/wta/Information`,
    so this page object has no `goto()` - reach it only via
    `CalculatorMenu.open_item("Corporate Rate Finder")`."""
from playwright.sync_api import Page

from pages.wta_common import JurisdictionPanel

CORPORATE_RATE_API = "https://regplusnest.api.kaz.com.bd/api/CorporateRate"


class CorporateRateFinderPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.instructions_heading = page.get_by_role("heading", name="How to find and compare rates")
        self.select_year_heading = page.get_by_text("Select Year", exact=True)
        self.show_more_button = page.get_by_role("button", name="Show More")
        self.export_label = page.get_by_text("Export:", exact=True).first
        self.export_icons = page.locator("span.reg-icon-button")
        self.results_table = page.locator("table").first
        self.modal = page.locator(".rs-modal-wrapper")
        self.modal_close_button = page.locator(".rs-modal-wrapper .reg-icon-button").first

    def year_checkbox(self, year):
        return self.page.locator(f"input.reg-checkbox[value='{year}']")

    def year_column_header(self, country: str):
        return self.page.locator("table").first.locator("span.reg-link-button", has_text=country)

    def open_country_detail_modal(self, country: str):
        self.year_column_header(country).first.click()

    def close_modal(self):
        self.modal_close_button.click()
