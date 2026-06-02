"""
Test Suite: Posts CRUD via Frontend
====================================
Validates creating, editing, and deleting posts through the React UI.
Requires authenticated session (uses `logged_in_user` fixture).
"""
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestDashboard:
    """Test the authenticated dashboard page."""

    def test_dashboard_shows_welcome(self, driver, wait, frontend_url, logged_in_user):
        """Dashboard should display welcome message with user name."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
        time.sleep(1)

        h2s = driver.find_elements(By.TAG_NAME, "h2")
        h2_texts = [h.text for h in h2s]
        assert any("Welcome back" in t for t in h2_texts), f"Welcome heading not found. H2s: {h2_texts}"

    def test_dashboard_stats_grid(self, driver, wait, frontend_url, logged_in_user):
        """Dashboard should show stats cards."""
        driver.get(f"{frontend_url}/dashboard")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
        time.sleep(1)

        h3s = driver.find_elements(By.TAG_NAME, "h3")
        h3_texts = [h.text for h in h3s]
        assert any("Total Posts" in t for t in h3_texts), f"Stats not found. H3s: {h3_texts}"

    def test_dashboard_recent_posts_section(self, driver, wait, frontend_url, logged_in_user):
        """Dashboard should have a 'Recent Posts' section."""
        driver.get(f"{frontend_url}/dashboard")
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Recent Posts" in body_text or "No posts found" in body_text


class TestPostsCRUD:
    """Test full CRUD lifecycle for posts."""

    def test_posts_page_loads(self, driver, wait, frontend_url, logged_in_user):
        """Posts management page should render."""
        driver.get(f"{frontend_url}/posts")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

        h2s = driver.find_elements(By.TAG_NAME, "h2")
        assert any("Manage Posts" in h.text for h in h2s)

    def test_create_post(self, driver, wait, frontend_url, logged_in_user):
        """Creating a post through the modal should add it to the table."""
        driver.get(f"{frontend_url}/posts")
        time.sleep(2)

        post_title = f"Selenium Test Post {uuid.uuid4().hex[:6]}"

        # Click Create Post button
        create_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post')]")
        create_btn.click()

        # Wait for modal
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(0.5)

        # Fill form
        title_input = driver.find_element(By.CSS_SELECTOR, "form input[type='text']")
        content_input = driver.find_element(By.CSS_SELECTOR, "form textarea")

        title_input.clear()
        title_input.send_keys(post_title)
        content_input.clear()
        content_input.send_keys("This is automated test content from Selenium E2E test.")

        # Submit
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post') and @type='submit']")
        submit_btn.click()
        time.sleep(2)

        # Verify post appears in table
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert post_title in body_text, f"Created post '{post_title}' not found in page"

    def test_edit_post(self, driver, wait, frontend_url, logged_in_user):
        """Editing a post should update its title in the table."""
        driver.get(f"{frontend_url}/posts")
        time.sleep(2)

        # Create a post specifically for editing to guarantee ownership
        post_title = f"To Edit {uuid.uuid4().hex[:6]}"
        create_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post')]")
        create_btn.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(0.5)

        title_input = driver.find_element(By.CSS_SELECTOR, "form input[type='text']")
        content_input = driver.find_element(By.CSS_SELECTOR, "form textarea")
        title_input.clear()
        title_input.send_keys(post_title)
        content_input.clear()
        content_input.send_keys("Post to be edited by Selenium test.")

        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post') and @type='submit']")
        submit_btn.click()
        time.sleep(2)

        # Now find the row for this post and click its edit button
        row = driver.find_element(By.XPATH, f"//tr[contains(., '{post_title}')]")
        edit_btn = row.find_element(By.CSS_SELECTOR, "button[title='Edit']")
        edit_btn.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(0.5)

        updated_title = f"Updated Title {uuid.uuid4().hex[:6]}"

        # Update title
        title_input = driver.find_element(By.CSS_SELECTOR, "form input[type='text']")
        title_input.clear()
        title_input.send_keys(updated_title)

        # Submit
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Update Post')]")
        submit_btn.click()
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert updated_title in body_text, f"Updated title '{updated_title}' not found"

    def test_delete_post(self, driver, wait, frontend_url, logged_in_user):
        """Deleting a post should remove it from the table."""
        # First create a post to delete
        driver.get(f"{frontend_url}/posts")
        time.sleep(2)

        post_title = f"To Delete {uuid.uuid4().hex[:6]}"

        create_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post')]")
        create_btn.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(0.5)

        title_input = driver.find_element(By.CSS_SELECTOR, "form input[type='text']")
        content_input = driver.find_element(By.CSS_SELECTOR, "form textarea")
        title_input.clear()
        title_input.send_keys(post_title)
        content_input.clear()
        content_input.send_keys("Post to be deleted by Selenium test.")

        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post') and @type='submit']")
        submit_btn.click()
        time.sleep(2)

        # Verify created
        assert post_title in driver.find_element(By.TAG_NAME, "body").text

        # Find and click the delete button for this post
        # Accept the confirm dialog
        driver.execute_script("window.confirm = function() { return true; };")

        # Find the specific row for this post and click its delete button
        row = driver.find_element(By.XPATH, f"//tr[contains(., '{post_title}')]")
        delete_btn = row.find_element(By.CSS_SELECTOR, "button[title='Delete']")
        delete_btn.click()
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert post_title not in body_text, f"Deleted post '{post_title}' still visible"
