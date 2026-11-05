"""TPA > Case Law (/tpa/CaseLaw). Confirmed live via scratchpad discovery
scripts (not part of the suite): the same "Jurisdictions and Categories"
left panel shape as National Rules - `JurisdictionPanel` + the identical
14-item `CategoryTree` (Requirements, Special areas, Financial
transactions, Digital economy transactions, Safe harbour, Application,
Comparability, Documentation, Compliance, Information exchange, Audits,
Adjustments, APAs, Dispute resolution).

**Real, structurally DIFFERENT content shape from every other TPA
table page (Forms/Regulations)**: the rendered table's columns are
"Case Number", "Case Title", "Date of Decision", "Court" - confirmed
live there is NO download link and NO "Add to Project" button anywhere
on this page (0 matches, not a timing issue - re-checked after a full
content render).

**Real gotcha confirmed live**: unlike National Rules/International
Guidelines, this page's category checklist (and its "Check All"
checkbox) starts with EVERY category already checked by default, not
unchecked - confirmed via `#checkAll`'s own `checked` attribute on a
fresh page load. This means selecting a jurisdiction ALONE already
renders real content (no explicit category click needed), and clicking
"Check All" a first time actually UNCHECKS everything (a toggle, not an
idempotent "select all"). Tests here select a country alone and leave
categories at their real default, rather than clicking a specific
category (which would otherwise un-select it from an already-all-on
state).

**Real, confirmed-live data gap**: most country/category combinations
show "No results found" (e.g. Australia/Requirements, Bangladesh/any,
China/any, Japan/any, Indonesia/any - all confirmed live) - this is a
genuine, sparse-data application state, not a defect. India/"Special
areas" is a confirmed-good real-content anchor (4 real cases, e.g.
"Azadi Bachao Andolan and Anr. v. Union of India and Anr.", Supreme
Court of India, 07-Oct-2003) used here instead of Australia/Requirements
(which is itself a confirmed real empty state, used as the "genuine no
results" anchor).

Supports a direct deep link (`/tpa/CaseLaw`, see
pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import JurisdictionPanel, CategoryTree

CASE_LAW_CATEGORIES = [
    "Requirements", "Special areas", "Financial transactions", "Digital economy transactions",
    "Safe harbour", "Application", "Comparability", "Documentation", "Compliance",
    "Information exchange", "Audits", "Adjustments", "APAs", "Dispute resolution",
]


class TpaCaseLawPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.category = CategoryTree(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction and categories.")
        self.showing_case_laws_text = page.get_by_text("Showing case laws of", exact=False)
        self.no_results_text = page.get_by_text("No results found", exact=True)
        self.col_case_number = page.get_by_text("Case Number", exact=True)
        self.col_case_title = page.get_by_text("Case Title", exact=True)
        self.col_date_of_decision = page.get_by_text("Date of Decision", exact=True)
        self.col_court = page.get_by_text("Court", exact=True)

    def goto(self):
        tpa_goto(self.page, "/tpa/CaseLaw")
