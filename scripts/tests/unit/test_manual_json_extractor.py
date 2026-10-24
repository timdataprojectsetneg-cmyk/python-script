"""Tests for manually curated JSON sources (local file and S3 references)."""

from __future__ import annotations

import json

import pytest

from ingestion.config import load_config
from ingestion.core.extractors.duckdb_extractor import (
    S3,
    DuckDBJSONExtractor,
    resolve_location,
)
from ingestion.exceptions import ConfigError

SAMPLE = [
    {"tahun": 2025, "produk": "Crude Oil", "komponen": "Production", "nilai": 221.2, "satuan": "Million Barrel", "pertumbuhan_yoy_persen": None},
    {"tahun": 2025, "produk": "Crude Oil", "komponen": "Export", "nilai": 22.5, "satuan": "Million Barrel", "pertumbuhan_yoy_persen": -17.2},
    {"tahun": 2025, "produk": "Oil Fuel", "komponen": "Production", "nilai": 364591.6, "satuan": "Thousand Barrel", "pertumbuhan_yoy_persen": None},
]


def _write(tmp_path, payload):
    path = tmp_path / "manual.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_manual_json_local_array(tmp_path):
    path = _write(tmp_path, SAMPLE)

    rows = list(DuckDBJSONExtractor({"url": str(path)}).extract())

    assert rows == SAMPLE
    assert rows[0]["pertumbuhan_yoy_persen"] is None
    assert rows[1]["pertumbuhan_yoy_persen"] == -17.2
    assert isinstance(rows[2]["nilai"], float)


def test_manual_json_wrapped_root(tmp_path):
    path = _write(tmp_path, {"data": SAMPLE[:2]})

    rows = list(DuckDBJSONExtractor({"url": str(path), "root": "data"}).extract())

    assert len(rows) == 2
    assert rows[1]["komponen"] == "Export"


def test_manual_json_file_uri(tmp_path):
    path = _write(tmp_path, SAMPLE)
    location = resolve_location(path.as_uri())
    assert location.kind == "local"

    rows = list(DuckDBJSONExtractor({"url": path.as_uri()}).extract())
    assert len(rows) == len(SAMPLE)


def test_manual_json_s3_and_minio_are_s3_locations():
    s3 = resolve_location("s3://raw-ketahanan-energi/manual/oil_balance.json")
    minio = resolve_location("minio://raw-ketahanan-energi/manual/oil_balance.json")

    assert s3.kind == S3
    assert s3.uri == "s3://raw-ketahanan-energi/manual/oil_balance.json"
    assert minio.kind == S3
    assert minio.uri == "s3://raw-ketahanan-energi/manual/oil_balance.json"


def test_manual_json_missing_local_file_raises():
    with pytest.raises(ConfigError, match="not found"):
        resolve_location("/no/such/manual/oil_balance.json")


def test_manual_json_url_comes_from_the_resource_url_env_key(monkeypatch, tmp_path):
    path = _write(tmp_path, SAMPLE)
    monkeypatch.setenv("DEMO__PUB__SRC__URL", str(path))

    config = load_config("demo", "pub", "src", require_url=False)
    rows = list(DuckDBJSONExtractor(config).extract())

    assert config["url"] == str(path)
    assert len(rows) == len(SAMPLE)
