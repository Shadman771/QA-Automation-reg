"""Login page - Regplus World Tax Analyzer.

Every scenario here was manually verified against the live application via
a discovery script before being automated:
  - #email / #password / button[type=submit] are the real selectors.
  - An empty submit shows a pink banner "Email is required!" - not native
    HTML5 validation.
  - Wrong credentials show a pink banner "Invalid Credentials!" and stay on
    /auth/login/.
  - A correct login redirects to /wta/Information.

Every click/fill/check below goes through `case.*`, which red-highlights
the exact element being interacted with or verified and pushes a live
event to the dashboard (see utils/case.py, utils/highlight.py, utils/dashboard.py).
"""
import pytest

from config.settings import LOGIN_EMAIL, LOGIN_PASSWORD
from pages.login_page import LoginPage
from utils.case import Case

FEATURE = "Login"


@pytest.mark.smoke
def test_login_01_page_loads(page, result):
    case = Case(
        page, "LOGIN_01", FEATURE, "Login page loads with all required elements",
        description="The login page must render the World Tax Analyzer login form.",
        precondition="Browser is open, user is not authenticated.",
        test_data="-",
        steps="1. Navigate to BASE_URL\n2. Verify the Log In heading, email field, "
              "password field and submit button are visible",
    )
    case.step(1, "Navigate to the login page")
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Verify required elements are visible")
    heading_ok = case.verify_visible(login_page.heading, "Log In heading")
    email_ok = case.verify_visible(login_page.email, "Email field")
    password_ok = case.verify_visible(login_page.password, "Password field")
    submit_ok = case.verify_visible(login_page.submit, "Log In submit button")
    ok = heading_ok and email_ok and password_ok and submit_ok
    case.check("Log In heading, email field, password field and submit button are visible", ok,
               expected="All four elements visible", actual=ok)

    actual = ("The login page loaded with the 'Log In' heading, an email field, a password "
              "field and an enabled 'Log In' submit button, all visible." if ok else
              "One or more required login elements were not visible on page load.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_login_02_password_is_masked(page, result):
    case = Case(
        page, "LOGIN_02", FEATURE, "Password field masks input",
        description="Characters typed into the password field must not be shown in plain text.",
        precondition="Login page is open.",
        test_data="Password: <masked, from .env>",
        steps="1. Navigate to the login page\n2. Type a password\n3. Verify the field's type attribute is 'password'",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()
    case.step(2, "Enter a password")
    case.fill(login_page.password, LOGIN_PASSWORD, "Password field", mask=True)

    case.step(3, "Verify the field masks input")
    input_type = login_page.password.get_attribute("type")
    ok = input_type == "password"
    case.check("Password input has type='password' (masked)", ok, expected="password", actual=input_type,
               locator=login_page.password)

    actual = (f"The password field's type attribute is '{input_type}', so entered characters "
              "are masked." if ok else
              f"The password field's type attribute is '{input_type}', so input is NOT masked.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_03_empty_submit_shows_validation(page, result):
    case = Case(
        page, "LOGIN_03", FEATURE, "Submitting the login form empty shows a validation message",
        description="Clicking Log In with no email/password must show an inline validation banner.",
        precondition="Login page is open, both fields are empty.",
        test_data="-",
        steps="1. Navigate to the login page\n2. Click 'Log In' without entering anything\n"
              "3. Verify a validation banner appears",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()
    case.step(2, "Submit the form with no data")
    case.click(login_page.submit, "Log In button (empty form)")

    case.step(3, "Wait for the validation banner")
    banner = login_page.wait_for_banner()
    ok = banner != ""
    case.check("A validation banner is shown for the missing field", ok,
               expected="'Email is required!' or similar", actual=banner or "no banner shown")

    actual = (f"Submitting the empty form showed the banner '{banner}' and the page stayed on "
              f"{page.url}." if ok else
              f"Submitting the empty form showed no validation banner. Page: {page.url}")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_04_invalid_credentials(page, result):
    case = Case(
        page, "LOGIN_04", FEATURE, "Invalid credentials show an error and do not authenticate",
        description="A wrong password must be rejected with an error banner, and the user must remain unauthenticated.",
        precondition="Login page is open.",
        test_data=f"Email: {LOGIN_EMAIL} (valid) / Password: intentionally wrong",
        steps="1. Navigate to the login page\n2. Enter the valid email with a wrong password\n"
              "3. Click Log In\n4. Verify an 'Invalid Credentials!' banner appears and the URL stays on /auth/login/",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()
    case.step(2, "Enter valid email with an incorrect password")
    case.fill(login_page.email, LOGIN_EMAIL, "Email field")
    case.fill(login_page.password, "WrongPassword123", "Password field", mask=True)

    case.step(3, "Click Log In")
    case.click(login_page.submit, "Log In button")

    case.step(4, "Wait for the error banner")
    banner = login_page.wait_for_banner()
    stayed_on_login = "/auth/login" in page.url
    ok = banner == "Invalid Credentials!" and stayed_on_login
    case.check("'Invalid Credentials!' banner is shown", banner == "Invalid Credentials!",
               expected="Invalid Credentials!", actual=banner)
    case.check("User remains on the login page (not authenticated)", stayed_on_login,
               expected="URL contains /auth/login", actual=page.url)

    actual = (f"Submitting a wrong password showed the banner '{banner}' and the user remained on "
              f"{page.url}, unauthenticated." if ok else
              f"Expected the 'Invalid Credentials!' banner and to stay on /auth/login/, but got "
              f"banner='{banner}', url={page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_login_05_valid_credentials_redirect(page, result):
    case = Case(
        page, "LOGIN_05", FEATURE, "Valid credentials authenticate and redirect to the landing page",
        description="A correct email/password must log the user in and redirect to the World Tax "
                     "Analyzer Information workspace (/wta/Information).",
        precondition="Login page is open.",
        test_data=f"Email: {LOGIN_EMAIL} / Password: <masked, from .env>",
        steps="1. Navigate to the login page\n2. Enter valid credentials\n3. Click Log In\n"
              "4. Verify the URL becomes /wta/Information",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()
    case.step(2, "Enter valid credentials")
    case.fill(login_page.email, LOGIN_EMAIL, "Email field")
    case.fill(login_page.password, LOGIN_PASSWORD, "Password field", mask=True)

    case.step(3, "Click Log In")
    case.click(login_page.submit, "Log In button")

    case.step(4, "Wait for redirect")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    ok = "/wta/Information" in page.url
    case.check("Redirected to /wta/Information after login", ok,
               expected="URL contains /wta/Information", actual=page.url)

    actual = (f"After submitting valid credentials, the application authenticated the user and "
              f"redirected to {page.url}." if ok else
              f"After submitting valid credentials, the application did not redirect to the "
              f"expected landing page. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_06_forgot_password_link(page, result):
    case = Case(
        page, "LOGIN_06", FEATURE, "'Forgot Password?' link navigates to the reset page",
        description="Clicking 'Forgot Password?' must navigate to /auth/forgot-password/.",
        precondition="Login page is open.",
        test_data="-",
        steps="1. Navigate to the login page\n2. Click 'Forgot Password?'\n3. Verify the URL",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()
    case.step(2, "Click 'Forgot Password?'")
    case.click(login_page.forgot_password_link, "'Forgot Password?' link")
    page.wait_for_load_state("domcontentloaded")

    case.step(3, "Verify the URL")
    ok = "/auth/forgot-password" in page.url
    case.check("URL contains /auth/forgot-password/", ok,
               expected="/auth/forgot-password/", actual=page.url)

    actual = (f"Clicking 'Forgot Password?' navigated to {page.url}." if ok else
              f"Clicking 'Forgot Password?' did not navigate to the reset page. Ended on {page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.smoke
def test_login_07_full_ui_content(page, result):
    case = Case(
        page, "LOGIN_07", FEATURE, "All login page UI/content elements are present and correct",
        description="Every visible text, label, placeholder, logo and link on the login page must "
                     "render as designed (logo, headings, labels, placeholders, links). There is no "
                     "<footer> element on this page - confirmed by DOM inspection, so nothing is "
                     "asserted there.",
        precondition="Login page is open.",
        test_data="-",
        steps="1. Navigate to the login page\n2. Verify the logo, headings, field labels/placeholders "
              "and left-panel marketing content are all visible",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Verify center card elements")
    checks = {
        "REG Analytics logo": case.verify_visible(login_page.logo, "REG Analytics logo"),
        "'Log In' heading": case.verify_visible(login_page.heading, "'Log In' heading"),
        "Email label": case.verify_visible(login_page.email_label, "Email label"),
        "Password label": case.verify_visible(login_page.password_label, "Password label"),
        "'OR' divider": case.verify_visible(login_page.or_divider, "'OR' divider"),
    }

    case.step(3, "Verify field placeholders")
    email_placeholder = login_page.email.get_attribute("placeholder")
    password_placeholder = login_page.password.get_attribute("placeholder")
    checks["Email placeholder == 'Email'"] = email_placeholder == "Email"
    checks["Password placeholder == 'Password'"] = password_placeholder == "Password"
    case.check("Email field placeholder is 'Email'", email_placeholder == "Email",
               expected="Email", actual=email_placeholder, locator=login_page.email)
    case.check("Password field placeholder is 'Password'", password_placeholder == "Password",
               expected="Password", actual=password_placeholder, locator=login_page.password)

    case.step(4, "Verify left-panel marketing content")
    checks["Left panel 'World Tax Analyzer (WTA)' heading"] = case.verify_visible(
        login_page.left_panel_heading, "'World Tax Analyzer (WTA)' heading")
    checks["'Request a Free Trial' link"] = case.verify_visible(
        login_page.free_trial_link, "'Request a Free Trial' link")
    # The left panel auto-rotates between 2 carousel slides (2 dot buttons
    # observed): a WTA slide (8 bullets) and a Transfer Pricing slide (9
    # bullets) - which one is active depends on real elapsed time, so a
    # fixed count would be flaky. Accept either valid slide size.
    bullet_count = login_page.feature_bullets.count()
    valid_slide_sizes = (8, 9)
    checks["Left panel shows a valid carousel slide's worth of feature bullets"] = (
        bullet_count in valid_slide_sizes)
    case.check(f"Left panel shows one of {valid_slide_sizes} visible feature bullets "
               "(the panel auto-rotates between a WTA slide and a Transfer Pricing slide)",
               bullet_count in valid_slide_sizes, expected=f"one of {valid_slide_sizes}",
               actual=bullet_count)

    for label, ok_i in checks.items():
        case.check(label, ok_i, expected=True, actual=ok_i)

    ok = all(checks.values())
    failing = [k for k, v in checks.items() if not v]
    actual = ("All UI/content elements (logo, headings, labels, placeholders, left-panel marketing "
              "content) rendered correctly." if ok else f"Missing/incorrect elements: {failing}")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_08_password_show_hide_toggle(page, result):
    case = Case(
        page, "LOGIN_08", FEATURE, "Password show/hide toggle reveals and re-masks the password",
        description="Clicking the eye icon next to the password field must flip its input type "
                     "between 'password' (masked) and 'text' (visible), and back again.",
        precondition="Login page is open.",
        test_data="Password: <masked, from .env>",
        steps="1. Navigate to the login page\n2. Type a password\n3. Click the show/hide toggle - "
              "verify the field becomes type=text\n4. Click it again - verify it returns to type=password",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Enter a password")
    case.fill(login_page.password, LOGIN_PASSWORD, "Password field", mask=True)
    initial_type = login_page.password.get_attribute("type")

    case.step(3, "Click the show/hide toggle to reveal the password")
    case.click(login_page.password_toggle, "Password show/hide toggle")
    revealed_type = login_page.password.get_attribute("type")
    revealed_ok = revealed_type == "text"
    case.check("Password field becomes type='text' after clicking the toggle", revealed_ok,
               expected="text", actual=revealed_type, locator=login_page.password)

    case.step(4, "Click the toggle again to re-mask the password")
    case.click(login_page.password_toggle, "Password show/hide toggle")
    remasked_type = login_page.password.get_attribute("type")
    remasked_ok = remasked_type == "password"
    case.check("Password field returns to type='password' after clicking the toggle again", remasked_ok,
               expected="password", actual=remasked_type, locator=login_page.password)

    ok = initial_type == "password" and revealed_ok and remasked_ok
    actual = (f"The show/hide toggle correctly flipped the password field between masked and visible "
              f"(password -> text -> password)." if ok else
              f"Toggle behavior incorrect: initial={initial_type}, after first click={revealed_type}, "
              f"after second click={remasked_type}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_09_sql_injection_blocked_by_email_format(page, result):
    case = Case(
        page, "LOGIN_09", FEATURE,
        "SQL-injection-style input with no '@' is rejected by native email-format validation",
        description="The email field has type='email', so browser-native validation must block "
                     "submission of a non-email-format SQL-injection-style payload before it ever "
                     "reaches the server - confirmed live: Chromium's own validationMessage fires.",
        precondition="Login page is open.",
        test_data="Email: ' OR '1'='1  (SQLi-style, no '@') / Password: ' OR '1'='1' --",
        steps="1. Navigate to the login page\n2. Enter a non-email-format SQL-injection-style string "
              "in the Email field\n3. Click Log In\n4. Verify the browser's native validation blocks "
              "submission (still on /auth/login/, a validationMessage is present)",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Enter a non-email-format SQL-injection-style payload")
    case.fill(login_page.email, "' OR '1'='1", "Email field")
    case.fill(login_page.password, "' OR '1'='1' --", "Password field", mask=True)

    case.step(3, "Click Log In")
    case.click(login_page.submit, "Log In button")
    page.wait_for_timeout(800)

    case.step(4, "Verify native validation blocked submission")
    validation_message = login_page.email.evaluate("el => el.validationMessage")
    stayed_on_login = "/auth/login" in page.url
    ok = stayed_on_login and bool(validation_message)
    case.check("Still on /auth/login/ (form did not submit)", stayed_on_login,
               expected="/auth/login/", actual=page.url)
    case.check("Native email validationMessage is present", bool(validation_message),
               expected="non-empty validation message", actual=validation_message or "(empty)")

    actual = (f"The browser blocked the SQL-injection-style, non-email-format input before "
              f"submission (validationMessage: {validation_message!r}); the request never reached "
              f"the server." if ok else
              f"Expected native validation to block submission. Stayed on login: {stayed_on_login}, "
              f"validationMessage: {validation_message!r}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_10_sql_injection_rejected_server_side(page, result):
    case = Case(
        page, "LOGIN_10", FEATURE,
        "A valid-format SQL-injection-style email/password is rejected as invalid credentials",
        description="An SQL-injection-style payload shaped like a valid email address (so it passes "
                     "client-side validation and reaches the server) must be rejected with the normal "
                     "'Invalid Credentials!' banner, not authenticate, and not error/crash the app - "
                     "confirmed live against the real backend.",
        precondition="Login page is open.",
        test_data="Email: admin'--@test.com / Password: ' OR '1'='1' --",
        steps="1. Navigate to the login page\n2. Enter an SQL-injection-style email (valid format) "
              "and password\n3. Click Log In\n4. Verify 'Invalid Credentials!' is shown and the user "
              "is not authenticated",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Enter a valid-format SQL-injection-style email and password")
    case.fill(login_page.email, "admin'--@test.com", "Email field")
    case.fill(login_page.password, "' OR '1'='1' --", "Password field", mask=True)

    case.step(3, "Click Log In")
    case.click(login_page.submit, "Log In button")

    case.step(4, "Wait for the error banner")
    banner = login_page.wait_for_banner()
    stayed_on_login = "/auth/login" in page.url
    ok = banner == "Invalid Credentials!" and stayed_on_login
    case.check("'Invalid Credentials!' banner is shown (no SQL injection / auth bypass)",
               banner == "Invalid Credentials!", expected="Invalid Credentials!", actual=banner)
    case.check("User remains on the login page (not authenticated)", stayed_on_login,
               expected="URL contains /auth/login", actual=page.url)

    actual = (f"The SQL-injection-style credentials were correctly rejected: banner '{banner}', "
              f"user remained on {page.url}, unauthenticated. No injection/auth-bypass observed." if ok
              else f"Expected rejection with 'Invalid Credentials!', got banner='{banner}', "
                   f"url={page.url}.")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_11_google_login_button_present(page, result):
    case = Case(
        page, "LOGIN_11", FEATURE, "'Login with Google' button is visible and enabled",
        description="The alternate OAuth entry point must be visible and enabled. Not clicked here - "
                     "it navigates to an external Google OAuth consent screen outside this suite's scope.",
        precondition="Login page is open.",
        test_data="-",
        steps="1. Navigate to the login page\n2. Verify the 'Login with Google' button is visible "
              "and enabled",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Verify the Google login button")
    visible = case.verify_visible(login_page.google_login, "'Login with Google' button")
    enabled = login_page.google_login.is_enabled() if visible else False
    ok = visible and enabled
    case.check("'Login with Google' button is visible and enabled", ok,
               expected="visible and enabled", actual=f"visible={visible}, enabled={enabled}",
               locator=login_page.google_login)

    actual = ("The 'Login with Google' button is visible and enabled." if ok else
              f"The 'Login with Google' button was not both visible and enabled "
              f"(visible={visible}, enabled={enabled}).")
    result(case, actual, ok)
    assert ok, actual


@pytest.mark.regression
def test_login_12_free_trial_link_points_external(page, result):
    case = Case(
        page, "LOGIN_12", FEATURE, "'Request a Free Trial' link points to the correct external URL",
        description="The left-panel 'Request a Free Trial' link must point to "
                     "https://www.reganalytics.com/request-free-trial. Not clicked/navigated here - "
                     "it's an external marketing site outside this suite's scope.",
        precondition="Login page is open.",
        test_data="-",
        steps="1. Navigate to the login page\n2. Verify the 'Request a Free Trial' link's href",
    )
    login_page = LoginPage(page)
    case.action("Navigating to the login page", kind="navigate")
    login_page.goto()

    case.step(2, "Verify the 'Request a Free Trial' link href")
    case.verify_visible(login_page.free_trial_link, "'Request a Free Trial' link")
    href = login_page.free_trial_link.get_attribute("href")
    expected_href = "https://www.reganalytics.com/request-free-trial"
    ok = href == expected_href
    case.check("'Request a Free Trial' href is correct", ok,
               expected=expected_href, actual=href, locator=login_page.free_trial_link)

    actual = (f"'Request a Free Trial' correctly points to {href}." if ok else
              f"Expected href {expected_href!r}, got {href!r}.")
    result(case, actual, ok)
    assert ok, actual
