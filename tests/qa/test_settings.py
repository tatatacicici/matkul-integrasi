"""
Test Suite: Settings Page
==========================
Validates the settings/profile management page.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestSettingsPage:
    """Test the settings page."""

    def test_settings_page_loads(self, driver, wait, frontend_url, logged_in_user):
        """Settings page should render with profile form."""
        driver.get(f"{frontend_url}/settings")
        wait.until(EC.presence_of_element_located((By.ID, "settings-heading")))

        heading = driver.find_element(By.ID, "settings-heading")
        assert "Settings" in heading.text

    def test_settings_form_has_fields(self, driver, wait, frontend_url, logged_in_user):
        """Settings form should contain name, email, and password fields."""
        driver.get(f"{frontend_url}/settings")
        wait.until(EC.presence_of_element_located((By.ID, "settings-form")))

        assert driver.find_element(By.ID, "settings-name")
        assert driver.find_element(By.ID, "settings-email")
        assert driver.find_element(By.ID, "settings-password")
        assert driver.find_element(By.ID, "settings-submit")

    def test_settings_pre_filled_with_user_data(self, driver, wait, frontend_url, logged_in_user):
        """Settings form should be pre-filled with current user data."""
        driver.get(f"{frontend_url}/settings")
        wait.until(EC.presence_of_element_located((By.ID, "settings-name")))
        time.sleep(1)

        name_value = driver.find_element(By.ID, "settings-name").get_attribute("value")
        email_value = driver.find_element(By.ID, "settings-email").get_attribute("value")

        assert name_value, "Name field should be pre-filled"
        assert email_value, "Email field should be pre-filled"
        assert "@" in email_value, "Email should contain @"

    def test_update_profile(self, driver, wait, frontend_url, logged_in_user):
        """Updating profile should show success message."""
        driver.get(f"{frontend_url}/settings")
        wait.until(EC.presence_of_element_located((By.ID, "settings-form")))
        time.sleep(1)

        # Fill password (required by PATCH /users/me)
        password_input = driver.find_element(By.ID, "settings-password")
        password_input.clear()
        password_input.send_keys(logged_in_user["password"])

        # Submit
        driver.find_element(By.ID, "settings-submit").click()
        time.sleep(2)

        # Check for success message
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "success" in body_text.lower() or "updated" in body_text.lower(), \
            f"Success message not found. Body: {body_text[:200]}"


class TestSidebarNavigation:
    """Test sidebar navigation in the layout."""

    def test_sidebar_has_all_nav_items(self, driver, wait, frontend_url, logged_in_user):
        """Sidebar should contain links to Dashboard, Posts, Comments, Settings."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "aside")))

        aside = driver.find_element(By.TAG_NAME, "aside")
        nav_text = aside.text

        assert "Dashboard" in nav_text
        assert "Posts" in nav_text
        assert "Comments" in nav_text
        assert "Settings" in nav_text

    def test_sidebar_has_logout(self, driver, wait, frontend_url, logged_in_user):
        """Sidebar should have a Logout button."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "aside")))

        aside = driver.find_element(By.TAG_NAME, "aside")
        assert "Logout" in aside.text

    def test_navigate_to_posts_via_sidebar(self, driver, wait, frontend_url, logged_in_user):
        """Clicking Posts in sidebar should navigate to /posts."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "aside")))

        posts_link = driver.find_element(By.XPATH, "//aside//a[contains(., 'Posts')]")
        posts_link.click()
        time.sleep(1)
        assert "/posts" in driver.current_url

    def test_navigate_to_comments_via_sidebar(self, driver, wait, frontend_url, logged_in_user):
        """Clicking Comments in sidebar should navigate to /comments."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "aside")))

        comments_link = driver.find_element(By.XPATH, "//aside//a[contains(., 'Comments')]")
        comments_link.click()
        time.sleep(1)
        assert "/comments" in driver.current_url

    def test_navigate_to_settings_via_sidebar(self, driver, wait, frontend_url, logged_in_user):
        """Clicking Settings in sidebar should navigate to /settings."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "aside")))

        settings_link = driver.find_element(By.XPATH, "//aside//a[contains(., 'Settings')]")
        settings_link.click()
        time.sleep(1)
        assert "/settings" in driver.current_url
