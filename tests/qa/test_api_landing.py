"""
Test Suite: API Landing Page & Documentation
=============================================
Validates the FastAPI backend landing page, Swagger UI,
ReDoc, and HTTP security headers.
"""
import time
import httpx
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def _get_text(element):
    """Get text content from element, fallback to textContent attribute."""
    text = element.text
    if not text:
        text = element.get_attribute("textContent") or ""
    return text


class TestAPILandingPage:
    """Test the API root landing page."""

    def test_api_landing_page_loads(self, driver, wait, api_url):
        """GET / should display the Blog API landing page."""
        driver.get(api_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(1)

        page_source = driver.page_source
        assert "Blog API" in page_source, f"'Blog API' not found in page source"

    def test_api_landing_has_swagger_link(self, driver, api_url):
        """Landing page should contain a link to Swagger UI (/docs)."""
        driver.get(api_url)
        time.sleep(1)
        links = driver.find_elements(By.TAG_NAME, "a")
        swagger_links = [l for l in links if "/docs" in (l.get_attribute("href") or "")]
        assert len(swagger_links) > 0, "No link to /docs found on landing page"

    def test_api_landing_has_redoc_link(self, driver, api_url):
        """Landing page should contain a link to ReDoc (/redoc)."""
        driver.get(api_url)
        time.sleep(1)
        links = driver.find_elements(By.TAG_NAME, "a")
        redoc_links = [l for l in links if "/redoc" in (l.get_attribute("href") or "")]
        assert len(redoc_links) > 0, "No link to /redoc found on landing page"

    def test_api_landing_has_version_badge(self, driver, api_url):
        """Landing page should show version badge."""
        driver.get(api_url)
        time.sleep(1)
        page_source = driver.page_source
        assert "v2.0.0" in page_source, "Version badge v2.0.0 not found in page"


class TestSwaggerDocs:
    """Test Swagger UI documentation page."""

    def test_swagger_docs_accessible(self, driver, wait, api_url):
        """GET /docs should load Swagger UI."""
        driver.get(f"{api_url}/docs")
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".swagger-ui, #swagger-ui")
        ))
        page_source = driver.page_source
        assert "swagger" in page_source.lower() or "Blog" in page_source

    def test_swagger_has_endpoints(self, driver, wait, api_url):
        """Swagger UI should show API endpoint operations."""
        driver.get(f"{api_url}/docs")
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".opblock")
        ))
        operations = driver.find_elements(By.CSS_SELECTOR, ".opblock")
        assert len(operations) > 0, "No API operations found in Swagger UI"


class TestReDoc:
    """Test ReDoc documentation page."""

    def test_redoc_accessible(self, driver, wait, api_url):
        """GET /redoc should load ReDoc page."""
        driver.get(f"{api_url}/redoc")
        time.sleep(3)  # ReDoc takes time to load from CDN
        page_source = driver.page_source
        assert "Blog REST API" in page_source or "redoc" in page_source.lower()


class TestSecurityHeaders:
    """Test HTTP security headers using httpx (no browser needed)."""

    def test_x_content_type_options(self, api_url):
        """Response should include X-Content-Type-Options: nosniff."""
        r = httpx.get(api_url)
        assert r.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, api_url):
        """Response should include X-Frame-Options: DENY."""
        r = httpx.get(api_url)
        assert r.headers.get("x-frame-options") == "DENY"

    def test_x_xss_protection(self, api_url):
        """Response should include X-XSS-Protection."""
        r = httpx.get(api_url)
        assert r.headers.get("x-xss-protection") == "1; mode=block"

    def test_strict_transport_security(self, api_url):
        """Response should include Strict-Transport-Security."""
        r = httpx.get(api_url)
        assert "max-age" in r.headers.get("strict-transport-security", "")

    def test_cache_control_no_store(self, api_url):
        """Response should include Cache-Control: no-store."""
        r = httpx.get(api_url)
        assert r.headers.get("cache-control") == "no-store"
