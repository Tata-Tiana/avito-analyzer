import re
from html.parser import HTMLParser
from typing import Dict, List
from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from config import SELENIUM_IMPLICIT_WAIT, SELENIUM_PAGE_LOAD_TIMEOUT


PRICE_RE = re.compile(r"(\d[\d\s]{2,}\s?(?:₽|руб\.?|рублей))", re.IGNORECASE)


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        HTMLParser.__init__(self)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            text = data.strip()
            if text:
                self.parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.parts)


class SeleniumParser:
    def __init__(self) -> None:
        self.page_load_timeout = SELENIUM_PAGE_LOAD_TIMEOUT
        self.implicit_wait = SELENIUM_IMPLICIT_WAIT
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )

    def extract_listing_data(self, url: str) -> Dict[str, str]:
        try:
            page = self._extract_with_selenium(url)
        except Exception:
            page = self._extract_with_http_fallback(url)

        title = page.get("title", "").strip()
        description = page.get("description", "").strip()
        price = page.get("price", "").strip()

        if not description:
            description = page.get("text", "").strip()

        return {
            "title": title,
            "price": price,
            "description": description,
        }

    def _build_driver(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1440,2200")
        options.add_argument("--user-agent=" + self.user_agent)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.implicitly_wait(self.implicit_wait)
        return driver

    def _extract_with_selenium(self, url: str) -> Dict[str, str]:
        driver = None
        try:
            driver = self._build_driver()
            driver.get(url)

            title = driver.title or ""
            meta_description = driver.execute_script(
                """
                var meta = document.querySelector('meta[name="description"]');
                return meta ? meta.getAttribute('content') || '' : '';
                """
            ) or ""
            page_text = driver.execute_script(
                "return document.body ? document.body.innerText || '' : '';"
            ) or ""

            return {
                "title": title,
                "price": self._extract_price(page_text),
                "description": meta_description,
                "text": page_text,
            }
        except WebDriverException as exc:
            raise RuntimeError("Selenium не смог открыть страницу.") from exc
        finally:
            if driver is not None:
                driver.quit()

    def _extract_with_http_fallback(self, url: str) -> Dict[str, str]:
        request = Request(url, headers={"User-Agent": self.user_agent})
        response = urlopen(request, timeout=self.page_load_timeout)
        html_bytes = response.read()
        html_text = html_bytes.decode("utf-8", errors="ignore")

        parser = _VisibleTextParser()
        parser.feed(html_text)
        text = parser.get_text().strip()
        title = self._extract_html_title(html_text)
        description = self._extract_meta_description(html_text)

        return {
            "title": title,
            "price": self._extract_price(text),
            "description": description,
            "text": text,
        }

    def _extract_html_title(self, html_text: str) -> str:
        match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()

    def _extract_meta_description(self, html_text: str) -> str:
        match = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            html_text,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()

    def _extract_price(self, text: str) -> str:
        match = PRICE_RE.search(text or "")
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()
