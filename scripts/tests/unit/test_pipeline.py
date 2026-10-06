"""Tests for the extractor pipeline."""

import pytest

from ingestion import cli
from ingestion.exceptions import ConfigError
from ingestion.usecases.registry import resolve_extractor_class


def test_resolve_extractor_class_source_specific():
    cls = resolve_extractor_class("ketenagakerjaan", "kemnaker", "kasus_perselisihan")
    assert cls.__module__.endswith("kasus_perselisihan.extractor")


def test_resolve_extractor_class_missing_raises():
    with pytest.raises(ConfigError):
        resolve_extractor_class("example_usecase", "example_publisher", "demo_source")


def test_extract_delegates_to_source_extractor(monkeypatch):
    class Step:
        def __init__(self, config):
            self.config = config

        def extract(self):
            return iter([{"url": self.config.get("url")}])

    monkeypatch.setattr(cli, "resolve_extractor_class", lambda *a, **k: Step)
    records = list(cli._extract("uc", "pub", "src", {"url": "https://x"}))
    assert records == [{"url": "https://x"}]


def test_error_location_reports_file_and_line():
    try:
        raise ValueError("boom")
    except ValueError as exc:
        location = cli.error_location(exc)

    assert "test_pipeline.py" in location
    assert "test_error_location_reports_file_and_line" in location
