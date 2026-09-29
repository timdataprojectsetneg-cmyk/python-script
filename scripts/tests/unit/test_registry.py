"""Unit tests for the use case registry and normalizers."""

from ingestion.usecases.registry import normalize_access, resolve_extractor, resolve_normalizer
from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.core.extractors.pdf_extractor import PdfExtractor


def test_access_alias():
    assert normalize_access("web") == "scraper"
    assert normalize_access("excel") == "excel"


def test_generic_extractor_fallback():
    cfg = {"usecase": "example_usecase", "source": "unknown_source", "access": "excel", "url": "u"}
    extractor = resolve_extractor("example_usecase", "unknown_source", "excel", cfg)
    assert isinstance(extractor, ExcelExtractor)


def test_pdf_extractor_fallback():
    cfg = {"usecase": "example_usecase", "source": "unknown_source", "access": "pdf", "url": "u"}
    extractor = resolve_extractor("example_usecase", "unknown_source", "pdf", cfg)
    assert isinstance(extractor, PdfExtractor)


def test_generic_normalizer_uses_record_model():
    normalizer = resolve_normalizer("example_usecase", "unknown_source", {})
    out = list(normalizer.normalize(iter([{"id": 1, "name": "a", "period": "2026-07"}])))
    assert out == [{"id": 1, "name": "a", "value": None, "period": "2026-07"}]
