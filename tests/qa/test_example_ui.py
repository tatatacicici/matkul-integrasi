"""
QA Testing dengan Selenium
===========================
Test ini menargetkan Backend API (localhost:8000) yang berjalan via Docker.
Tidak membutuhkan frontend — cukup `make up` saja.

Jalankan:
    .venv/bin/pytest tests/qa/ -v
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def driver():
    """Set up Chrome WebDriver dalam mode headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


# ── Landing Page Tests ────────────────────────────────────────────────────────

class TestLandingPage:
    """Test halaman utama API (GET /)."""

    def test_landing_page_loads(self, driver):
        """Halaman utama harus bisa diakses tanpa error."""
        driver.get(f"{BASE_URL}/")
        assert "Blog" in driver.title or "API" in driver.title

    def test_landing_page_has_heading(self, driver):
        """Halaman harus menampilkan heading Blog API."""
        driver.get(f"{BASE_URL}/")
        h1 = driver.find_element(By.TAG_NAME, "h1")
        assert "Blog API" in h1.get_attribute("textContent")

    def test_landing_page_has_swagger_link(self, driver):
        """Harus ada link menuju Swagger UI (/docs)."""
        driver.get(f"{BASE_URL}/")
        links = driver.find_elements(By.TAG_NAME, "a")
        swagger_link = [a for a in links if "/docs" in (a.get_attribute("href") or "")]
        assert len(swagger_link) > 0, "Link ke Swagger UI tidak ditemukan"

    def test_landing_page_has_redoc_link(self, driver):
        """Harus ada link menuju ReDoc (/redoc)."""
        driver.get(f"{BASE_URL}/")
        links = driver.find_elements(By.TAG_NAME, "a")
        redoc_link = [a for a in links if "/redoc" in (a.get_attribute("href") or "")]
        assert len(redoc_link) > 0, "Link ke ReDoc tidak ditemukan"

    def test_landing_page_shows_version_badge(self, driver):
        """Halaman harus menampilkan badge versi v2.0.0."""
        driver.get(f"{BASE_URL}/")
        badges = driver.find_elements(By.CLASS_NAME, "badge")
        badge_texts = [b.get_attribute("textContent") for b in badges]
        assert any("v2.0.0" in t for t in badge_texts), f"Badge versi tidak ditemukan. Badge: {badge_texts}"


# ── Swagger UI Tests ─────────────────────────────────────────────────────────

class TestSwaggerUI:
    """Test Swagger UI (/docs)."""

    def test_swagger_page_loads(self, driver):
        """Swagger UI harus bisa diakses."""
        driver.get(f"{BASE_URL}/docs")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swagger-ui")))

    def test_swagger_shows_api_title(self, driver):
        """Swagger harus menampilkan judul 'Blog REST API'."""
        driver.get(f"{BASE_URL}/docs")
        wait = WebDriverWait(driver, 10)
        title_el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".swagger-ui .title"))
        )
        assert "Blog REST API" in title_el.text

    def test_swagger_has_auth_section(self, driver):
        """Swagger harus memiliki section Auth."""
        driver.get(f"{BASE_URL}/docs")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swagger-ui")))
        page_source = driver.page_source
        assert "Auth" in page_source, "Section Auth tidak ditemukan di Swagger UI"

    def test_swagger_has_posts_section(self, driver):
        """Swagger harus memiliki section Posts."""
        driver.get(f"{BASE_URL}/docs")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swagger-ui")))
        page_source = driver.page_source
        assert "Posts" in page_source, "Section Posts tidak ditemukan di Swagger UI"


# ── API Endpoint Tests via Browser ────────────────────────────────────────────

class TestAPIEndpoints:
    """Test API endpoints langsung lewat browser (JSON response)."""

    def test_get_posts_returns_json(self, driver):
        """GET /api/v1/posts/ harus mengembalikan JSON valid."""
        driver.get(f"{BASE_URL}/api/v1/posts/")
        body = driver.find_element(By.TAG_NAME, "body").text
        # Response harus mengandung field "data" dan "meta"
        assert "data" in body, f"Response tidak mengandung 'data': {body[:200]}"
        assert "meta" in body, f"Response tidak mengandung 'meta': {body[:200]}"

    def test_get_posts_has_pagination_meta(self, driver):
        """Response posts harus memiliki pagination meta (total, page, dll)."""
        driver.get(f"{BASE_URL}/api/v1/posts/")
        body = driver.find_element(By.TAG_NAME, "body").text
        assert "total" in body
        assert "page" in body
        assert "page_size" in body

    def test_nonexistent_post_returns_404(self, driver):
        """GET /api/v1/posts/999999 harus mengembalikan error 'not found'."""
        driver.get(f"{BASE_URL}/api/v1/posts/999999")
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "not found" in body, f"Expected 'not found' in response: {body[:200]}"

    def test_openapi_json_accessible(self, driver):
        """OpenAPI spec (/openapi.json) harus bisa diakses."""
        driver.get(f"{BASE_URL}/openapi.json")
        body = driver.find_element(By.TAG_NAME, "body").text
        assert "Blog REST API" in body
        assert "paths" in body


# ── Security Header Tests ─────────────────────────────────────────────────────

class TestSecurityHeaders:
    """Test security headers via Selenium + JavaScript execution."""

    def _get_response_header(self, driver, url, header_name):
        """Helper: fetch URL via JS XMLHttpRequest dan ambil response header."""
        driver.get(f"{BASE_URL}/")
        script = f"""
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '{url}', false);
        xhr.send();
        return xhr.getResponseHeader('{header_name}');
        """
        return driver.execute_script(script)

    def test_x_content_type_options(self, driver):
        """Response harus memiliki header X-Content-Type-Options: nosniff."""
        value = self._get_response_header(driver, f"{BASE_URL}/api/v1/posts/", "X-Content-Type-Options")
        assert value == "nosniff", f"Expected 'nosniff', got '{value}'"

    def test_x_frame_options(self, driver):
        """Response harus memiliki header X-Frame-Options: DENY."""
        value = self._get_response_header(driver, f"{BASE_URL}/api/v1/posts/", "X-Frame-Options")
        assert value == "DENY", f"Expected 'DENY', got '{value}'"

    def test_cache_control(self, driver):
        """Response harus memiliki header Cache-Control: no-store."""
        value = self._get_response_header(driver, f"{BASE_URL}/api/v1/posts/", "Cache-Control")
        assert value == "no-store", f"Expected 'no-store', got '{value}'"
