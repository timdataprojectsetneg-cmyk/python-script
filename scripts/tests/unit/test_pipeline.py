"""Tests for the extractor pipeline / optional access resolution."""

import pytest

from ingestion import cli
from ingestion.exceptions import ConfigError, IngestionError
from ingestion.usecases import registry
from ingestion.usecases.registry import (
    available_accesses,
    default_accesses,
    resolve_extractor_class,
)


def test_default_accesses_detects_single_source_extractor():
    assert default_accesses("ketenagakerjaan", "kasus_perselisihan") == ["excel"]


def test_available_accesses_for_satudata_source():
    assert available_accesses("ketenagakerjaan", "kasus_perselisihan") == ["excel"]


def test_resolve_extractor_class_source_specific():
    cls = resolve_extractor_class("ketenagakerjaan", "kasus_perselisihan", "excel")
    assert cls.__module__.endswith("kasus_perselisihan.excel.extractor")


def test_default_accesses_missing_raises():
    with pytest.raises(ConfigError):
        default_accesses("example_usecase", "demo_source")


def test_parse_accesses_variants(monkeypatch):
    assert cli._parse_accesses("scraper,excel", "uc", "src") == ["scraper", "excel"]
    assert cli._parse_accesses(("excel",), "uc", "src") == ["excel"]
    assert cli._parse_accesses(("scraper", "excel"), "uc", "src") == ["scraper", "excel"]

    monkeypatch.setattr(registry, "default_accesses", lambda uc, src: ["excel"])
    assert cli._parse_accesses((), "uc", "src") == ["excel"]
    assert cli._parse_accesses(None, "uc", "src") == ["excel"]

    with pytest.raises(ConfigError):
        cli._parse_accesses("bogus", "uc", "src")


def test_extract_pipeline_feeds_url_forward(monkeypatch):
    class DiscoveryStep:
        def __init__(self, config):
            self.config = config

        def extract(self):
            return iter([{"url": "https://files.example.com/data.xlsx"}])

    class ExcelStep:
        def __init__(self, config):
            self.config = config

        def extract(self):
            yield {"download_url": self.config.get("download_url")}

    mapping = {"scraper": DiscoveryStep, "excel": ExcelStep}
    monkeypatch.setattr(registry, "resolve_extractor_class", lambda uc, src, access: mapping[access])

    configs = [{"url": "https://landing.example.com"}, {}]
    records = list(cli._extract("uc", "src", ["scraper", "excel"], configs))
    assert records == [{"download_url": "https://files.example.com/data.xlsx"}]


def test_extract_pipeline_missing_url_raises(monkeypatch):
    class EmptyStep:
        def __init__(self, config):
            self.config = config

        def extract(self):
            return iter([{"nothing": 1}])

    class ExcelStep:
        def __init__(self, config):
            self.config = config

        def extract(self):
            return iter([])

    mapping = {"scraper": EmptyStep, "excel": ExcelStep}
    monkeypatch.setattr(registry, "resolve_extractor_class", lambda uc, src, access: mapping[access])

    with pytest.raises(IngestionError):
        list(cli._extract("uc", "src", ["scraper", "excel"], [{}, {}]))


def test_error_location_reports_file_and_line():
    try:
        raise ValueError("boom")
    except ValueError as exc:
        location = cli.error_location(exc)

    assert "test_pipeline.py" in location
    assert "test_error_location_reports_file_and_line" in location
