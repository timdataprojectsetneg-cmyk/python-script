"""Extractor — BPH Migas – BPH Migas Pastikan Pasokan dan Penyaluran BBM Terjaga dengan Baik.

Scaffolded from the catalog Data Access 'scraper'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.web_scraper import WebScraper


class Extractor(WebScraper):
    """Implemented per source; subclass the generic base and override as needed."""
