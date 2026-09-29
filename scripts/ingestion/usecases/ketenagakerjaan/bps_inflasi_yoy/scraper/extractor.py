"""Web scraping access — BPS Inflasi YoY press release."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterator

from bs4 import BeautifulSoup

from .....core.extractors.web_scraper import WebScraper

MONTHS = {
    "januari": "01", "februari": "02", "maret": "03", "april": "04",
    "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
    "september": "09", "oktober": "10", "november": "11", "desember": "12",
}


class Extractor(WebScraper):
    """Extracts the YoY inflation headline value from a BPS press release."""

    def _parse(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.get_text(separator=" ", strip=True).split())

        value = None
        match = re.search(
            r"inflasi\s+year\s+on\s+year[^.]*?sebesar\s+([\d.,]+)\s*persen",
            text,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(r"sebesar\s+([\d.,]+)\s*persen", text, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(".", "").replace(",", "."))

        period = None
        month_match = re.search(
            r"(?:pada|bulan)\s+(" + "|".join(MONTHS) + r")\s+(\d{4})", text, re.IGNORECASE
        )
        if month_match:
            period = f"{month_match.group(2)}-{MONTHS[month_match.group(1).lower()]}"

        return {
            "period": period,
            "Inflasi_YoY": value,
            "headline": text[:500],
            "source_url": self.url,
        }

    def extract(self) -> Iterator[Dict[str, Any]]:
        resp = self.http.get(self.url, timeout=60)
        yield self._parse(resp.text)
