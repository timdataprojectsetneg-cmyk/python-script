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


def test_declared_targets_from_config_keys():
    assert cli._declared_targets({"postgre_table": "raw_bps.x"}) == ["postgres"]
    assert cli._declared_targets({"postgre_schema": "raw_bps"}) == ["postgres"]
    assert cli._declared_targets({"es_index": "i", "minio_bucket": "b", "postgre_table": "t"}) == [
        "elastic",
        "minio",
        "postgres",
    ]
    assert cli._declared_targets({}) == []


def test_effective_targets_intersects_declared():
    requested = ["elastic", "minio", "postgres"]
    # A PostgreSQL-only source must not be pushed into Elasticsearch.
    assert cli._effective_targets(requested, ["postgres"]) == ["postgres"]
    assert cli._effective_targets(requested, ["elastic", "postgres"]) == ["elastic", "postgres"]
    # No matching sink -> no loading.
    assert cli._effective_targets(["elastic"], ["postgres"]) == ["none"]
    # Undeclared source keeps the requested sinks.
    assert cli._effective_targets(requested, []) == requested
