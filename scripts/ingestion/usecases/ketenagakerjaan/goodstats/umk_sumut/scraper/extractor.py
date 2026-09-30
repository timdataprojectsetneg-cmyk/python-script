"""Web scraping access — UMK Sumatera Utara (data.goodstats.id).

Parsing follows ``umk_2026.py``: scope the article body (``div.statistic-content``),
read the ordered list (``ol li``) and match ``"<kabupaten/kota>: Rp<nilai>"``::

    Kota Medan: Rp4.335.198
    Kabupaten Deli Serdang: Rp4.041.543

This extractor uses a normal HTTP request and parses the returned HTML with
BeautifulSoup/lxml. It also accepts a saved page via ``SOURCE_FILE`` for
networks where goodstats.id returns a Cloudflare challenge.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterator, List

import requests
from bs4 import BeautifulSoup

from ......exceptions import ConfigError, SourceUnavailable
from ......core.base.extractor import BaseExtractor

DEFAULT_ITEM_SELECTOR = "div.statistic-content"
DEFAULT_LIST_SELECTOR = "ol li"

# "Kota Medan: Rp4.335.198" -> nama="Kota Medan", nilai="4.335.198"
ITEM_RE = re.compile(r"^(?P<nama>.+?):\s*Rp\s*(?P<nilai>[\d.]+)\s*$")

REQUEST_HEADERS = {"Accept-Language": "id-ID,id;q=0.9,en;q=0.8"}

CHALLENGE_MARKERS = (
    "Performing security verification",
    "Melakukan verifikasi keamanan",
    "Tunggu sebentar",
    "challenges.cloudflare.com",
    "cdn-cgi/challenge-platform",
    "Attention Required!",
    "Just a moment",
)


class Extractor(BaseExtractor):
    """Scrape kabupaten/kota UMK amounts from the goodstats statistic page."""

    def extract(self) -> Iterator[Dict[str, Any]]:
        html = self._load_html()
        if self._is_challenge(html):
            raise SourceUnavailable(
                "goodstats.id returned a Cloudflare challenge (bot protection).\n"
                "Save the page and run offline, e.g.:\n"
                "  KETENAGAKERJAAN__GOODSTATS__UMK_SUMUT__SCRAPER__SOURCE_FILE=./data/umk_sumut.html"
            )
        rows = self._parse_html(html)
        if not rows:
            raise SourceUnavailable(
                "Daftar UMK tidak ditemukan "
                f"({self._item_selector()} / {DEFAULT_LIST_SELECTOR})."
            )
        for row in rows:
            yield row

    def _load_html(self) -> str:
        source_file = self.config.get("source_file") or self.config.get("html_path")
        if source_file:
            path = Path(str(source_file))
            if not path.exists():
                raise ConfigError(f"SOURCE_FILE not found: {path}")
            return path.read_text(encoding="utf-8", errors="ignore")

        try:
            response = requests.get(
                self.url,
                headers={**REQUEST_HEADERS, "User-Agent": self._user_agent()},
                timeout=30,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            raise SourceUnavailable(
                f"Could not fetch {self.url} ({exc}). goodstats.id is behind Cloudflare "
                "bot protection, so automated fetching may be blocked.\n"
                "Options:\n"
                "  Save the page (browser: Save as) and run offline, e.g.:\n"
                "  KETENAGAKERJAAN__GOODSTATS__UMK_SUMUT__SCRAPER__SOURCE_FILE=./data/umk_sumut.html"
            ) from exc

    def _user_agent(self) -> str:
        return str(self.config.get("user_agent") or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))

    def _item_selector(self) -> str:
        return str(self.config.get("item_selector") or DEFAULT_ITEM_SELECTOR)

    @staticmethod
    def _is_challenge(html: str) -> bool:
        return any(marker in html for marker in CHALLENGE_MARKERS)

    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")

        content = soup.select_one(self._item_selector())
        if content is None:
            return []
        return self._parse_items(content)

    @staticmethod
    def _parse_items(content: Any) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for item in content.select(DEFAULT_LIST_SELECTOR):
            match = ITEM_RE.match(item.get_text(strip=True))
            if not match:
                continue
            rows.append(
                {
                    "kabupaten_kota": match.group("nama").strip(),
                    "umk_2026": int(match.group("nilai").replace(".", "")),
                }
            )
        return rows
