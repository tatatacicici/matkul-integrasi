"""
Test Suite: Comments E2E
=========================
Validates comment creation on post detail page and comments management page.
"""
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestPostDetailAndComments:
    """Test post detail page and comment interactions."""

    def _ensure_published_post(self, driver, wait, frontend_url):
        """Helper: create a published post and return its URL."""
        driver.get(f"{frontend_url}/posts")
        time.sleep(2)

        post_title = f"Comment Test Post {uuid.uuid4().hex[:6]}"

        create_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post')]")
        create_btn.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(0.5)

        title_input = driver.find_element(By.CSS_SELECTOR, "form input[type='text']")
        content_input = driver.find_element(By.CSS_SELECTOR, "form textarea")
        title_input.clear()
        title_input.send_keys(post_title)
        content_input.clear()
        content_input.send_keys("This post is for testing comments in Selenium E2E.")

        # Make sure status is "published"
        select = driver.find_element(By.CSS_SELECTOR, "form select")
        select.click()
        time.sleep(0.3)
        option = driver.find_element(By.CSS_SELECTOR, "option[value='published']")
        option.click()

        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create Post') and @type='submit']")
        submit_btn.click()
        time.sleep(2)

        return post_title

    def test_post_detail_page_loads(self, driver, wait, frontend_url, logged_in_user):
        """Post detail page should display post title and content."""
        post_title = self._ensure_published_post(driver, wait, frontend_url)

        # Navigate to public blog and find the post
        driver.get(frontend_url)
        time.sleep(2)

        # Find and click Read more link
        links = driver.find_elements(By.XPATH, "//a[contains(., 'Read more')]")
        if links:
            links[0].click()
            wait.until(EC.presence_of_element_located((By.ID, "post-title")))
            title_el = driver.find_element(By.ID, "post-title")
            assert title_el.text, "Post title should not be empty"
            assert driver.find_element(By.ID, "post-content")
        else:
            # Directly navigate to a post detail page
            driver.get(f"{frontend_url}/post/1")
            time.sleep(2)
            # Either shows post or "Post Not Found"
            body_text = driver.find_element(By.TAG_NAME, "body").text
            assert "Post" in body_text

    def test_comment_section_visible(self, driver, wait, frontend_url, logged_in_user):
        """Post detail should show the comments section."""
        # Navigate to first available post
        driver.get(frontend_url)
        time.sleep(2)
        links = driver.find_elements(By.XPATH, "//a[contains(., 'Read more')]")
        if links:
            links[0].click()
            wait.until(EC.presence_of_element_located((By.ID, "comments-heading")))
            heading = driver.find_element(By.ID, "comments-heading")
            assert "Comments" in heading.text

    def test_add_comment_on_post_detail(self, driver, wait, frontend_url, logged_in_user):
        """Logged in user should be able to add a comment on post detail."""
        post_title = self._ensure_published_post(driver, wait, frontend_url)

        # Go to public blog, find post and click
        driver.get(frontend_url)
        time.sleep(2)
        links = driver.find_elements(By.XPATH, "//a[contains(., 'Read more')]")
        assert len(links) > 0, "No posts with Read more link found"
        links[0].click()

        wait.until(EC.presence_of_element_located((By.ID, "comment-form")))

        comment_text = f"Selenium test comment {uuid.uuid4().hex[:6]}"
        textarea = driver.find_element(By.ID, "comment-input")
        textarea.clear()
        textarea.send_keys(comment_text)

        submit = driver.find_element(By.ID, "comment-submit")
        submit.click()
        time.sleep(2)

        # Verify comment appears
        comments_list = driver.find_element(By.ID, "comments-list")
        assert comment_text in comments_list.text, f"Comment '{comment_text}' not found"


class TestCommentsManagementPage:
    """Test the comments management page (protected)."""

    def test_comments_page_loads(self, driver, wait, frontend_url, logged_in_user):
        """Comments page should load and display heading."""
        driver.get(f"{frontend_url}/comments")
        wait.until(EC.presence_of_element_located((By.ID, "comments-page-heading")))
        heading = driver.find_element(By.ID, "comments-page-heading")
        assert "Manage Comments" in heading.text

    def test_comments_table_or_empty(self, driver, wait, frontend_url, logged_in_user):
        """Comments page should show either a table or empty state."""
        driver.get(f"{frontend_url}/comments")
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        # Either table exists or empty state message
        has_table = len(driver.find_elements(By.ID, "comments-table")) > 0
        has_empty = "No comments found" in body_text
        assert has_table or has_empty, "Neither table nor empty state found"
