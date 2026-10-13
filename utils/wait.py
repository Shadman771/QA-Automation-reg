"""Shared, framework-wide navigation/content waiting. This is the single
place the "loader" problem gets solved: `wait_until="domcontentloaded"`
(used everywhere instead of `"networkidle"` - see CLAUDE.md/AGENT.md on why
`networkidle` can hang forever on this app's authenticated pages) only
guarantees the HTML document exists, NOT that the SPA has actually
rendered real content yet. Every page object's `goto()`, and every
menu's `open_item()`, must wait for a page-specific "this has genuinely
loaded" signal (a heading, placeholder, or other text element that's
always present once real content is up) before returning control -
never a fixed sleep, never assumed from the navigation call alone."""


def wait_for_content(locator, timeout: int = 10000) -> bool:
    """Waits for a locator (a heading, a table, a 'Showing ... of
    <Country>' heading, a commentary section, etc.) to become visible.
    Confirmed live: this app fetches data from the backend both on
    initial page load and after a jurisdiction/category selection, so a
    fixed short sleep is not reliably enough time under real network
    latency - this waits for the actual DOM change (up to `timeout`ms)
    instead of guessing a delay. Never raises; returns False (not visible
    in time) so callers assert on the boolean the same way they would on
    `Locator.is_visible()`."""
    try:
        locator.first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False


def goto_and_wait_ready(page, url: str, ready_locator, timeout: int = 20000) -> bool:
    """The one shared navigation helper every page object's `goto()`
    should call instead of a bare `page.goto()`. Navigates
    (`wait_until="domcontentloaded"`), then waits up to `timeout`ms for
    `ready_locator` - a heading/placeholder/other text element that is
    ALWAYS present once THIS specific page has genuinely finished
    rendering - to become visible, before returning. Returns the same
    True/False `wait_for_content` does; never raises on its own, so a
    page that never loads surfaces as a clear failure at the caller's own
    next assertion rather than a mysterious failure somewhere downstream."""
    page.goto(url, wait_until="domcontentloaded")
    return wait_for_content(ready_locator, timeout=timeout)


def wait_after_menu_navigation(page, ready_locator, timeout: int = 20000) -> bool:
    """The equivalent of `goto_and_wait_ready` for the Treaties/Tools/
    Calculator modules, whose pages have NO `goto()` (no deep link - see
    CLAUDE.md/AGENT.md) and are only reachable by clicking through their
    top-nav dropdown menu. Call this right after `<Menu>.open_item(name)`
    with the destination page's own ready locator, the same way
    `goto_and_wait_ready` is built into every other page's `goto()`."""
    return wait_for_content(ready_locator, timeout=timeout)
