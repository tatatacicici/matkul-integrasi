"""
Test Suite: Frontend Public Blog
=================================
Validates the public-facing blog pages rendered by the React frontend.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestPublicBlogPage:
    """Test the public blog homepage."""

    def test_public_blog_loads(self, driver, wait, frontend_url):
        """Homepage should load and display the blog brand."""
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "IntegrasiBlog" in page_text

    def test_hero_section_heading(self, driver, wait, frontend_url):
        """Homepage should display the hero section heading."""
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1 = driver.find_element(By.TAG_NAME, "h1")
        assert "Insights" in h1.text or "Stories" in h1.text

    def test_hero_section_description(self, driver, frontend_url):
        """Homepage should display a description paragraph."""
        driver.get(frontend_url)
        time.sleep(1)
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        descriptions = [p.text for p in paragraphs]
        assert any("articles" in d.lower() or "tutorials" in d.lower() for d in descriptions)

    def test_navbar_sign_in_link(self, driver, wait, frontend_url):
        """Navbar should show a Sign In link when not logged in."""
        # Temporarily clear auth
        driver.get(frontend_url)
        token = driver.execute_script("return localStorage.getItem('token');")
        if token:
            driver.execute_script("localStorage.removeItem('token');")
        
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
        time.sleep(1)

        nav = driver.find_element(By.TAG_NAME, "nav")
        assert "Sign In" in nav.text
        
        # Restore auth
        if token:
            driver.execute_script(f"localStorage.setItem('token', '{token}');")

    def test_navbar_dashboard_button(self, driver, wait, frontend_url):
        """Navbar should have a Dashboard button/link."""
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
        nav = driver.find_element(By.TAG_NAME, "nav")
        assert "Dashboard" in nav.text

    def test_latest_articles_section(self, driver, wait, frontend_url):
        """Homepage should display a 'Latest Articles' section heading."""
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
        headings = driver.find_elements(By.TAG_NAME, "h2")
        heading_texts = [h.text for h in headings]
        assert any("Latest Articles" in t for t in heading_texts)

    def test_footer_present(self, driver, wait, frontend_url):
        """Homepage should have a footer with copyright."""
        driver.get(frontend_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
        footer = driver.find_element(By.TAG_NAME, "footer")
        assert "IntegrasiBlog" in footer.text
        assert "©" in footer.text or "rights" in footer.text.lower()
