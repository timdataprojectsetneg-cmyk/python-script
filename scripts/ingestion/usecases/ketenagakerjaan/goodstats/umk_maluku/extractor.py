"""Scraper access — UMK Maluku."""

from __future__ import annotations

from .....core.extractors.web_scraper import WebScraper


class Extractor(WebScraper):
    """Implemented per source; falls back to the generic scraper extractor."""
