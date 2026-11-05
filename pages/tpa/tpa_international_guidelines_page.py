"""TPA > Information > International Guidelines (/tpa/InternationalGuideline).
Confirmed live via scratchpad discovery scripts (not part of the suite).

**Real gotcha**: the left panel's "Guideline" selector (EU/OECD/UN) does
NOT use `JurisdictionPanel`'s country `<label><span>Name</span></label>`
shape - it uses the SAME DOM shape as `CategoryTree`
(`<input type="checkbox" id="G12"><label for="G12">OECD</label>`), with
its own "Check All" (`#checkAllGuideline`, a DIFFERENT id from the
category tree's own `#checkAll`). So this page composes TWO
`CategoryTree` instances - one for the 3-item Guideline selector, one for
the 17-item category list - rather than needing any new panel class.

Selecting a Guideline (e.g. OECD) AND a top-level category (e.g. "Basic
rule") renders real content: the top-level category expands into its own
nested sub-topics (confirmed live: "Basic rule" expands into "Global
business and the arm's length principle", "Aligning transfer pricing
outcomes with value creation", etc.), each with its own heading and (for
some, not all - a real, confirmed content gap, not a defect) a paragraph
of real text. The content area has an "Export:" control, a "Category"
selector, and a "Compare jurisdiction(s) against Guideline(s)" button -
a DIFFERENT label from National Rules' own "Compare with other years".
No per-sub-topic "Commentary" button exists here (unlike National Rules)
- confirmed live, not assumed.

Supports a direct deep link (`/tpa/InternationalGuideline`, see
pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto
from pages.wta.wta_common import CategoryTree

GUIDELINE_BODIES = ["EU", "OECD", "UN"]

INTERNATIONAL_GUIDELINES_CATEGORIES = [
    "Basic rule", "Legislative design principles", "Transfer pricing methods",
    "Measuring and monitoring BEPS", "Mandatory disclosure rules", "Documentation",
    "Comparability", "Dispute resolution", "Intangibles", "Intragroup services",
    "Cost contribution arrangements", "Business restructurings", "Financial transactions",
    "Digital economy transactions", "Interaction with customs valuation",
    "Information exchange", "Audits and risk assessment",
]


class TpaInternationalGuidelinesPage:
    def __init__(self, page: Page):
        self.page = page
        self.guideline = CategoryTree(page)
        self.guideline.check_all_categories = page.locator("#checkAllGuideline")
        self.category = CategoryTree(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose guideline and categories.")
        self.export_label = page.get_by_text("Export:", exact=False)
        self.compare_button = page.get_by_role("button", name="Compare jurisdiction(s) against Guideline(s)")

    def goto(self):
        tpa_goto(self.page, "/tpa/InternationalGuideline")

    def sub_topic_heading(self, text: str):
        return self.page.get_by_text(text, exact=True)
