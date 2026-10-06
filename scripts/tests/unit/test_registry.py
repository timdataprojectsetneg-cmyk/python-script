"""Unit tests for the use case registry and normalizers."""

from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.exceptions import ConfigError
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer


def test_resolve_source_extractor_class():
    cls = resolve_extractor_class("example_usecase", "example_publisher", "example_source")
    assert issubclass(cls, ExcelExtractor)
    assert cls.__module__.endswith("example_source.extractor")


def test_resolve_missing_extractor_raises():
    try:
        resolve_extractor_class("example_usecase", "example_publisher", "demo_source")
    except ConfigError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ConfigError")


def test_normalizer_uses_source_record_model():
    normalizer = resolve_normalizer("example_usecase", "example_publisher", "example_source", {})
    out = list(normalizer.normalize(iter([{"id": 1, "name": "a", "period": "2026-07"}])))
    assert out == [{"id": 1, "name": "a", "value": None, "period": "2026-07"}]
