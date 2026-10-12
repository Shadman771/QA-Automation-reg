"""Case: a test case's metadata plus helpers that, on every interaction or
assertion, (1) log to the console/log file, (2) push a live event to the
dashboard (utils/dashboard.py), (3) draw a red outline around the exact
element being acted on or verified (utils/highlight.py), and (4) capture a
small labeled screenshot AT THE MOMENT the element is highlighted, so the
red outline shows up in saved evidence (self.evidence) - not just whatever
happens to be on screen at the very end of the test."""
import re

from utils.logger import get_logger, step as log_step, action as log_action, assertion as log_assertion
from utils.highlight import highlight
from utils import dashboard
from config.settings import SCREENSHOTS_DIR, ASSERTION_TIMEOUT_MS


class Case:
    def __init__(self, page, case_id: str, feature: str, title: str, description: str = "",
                 precondition: str = "", test_data: str = "", steps: str = ""):
        self.page = page
        self.id = case_id
        self.feature = feature
        self.title = title
        self.description = description
        self.precondition = precondition
        self.test_data = test_data
        self.steps = steps
        self.assertions = []
        self.evidence = []
        self._evidence_dir = SCREENSHOTS_DIR / "_pending" / feature / case_id
        self._evidence_n = 0
        self.logger = get_logger(feature)
        dashboard.start_case(feature, case_id, title)

    def _capture_evidence(self, kind: str, label: str):
        """Saves a small (viewport, not full-page) screenshot right after an
        element has been red-highlighted, so the highlight is visible in the
        saved evidence. Best-effort: never fails the test."""
        try:
            self._evidence_n += 1
            self._evidence_dir.mkdir(parents=True, exist_ok=True)
            safe_label = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_")[:40] or kind
            fname = f"step_{self._evidence_n:02d}_{kind}_{safe_label}.png"
            out_path = self._evidence_dir / fname
            self.page.screenshot(path=str(out_path))
            self.evidence.append({
                "n": self._evidence_n, "kind": kind, "label": label, "path": out_path,
            })
        except Exception:
            pass

    def step(self, n: int, text: str):
        log_step(self.logger, n, text)
        dashboard.add_step(n, text)

    def action(self, text: str, kind: str = "info"):
        log_action(self.logger, text)
        dashboard.set_action(kind, text)

    def goto(self, url: str, label: str = ""):
        self.action(f"Navigating to {label or url}", kind="navigate")
        self.page.goto(url, wait_until="networkidle")

    def click(self, locator, label: str, force: bool = False, native_js: bool = False):
        """native_js: dispatches a real DOM click via `element.click()`
        (JS), bypassing Playwright's actionability/visibility system
        entirely - for the rare case of an element that's functionally
        clickable (its handler fires) but CSS-clipped in a way Playwright
        can't compute a click point for, even with force=True (confirmed
        live: a max-height/overflow-collapsed tree node in
        pages/tools_questionnaire_creator_page.py). Prefer force=False,
        then force=True, before reaching for this - it skips real
        actionability guarantees."""
        self.action(f"Clicking: {label}", kind="click")
        highlight(self.page, locator)
        self._capture_evidence("click", label)
        if native_js:
            locator.evaluate("el => el.click()")
        else:
            locator.click(force=force)

    def fill(self, locator, value: str, label: str, mask: bool = False):
        shown = "<masked>" if mask else value
        self.action(f"Typing into {label}: {shown}", kind="type")
        highlight(self.page, locator)
        self._capture_evidence("type", label)
        locator.fill(value)

    def verify_visible(self, locator, label: str) -> bool:
        """Highlights `locator` in red while checking visibility, so the
        element being verified is visible on screen as it's checked.

        Actually WAITS (up to ASSERTION_TIMEOUT_MS) for the element to
        become visible rather than an instant check - `Locator.is_visible()`
        alone does NOT auto-wait/retry the way `.click()`/`expect()` do, it
        just reports the current DOM state immediately. That was masked for
        a long time by page-level `wait_until="networkidle"` navigation
        effectively pre-waiting for the SPA to finish rendering before any
        test logic ran; switching page objects to `domcontentloaded` (a
        separate, confirmed-live fix for pages whose persistent background
        requests never let networkidle resolve) exposed this - initial-load
        assertions started firing before the React app had rendered.
        Waiting here, at the assertion itself, is the correct fix rather
        than re-adding a blocking page-level wait."""
        self.action(f"Checking visibility: {label}", kind="verify")
        try:
            locator.first.wait_for(state="visible", timeout=ASSERTION_TIMEOUT_MS)
        except Exception:
            return False
        try:
            highlight(self.page, locator, hold_ms=220)
            self._capture_evidence("verify", label)
        except Exception:
            pass
        return True

    def check(self, text: str, passed: bool, expected="", actual="", locator=None) -> bool:
        if locator is not None:
            try:
                highlight(self.page, locator, hold_ms=250)
                self._capture_evidence("check", text)
            except Exception:
                pass
        log_assertion(self.logger, text, passed, expected, actual)
        dashboard.set_assertion(text, passed)
        self.assertions.append({
            "text": text, "passed": bool(passed),
            "expected": str(expected), "actual": str(actual),
        })
        return passed
