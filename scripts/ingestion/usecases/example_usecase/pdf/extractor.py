"""PDF access for the example use case: download → MinIO/S3 on-prem."""

from __future__ import annotations

from ....core.extractors.pdf_extractor import PdfExtractor


class Extractor(PdfExtractor):
    """Downloads the PDF and uploads it to object storage; yields metadata."""
