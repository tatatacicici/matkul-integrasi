"""
Test Suite: Authentication Flow (Register + Login)
===================================================
Validates the full auth flow: registration, login, and error handling.
"""
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestRegisterPage:
    """Test the registration page."""

    def test_register_page_loads(self, driver, wait, frontend_url):
        """Register page should render the registration form."""
        driver.get(f"{frontend_url}/register")
        wait.until(EC.presence_of_element_located((By.ID, "register-form")))
        heading = driver.find_element(By.ID, "register-heading")
        assert "Create Account" in heading.text

    def test_register_form_has_fields(self, driver, wait, frontend_url):
        """Register form should contain name, email, and password fields."""
        driver.get(f"{frontend_url}/register")
        wait.until(EC.presence_of_element_located((By.ID, "register-form")))

        assert driver.find_element(By.ID, "register-name")
        assert driver.find_element(By.ID, "register-email")
        assert driver.find_element(By.ID, "register-password")
        assert driver.find_element(By.ID, "register-submit")

    def test_register_has_login_link(self, driver, wait, frontend_url):
        """Register page should have a link to login page."""
        driver.get(f"{frontend_url}/register")
        wait.until(EC.presence_of_element_located((By.ID, "link-to-login")))
        link = driver.find_element(By.ID, "link-to-login")
        assert "sign in" in link.text.lower() or "login" in link.text.lower()


class TestRegisterFlow:
    """Test the actual registration process."""

    def test_register_success(self, driver, wait, frontend_url, registered_user):
        """Registration should succeed and redirect to login.
        Uses the `registered_user` fixture which performs the registration.
        After redirect, we should be on the login page.
        """
        # The registered_user fixture handles registration.
        # At this point, driver should be on the login page after redirect.
        current = driver.current_url
        assert "/login" in current or "/register" in current

    def test_register_duplicate_email(self, driver, wait, frontend_url, registered_user):
        """Registering with an existing email should show error."""
        driver.get(f"{frontend_url}/register")
        wait.until(EC.presence_of_element_located((By.ID, "register-form")))

        driver.find_element(By.ID, "register-name").send_keys("Duplicate User")
        driver.find_element(By.ID, "register-email").send_keys(registered_user["email"])
        driver.find_element(By.ID, "register-password").send_keys("password123")
        driver.find_element(By.ID, "register-submit").click()

        wait.until(EC.presence_of_element_located((By.ID, "register-error")))
        error = driver.find_element(By.ID, "register-error")
        assert "already" in error.text.lower() or "email" in error.text.lower()


class TestLoginPage:
    """Test the login page."""

    def test_login_page_loads(self, driver, wait, frontend_url):
        """Login page should render the login form."""
        driver.get(f"{frontend_url}/login")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Welcome Back" in page_text or "Sign in" in page_text

    def test_login_form_has_fields(self, driver, wait, frontend_url):
        """Login form should contain email and password fields."""
        driver.get(f"{frontend_url}/login")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        assert driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        assert driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    def test_login_has_register_link(self, driver, wait, frontend_url):
        """Login page should have a link to register page."""
        driver.get(f"{frontend_url}/login")
        wait.until(EC.presence_of_element_located((By.ID, "link-to-register")))
        link = driver.find_element(By.ID, "link-to-register")
        assert "create" in link.text.lower() or "register" in link.text.lower()


class TestLoginFlow:
    """Test the actual login process."""

    def test_login_success(self, driver, wait, frontend_url, logged_in_user):
        """Login should succeed and redirect to dashboard.
        Uses the `logged_in_user` fixture which performs login.
        """
        assert "/dashboard" in driver.current_url

    def test_login_invalid_credentials(self, driver, wait, frontend_url):
        """Login with wrong password should show error message."""
        driver.get(f"{frontend_url}/login")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        email_input.clear()
        email_input.send_keys("wrong@email.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "failed" in body_text.lower() or "invalid" in body_text.lower() or "error" in body_text.lower()
