"""Extractor — 6.5.1 Geothermal Resources and Reserves.

Scaffolded from the catalog Data Access 'pdf'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.pdf_extractor import PdfExtractor


class Extractor(PdfExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
