"""Web scraping access — Signal Ketenagakerjaan (the-signal.id)."""

from __future__ import annotations

from ......core.extractors.web_scraper import WebScraper


class Extractor(WebScraper):
    """ITEM_SELECTOR + FIELDS (JSON) drive the article list extraction."""
