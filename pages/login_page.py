"""Locators come from scripts/discover.py's dump of the real login page
(#email, #password, button[type=submit]) - not guessed.

Full-page DOM dump re-verified live (2026-09-23) for 100% element coverage:
  - Left marketing panel: "World Tax Analyzer (WTA)" heading, 7 feature
    bullets (Shield tick icon + text, e.g. "Comprehensive Coverage of Tax
    Laws Across 120 Jurisdictions"), a "Request a Free Trial" link to
    https://www.reganalytics.com/request-free-trial (external), and 2
    carousel-dot buttons.
  - Center card: REG Analytics logo (<img alt="REG Analytics Logo">), "Log
    In" H1, Email label+input (#email, type=email, placeholder="Email"),
    Password label+input (#password, type=password, placeholder="Password"),
    a password show/hide toggle (an icon-only <span> immediately after
    #password - confirmed it flips the input's type attribute
    password<->text on click), "Forgot Password?" link, the Log In submit
    button, an "OR" divider, and "Login with Google" button.
  - No <footer> element exists on this page - there is nothing to assert
    there."""
from playwright.sync_api import Page

from config.settings import BASE_URL
from utils.wait import goto_and_wait_ready


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # Center login card
        self.logo = page.get_by_alt_text("REG Analytics Logo")
        self.heading = page.get_by_role("heading", name="Log In")
        self.email_label = page.locator("label", has_text="Email")
        self.email = page.locator("#email")
        self.password_label = page.locator("label", has_text="Password")
        self.password = page.locator("#password")
        self.password_toggle = page.locator("#password").locator("xpath=following-sibling::span[1]")
        self.submit = page.locator('button[type="submit"]')
        self.forgot_password_link = page.get_by_text("Forgot Password?")
        self.or_divider = page.get_by_text("OR", exact=True)
        self.google_login = page.get_by_role("button", name="Login with Google")

        # Left marketing panel. This is a 2-slide AUTO-ROTATING carousel (2
        # dot buttons observed): a WTA slide (8 feature bullets) and a
        # Transfer-Pricing-product slide (9 bullets, same CSS classes) -
        # confirmed live that which slide is active depends on elapsed time,
        # not a fixed default. The :visible pseudo-class scopes to whichever
        # slide is currently active; callers must accept either bullet count
        # (8 or 9), never assume one specific slide is showing.
        self.left_panel_heading = page.get_by_role("heading", name="World Tax Analyzer (WTA)")
        self.free_trial_link = page.get_by_role("link", name="Request a Free Trial")
        self.feature_bullets = page.locator(
            "span.text-14-medium.text-reg-gray-600:visible"
        )

    def goto(self):
        goto_and_wait_ready(self.page, BASE_URL, self.heading)

    def is_loaded(self) -> bool:
        return (self.heading.is_visible() and self.email.is_visible()
                and self.password.is_visible() and self.submit.is_visible())

    def wait_for_banner(self, timeout: int = 6000) -> str:
        """Polls body text for the known banner strings (a custom pink/red
        banner, not a native validation bubble - see scripts/discover_invalid.py)."""
        candidates = ("Invalid Credentials!", "Email is required!", "Password is required!")
        elapsed = 0
        step_ms = 200
        while elapsed <= timeout:
            body = self.page.evaluate("() => document.body.innerText")
            for candidate in candidates:
                if candidate in body:
                    return candidate
            self.page.wait_for_timeout(step_ms)
            elapsed += step_ms
        return ""
