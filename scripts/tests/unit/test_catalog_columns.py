"""Tests for the catalog column dictionary and its sheet validation."""

from ingestion.catalog.metadata_parser import (
    CATALOG_COLUMNS,
    CATALOG_COLUMN_SPEC,
    parse_catalog_row,
    validate_catalog_columns,
)

FULL_HEADER = [entry["column"] for entry in CATALOG_COLUMN_SPEC]


def test_dictionary_flags_required_and_optional():
    spec = {entry["column"]: entry["required"] for entry in CATALOG_COLUMN_SPEC}
    assert spec["Source Name"] is True
    assert spec["Page"] is False
    assert spec["Raw Scheduler"] is False
    assert spec["Cleaned Scheduler"] is False


def test_full_header_has_no_missing_or_unknown():
    assert validate_catalog_columns(FULL_HEADER) == ([], [])


def test_optional_column_may_be_absent():
    headers = [header for header in FULL_HEADER if header != "Page"]
    missing, unknown = validate_catalog_columns(headers)
    assert missing == []
    assert unknown == []


def test_missing_required_column_is_reported():
    headers = [header for header in FULL_HEADER if header != "Publisher"]
    missing, _ = validate_catalog_columns(headers)
    assert missing == ["Publisher"]


def test_unknown_column_is_reported():
    missing, unknown = validate_catalog_columns([*FULL_HEADER, "Catatan Baru"])
    assert missing == []
    assert unknown == ["Catatan Baru"]


def test_multiline_eligible_header_matches():
    headers = [
        "Eligible\n(Layak untuk diambil datanya)" if header == "Eligible" else header
        for header in FULL_HEADER
    ]
    assert validate_catalog_columns(headers) == ([], [])


def test_dictionary_drives_row_parsing():
    assert CATALOG_COLUMNS["source_name"][0] == "Source Name"
    assert "Raw Minio" in CATALOG_COLUMNS["raw_minio_bucket"]
    source = parse_catalog_row(
        {
            "Source Name": "Kasus Perselisihan",
            "Publisher": "Kemnaker",
            "Data Access": "Download Excel",
            "Source Link": "https://example.org/a",
            "Raw Minio (Bucket)": "raw-kemnaker",
            "Eligible\n(Layak untuk diambil datanya)": True,
        }
    )
    assert source["raw_minio_bucket"] == "raw-kemnaker"
    assert source["minio_bucket"] == "raw-kemnaker"
    assert source["eligible"] is True
