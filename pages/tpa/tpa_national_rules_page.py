"""TPA > Information > National Rules (/tpa/NationalRules). Confirmed
live via scratchpad discovery scripts (not part of the suite): the same
"Jurisdictions and Categories" left panel shape as WTA's Information/
Pillar 2 Information pages - `JurisdictionPanel` (single-select country)
+ `CategoryTree` (14 categories: Requirements, Special areas, Financial
transactions, Digital economy transactions, Safe harbour, Application,
Comparability, Documentation, Compliance, Information exchange, Audits,
Adjustments, APAs, Dispute resolution), "Check All", Depth 1-4 - both
reused unmodified from pages/wta/wta_common.py.

Selecting a jurisdiction AND a category renders real content: one
sub-topic heading per real question (e.g. "Scope of transfer pricing
rules", "OECD Guidelines", "Related party definition"), each with a real
paragraph of legal text, a pipe-separated list of real regulation
citations, and its own "Commentary" button (confirmed live: 3 sub-topics
under "Requirements" for Australia, 3 matching "Commentary" buttons). The
content area also has an "Export:" control (3 icon-only download
buttons, no visible text labels - confirmed live via `<img>` src, not a
single labelled button) and a "Compare with other years" button.

Supports a direct deep link (`/tpa/NationalRules`, see
pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel, CategoryTree

NATIONAL_RULES_CATEGORIES = [
    "Requirements", "Special areas", "Financial transactions", "Digital economy transactions",
    "Safe harbour", "Application", "Comparability", "Documentation", "Compliance",
    "Information exchange", "Audits", "Adjustments", "APAs", "Dispute resolution",
]


class TpaNationalRulesPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.category = CategoryTree(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdictions and categories.")
        self.export_label = page.get_by_text("Export:", exact=False)
        self.compare_years_button = page.get_by_role("button", name="Compare with other years")
        self.commentary_buttons = page.get_by_role("button", name="Commentary")

    def goto(self):
        tpa_goto(self.page, "/tpa/NationalRules")

    def sub_topic_heading(self, text: str):
        return self.page.get_by_text(text, exact=True)
