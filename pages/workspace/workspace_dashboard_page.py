"""Workspace > Dashboard (`/companydata/dashboard/`), on-page heading
"Risk Heatmap". Confirmed live via scratchpad discovery (full HTML dump,
not part of the suite) that this page has two real, independently
verifiable sections, plus a yFiles-rendered chart that is NOT real,
assertable DOM content:

1. **Risk Heatmap** - a yFiles-licensed SVG tree chart ("A visual overview
   of risk across your entities") with a real, DOM-based legend (High
   Risk/Medium Risk/No Risk, each a `<span>` dot + label) - the chart
   canvas itself is an opaque third-party widget, so only the legend
   labels and the heading are asserted on, never the chart's visual
   content (no way to verify an SVG render meaningfully without a
   screenshot diff, which this framework does not do).
2. **News, Alerts & Updates** - a real, filterable feed. Confirmed live:
   4 real `<button class="reg-chip-button-choice...">` chips - "All (N)",
   "High (N)", "Medium (N)", "No Risk (N)" (the counts are real entity-risk
   counts, not placeholders; a chip with 0 real matches, e.g. "Medium (0)"
   on this account, renders `disabled` rather than clickable - confirmed
   live, NOT a bug). Clicking a non-"All" chip narrows the feed AND adds a
   "Filtered" label next to the "News, Alerts & Updates" heading (confirmed
   live via before/after innerText diff: the UK/Canada/Brazil news items
   that only applied to "No Risk"/other-risk entities disappeared from the
   feed once "High" was selected). A `placeholder="Search"` text input
   inside the news panel further narrows the same feed by free text.

**Real gotcha confirmed live**: the chip buttons' accessible name includes
the live count ("High (9)"), not just the risk label, so an exact-name
lookup breaks the moment the count changes - `risk_chip()` below matches
by a name REGEX anchored to the label text, not an exact string."""
import re

from playwright.sync_api import Page

from pages.workspace.workspace_common import WORKSPACE_DASHBOARD_URL, workspace_goto
from utils.wait import wait_for_content


class WorkspaceDashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.heading_risk_heatmap = page.get_by_role("heading", name="Risk Heatmap", exact=True)
        self.heading_news = page.get_by_role("heading", name="News, Alerts & Updates", exact=True)
        self.filtered_badge = page.get_by_text("Filtered", exact=True)

        self.legend_high_risk = page.get_by_text("High Risk", exact=True)
        self.legend_medium_risk = page.get_by_text("Medium Risk", exact=True)
        self.legend_no_risk = page.get_by_text("No Risk", exact=True)

        self.news_search = page.locator('input[placeholder="Search"]').first
        self.news_cards = page.locator("div[id^='event-card-']")
        self.risk_chips = page.locator("button.reg-chip-button-choice")
        # Each item inside a card carries a coloured left bar: red-800 for a
        # High-risk entity, green-500 for No Risk (confirmed live).
        self.card_risk_bars = page.locator("div[id^='event-card-'] div.absolute")
        self.empty_state = page.get_by_text("No news or updates match your current search or filter.", exact=True)
        self.collapse_panel_button = page.get_by_role("button", name="Collapse panel")
        self.heatmap_canvas = page.locator("canvas")
        self.heatmap_toolbar_buttons = page.locator(".dot-grid-bg button.reg-icon-button")
        self.ask_ai_button = page.get_by_text("Ask AI", exact=True)

    def goto(self):
        """Waits for the real 'Risk Heatmap' heading before returning
        control - the same `goto_and_wait_ready` discipline every other
        page object in this project follows, to avoid racing this SPA's
        render (confirmed live via a real test run: a bare `page.goto()`
        with no ready-wait can leave the next click/assert hitting a
        still-rendering page)."""
        workspace_goto(self.page, WORKSPACE_DASHBOARD_URL)
        wait_for_content(self.heading_risk_heatmap, timeout=30000)

    def risk_chip(self, label: str):
        """`label` one of "All"/"High"/"Medium"/"No Risk" - matches the
        real chip button regardless of its live count suffix."""
        return self.page.get_by_role("button", name=re.compile(rf"^{re.escape(label)}\s*\(\d+\)"))

    def is_risk_chip_disabled(self, label: str) -> bool:
        chip = self.risk_chip(label)
        if chip.count() == 0:
            return False
        return bool(chip.first.get_attribute("disabled") is not None)

    def news_item_count(self) -> int:
        """Counts real per-entity news/compliance-deadline cards in the
        feed. Confirmed live via HTML dump: each card is `<div
        id="event-card-<N>">` (a real, stable id prefix, not a generic
        Tailwind class) - used as the "how many items are showing" proxy
        the same way TPA World Tax Brief's `.brief-country-name` count is
        used."""
        return self.page.locator("div[id^='event-card-']").count()

    def card_entity_names(self) -> list:
        """Each feed card's entity name (its `<h6>` title, confirmed via
        HTML dump)."""
        return [t.strip() for t in self.page.locator("div[id^='event-card-'] h6").all_inner_texts()]

    def chip_counts(self) -> dict:
        """{"All": 15, "High": 10, "Medium": 0, "No Risk": 5} from the live chips."""
        out = {}
        for t in self.risk_chips.all_inner_texts():
            m = re.match(r"^(.*?)\s*\((\d+)\)\s*$", t.strip())
            if m:
                out[m.group(1).strip()] = int(m.group(2))
        return out

    def selected_chip_labels(self) -> list:
        """The active chip gets a colour-suffixed class
        (`reg-chip-button-choice-blue|red|yellow|green`) - confirmed live;
        chips are single-select."""
        out = []
        for b in self.risk_chips.all():
            if re.search(r"reg-chip-button-choice-\w+", b.get_attribute("class") or ""):
                out.append(re.sub(r"\s*\(\d+\)\s*$", "", b.inner_text().strip()))
        return out

    def risk_bar_colours(self) -> list:
        return self.page.evaluate("""() => [...new Set([...document.querySelectorAll(
            "div[id^='event-card-'] div.absolute")].map(e =>
            [...e.classList].find(c => c.startsWith('bg-reg-'))).filter(Boolean))]""")

    def clear_news_search(self):
        """Clears the search with real keystrokes (the feed only reacts to
        key events, so `fill("")` would leave it filtered)."""
        self.news_search.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")

    def card_flags(self) -> list:
        """Each card's jurisdiction flag alt text, e.g. "Singapore Flag"."""
        return self.page.evaluate("""() => [...document.querySelectorAll("div[id^='event-card-']")]
            .map(c => (c.querySelector('img[alt$="Flag"]') || {}).alt || '')""")

    def body_text(self) -> str:
        return self.page.evaluate("() => document.body.innerText")

    def card_texts(self) -> list:
        return self.page.locator("div[id^='event-card-']").all_inner_texts()

    def type_news_search(self, term: str):
        """Same keystroke-driven filter as Entities' grid search - `fill()`
        leaves the feed unfiltered (confirmed live: 10 stayed 10), typing
        key-by-key filters it (10 -> 1 for "Singapore")."""
        self.news_search.press_sequentially(term, delay=40)
