"""
Selenium E2E Test Configuration
================================
Shared fixtures for QA/E2E tests using Selenium WebDriver (Chrome headless).

Prerequisites:
  - Docker services running: `make up`
  - Frontend dev server running: `cd frontend && npm run dev`
  - Chrome + ChromeDriver installed on host
"""
import pytest
import time
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Configuration ────────────────────────────────────────────────────────────

API_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:5173"
WAIT_TIMEOUT = 10  # seconds


# ── WebDriver Fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def driver():
    """Create a Chrome WebDriver in headless mode for the entire test session."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def wait(driver):
    """Provide a WebDriverWait instance."""
    return WebDriverWait(driver, WAIT_TIMEOUT)


# ── Helper Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def unique_suffix():
    """Generate a unique suffix to avoid test data collisions."""
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="session")
def test_user_credentials(unique_suffix):
    """Unique user credentials for E2E tests."""
    return {
        "name": f"E2E Tester {unique_suffix}",
        "email": f"e2e_{unique_suffix}@test.com",
        "password": "testpassword123",
    }


@pytest.fixture(scope="session")
def api_url():
    """Return the API base URL."""
    return API_BASE_URL


@pytest.fixture(scope="session")
def frontend_url():
    """Return the frontend base URL."""
    return FRONTEND_BASE_URL


# ── Registration & Login Helper ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def registered_user(driver, wait, frontend_url, test_user_credentials):
    """
    Register a test user via the frontend.
    Returns the credentials dict. This runs once per session.
    """
    driver.get(f"{frontend_url}/register")
    time.sleep(1)

    driver.find_element(By.ID, "register-name").send_keys(test_user_credentials["name"])
    driver.find_element(By.ID, "register-email").send_keys(test_user_credentials["email"])
    driver.find_element(By.ID, "register-password").send_keys(test_user_credentials["password"])
    driver.find_element(By.ID, "register-submit").click()

    # Wait for success message
    wait.until(EC.presence_of_element_located((By.ID, "register-success")))
    time.sleep(2.5)  # Wait for redirect to login

    return test_user_credentials


@pytest.fixture(scope="session")
def logged_in_user(driver, wait, frontend_url, registered_user):
    """
    Log in the registered user via the frontend.
    After this fixture, the browser session is authenticated.
    """
    driver.get(f"{frontend_url}/login")
    time.sleep(1)

    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    email_input.clear()
    email_input.send_keys(registered_user["email"])
    password_input.clear()
    password_input.send_keys(registered_user["password"])

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for redirect to dashboard
    wait.until(EC.url_contains("/dashboard"))
    time.sleep(1)

    return registered_user
