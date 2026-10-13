"""Shared "Jurisdictions [and Categories/Filters]" left panel, reused across
almost every World Tax Analyzer module (Information, every Pillar 2
sub-page, News, Forms, Regulations). Confirmed live via scripts/discover_wta.py:

  - Region tab buttons: Asia Pacific / Americas / Europe / MEA
    (`<button class="reg-tab-button-square-container">`).
  - A "Search countries" text input that filters the country list, showing
    'No countries found matching "..."' on no match.
  - Each country is a `<label>` wrapping an `<input>` + a flag `<img>` + a
    `<span>` with the country name - looked up here by the visible name so
    the automation is not tied to ISO codes. The underlying `<input>`
    differs by page: multi-select pages (Information, Pillar 2 >
    Information) use a visible `<input type="checkbox">`; single-select
    pages (Compliance Calendar, Country Commentary, Pillar 2 Forms/
    Regulation/News, top-level News/Forms/Regulations - anywhere the left
    panel says "Select Jurisdiction", singular) use an `<input
    type="radio" class="hidden">` that is NOT visible/clickable itself (a
    sibling `<div>` renders the visible dot). Confirmed live
    (scripts/discover_wta.py) that clicking the always-visible `<label>`
    reliably toggles either kind, so that is what `country_checkbox()`
    targets - clicking the raw `<input>` directly times out on the
    single-select pages since it is hidden.
  - Where a category tree exists (Information, Pillar 2 > Information,
    Forms), each row is `<div><input type="checkbox" id="<Label><numericId>">
    <label>Label</label></div>` - the numeric id suffix is data-driven, so
    categories are also looked up by visible label text via xpath.
  - Right-hand content only replaces the "Select Jurisdiction(s)..." helper
    text once enough of the left panel is selected (confirmed: jurisdiction
    alone is enough on Compliance Calendar / Pillar 2 Forms / Country
    Commentary / Pillar 2 Regulation / Pillar 2 News / News / Forms /
    Regulations; Information and Pillar 2 > Information additionally
    require a category to be selected).

Every module-specific page object in this package composes a
`JurisdictionPanel` instance instead of redeclaring these locators."""
from playwright.sync_api import Page


def wait_for_content(locator, timeout: int = 10000) -> bool:
    """Waits for a server-rendered content locator (a table, a 'Showing
    ... of <Country>' heading, a commentary section, etc.) to become
    visible after a jurisdiction/category selection. Confirmed live: these
    pages fetch data from the backend on selection, so a fixed short sleep
    is not reliably enough time under real network latency - this waits
    for the actual DOM change (up to `timeout`ms) instead of guessing a
    delay. Never raises; returns False (not visible in time) so callers
    assert on the boolean the same way they would on `Locator.is_visible()`."""
    try:
        locator.first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False


class JurisdictionPanel:
    def __init__(self, page: Page):
        self.page = page
        self.search_countries = page.get_by_placeholder("Search countries")
        self.no_countries_message = page.get_by_text("No countries found matching", exact=False)

    def region_tab(self, name: str):
        return self.page.get_by_role("button", name=name, exact=True)

    def country_checkbox(self, name: str):
        """The country's clickable <label> (found by its visible name,
        robust to the underlying ISO id). Targets the label rather than
        the raw <input> because on single-select pages that input is a
        hidden radio button - see the module docstring."""
        return self.page.locator(f"xpath=//label[.//span[normalize-space(text())='{name}']]")

    def country_row_visible(self, name: str):
        return self.country_checkbox(name)

    def is_country_checked(self, name: str) -> bool:
        """Reads the underlying <input>'s checked state via JS, since it
        works whether that input is a visible checkbox or a hidden radio."""
        try:
            return bool(self.page.evaluate(
                """(name) => {
                    const label = [...document.querySelectorAll('label')].find(l => {
                        const span = l.querySelector('span');
                        return span && span.textContent.trim() === name;
                    });
                    const input = label ? label.querySelector('input') : null;
                    return input ? input.checked : false;
                }""",
                name,
            ))
        except Exception:
            return False


class CategoryTree:
    """The optional category checklist to the right of/under the
    jurisdiction list (Information, Pillar 2 > Information, Forms). Each
    entry is `<input id="<Label><numericId>"> <label>Label</label>` as
    plain siblings, not wrapped - so the checkbox is the label's immediate
    preceding sibling."""
    def __init__(self, page: Page):
        self.page = page
        self.search_categories = page.get_by_placeholder("Search categories")
        # Confirmed live: id="checkAll" belongs to the CATEGORY tree's
        # "Check All" row (it appears right before the "Depth-" control),
        # not the country list - it checks every category checkbox.
        self.check_all_categories = page.locator("#checkAll")

    def category_checkbox(self, label: str):
        return self.page.locator(
            f"xpath=//label[normalize-space(text())='{label}']/preceding-sibling::input[@type='checkbox'][1]"
        )

    def category_label(self, label: str):
        return self.page.get_by_text(label, exact=True)

    def is_category_visible(self, label: str) -> bool:
        try:
            return self.category_label(label).first.is_visible()
        except Exception:
            return False
