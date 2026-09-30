"""Pdf access — Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)."""

from __future__ import annotations

from ......core.extractors.pdf_extractor import PdfExtractor


class Extractor(PdfExtractor):
    """Implemented per source; falls back to the generic pdf extractor."""
