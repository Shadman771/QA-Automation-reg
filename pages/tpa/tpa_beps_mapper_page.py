"""TPA > BEPS > BEPS Mapper (/tpa/beps). Confirmed live via scratchpad
discovery scripts (not part of the suite): the "more" overflow menu's
"BEPS" submenu toggle has exactly 2 children - "BEPS Questionnaire"
(/tpa/BEPSQuestionnaireCreator, see tpa_beps_questionnaire_page.py) and
"BEPS Mapper" (/tpa/beps) - this file covers the latter.

**Real business purpose, confirmed live, genuinely different from every
other TPA/WTA "jurisdiction + category" page**: "BEPS Mapper" is NOT a
data-field mapper in the ETL/import-export sense the feature name might
suggest - it maps each of the 15 BEPS Action items (BEPS 1.0) / 2 Pillars
(BEPS 2.0) to WHERE that topic is actually covered across the application's
other modules (Transfer Pricing Analyzer / World Tax Analyzer), for a
selected jurisdiction. Confirmed live for Australia + "Action 1: Tax
Challenges Arising from Digitalisation": expanding the action reveals a
"Transfer Pricing Analyzer" sub-section with 3 real checkable items
("Digital economy transactions-General/-Services covered/-Profit
allocation") and a "World Tax Analyzer" sub-section reading "Not Covered in
World Tax Analyzer (WTA)" - i.e. the mapping result can legitimately be
"not covered at all" in a given module, which is real, correct behavior,
not missing data.

Left panel heading is "Jurisdictions, Pillars and Categories" (confirmed
live via a full text dump) - a 3-word heading distinct from every other
WTA/TPA page's "Select Jurisdiction"/"Jurisdictions [and Categories]"
wording, so not asserted against those other pages' exact strings.
Placeholder text before an action is picked: "Use the left panel to choose
actions." (also page-specific wording - "actions", not "jurisdiction"). The
country list itself (region tabs, search, `<label>` country shape) is
confirmed live BYTE-IDENTICAL to `pages/wta/wta_common.py`'s
`JurisdictionPanel` (same markup, same "Search countries" placeholder), so
it is reused unmodified here - verified, not assumed.

**Real, live-confirmed distinct component, NOT `CategoryTree`**: the
Pillars/Categories panel is an ACCORDION tree, not a flat checkbox list -
confirmed live via a full HTML dump showing each top-level row ("BEPS 2.0",
"BEPS 1.0", and each "Action N: ..."/Pillar label under them) rendered as
plain `<span>` text with a "+" expand icon and NO underlying `<input>` at
all (`cb.count() == 0` confirmed for a raw "preceding-sibling checkbox"
probe against an Action label - `CategoryTree.category_checkbox()`'s xpath
genuinely does not apply here). Clicking a top-level Action/Pillar label
EXPANDS it (confirmed live: clicking "Action 1: ..." revealed its
Transfer-Pricing-Analyzer/World-Tax-Analyzer sub-sections, each sub-section
is visually distinguished by its own `tpa-section`/`wta-section` CSS
class), rather than toggling a selection state directly on that label.
ONLY the nested leaf items 2 levels down (e.g. "Digital economy
transactions-General") are real checkboxes - confirmed live via HTML dump:
`<div class="reg-checkbox-container"><input type="checkbox">
<p>Label</p></div>`, i.e. the checkbox is the `<p>`'s own PRECEDING SIBLING,
not a `<label for=...>` wrapper - the same "checkbox is a sibling, not an
ancestor/descendant" family of gotcha already documented project-wide (e.g.
WHT Router's Intermediaries modal, `pages/landing_page.py::category_checkbox`),
confirmed here independently rather than assumed to match.

A top-level "All" region-style toggle plus "BEPS 2.0"/"BEPS 1.0" group
headers and their own "Check All" control are present (confirmed live via
the same text dump) - same "Check All" id/shape as every other category
tree in the project (`#checkAll`), reused directly since this control (unlike
the leaf items) IS a real top-of-tree action matching that project-wide
pattern.

Supports a direct deep link (`/tpa/beps`, confirmed live) - same pattern as
every other TPA page. An "Ask AI" control is present (confirmed live,
presence-only, same scope decision as BEPS Questionnaire's)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel


class TpaBepsMapperPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.heading = page.get_by_text("Jurisdictions, Pillars and Categories", exact=True)
        self.placeholder_text = page.get_by_text("Use the left panel to choose actions.", exact=False)
        self.check_all = page.locator("#checkAll")
        self.ask_ai_button = page.get_by_role("button", name="Ask AI")
        self.mapper_country_heading = page.get_by_text("BEPS Mapper", exact=True)

    def goto(self):
        tpa_goto(self.page, "/tpa/beps")

    def action_label(self, text: str):
        """A top-level Action ("Action N: ...") or Pillar label - clicking
        it EXPANDS its Transfer Pricing Analyzer / World Tax Analyzer
        sub-sections, it is not itself a checkbox."""
        return self.page.get_by_text(text, exact=True)

    def expand_action(self, text: str):
        self.action_label(text).first.click()

    def leaf_checkbox(self, label: str):
        """A nested, 2-levels-deep checkable mapping item (e.g. "Digital
        economy transactions-General") - the checkbox is the <p>'s own
        preceding sibling <input>, not a <label> wrapper."""
        return self.page.locator(
            f"xpath=//p[normalize-space(text())='{label}']/preceding-sibling::input[@type='checkbox'][1]"
        )

    def is_leaf_visible(self, label: str) -> bool:
        try:
            return self.page.get_by_text(label, exact=True).first.is_visible()
        except Exception:
            return False

    def not_covered_in_wta_text(self):
        return self.page.get_by_text("Not Covered in World Tax Analyzer (WTA)", exact=True)

    def tpa_section_heading(self):
        return self.page.locator("div.tpa-section").locator("xpath=preceding-sibling::h5[1]")

    def selected_country_chip(self, name: str):
        """A selected-jurisdiction 'pill' (flag + name + a 'Remove' button) -
        confirmed live this page renders selections as removable chips
        rather than just leaving the left-panel checkbox checked."""
        return self.page.locator("span").filter(has_text=name).filter(
            has=self.page.get_by_role("button", name="Remove")
        )
