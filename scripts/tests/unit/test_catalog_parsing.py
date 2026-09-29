"""Tests for catalog sheet header detection, parsing and filtering."""

from ingestion.sharepoint.client import SharePointClient
from ingestion.sharepoint.metadata_parser import (
    derive_module_name,
    is_eligible,
    is_source_row,
    parse_catalog_row,
    source_slug,
)


def test_matrix_locates_header_and_skips_title_rows():
    client = SharePointClient()
    matrix = [
        ["AVAILABLE DATA KETENAGAKERJAAN", None, None],
        [None, None, None],
        ["No", "Source Name", "Publisher"],
        [None, None, None],
        [1, "Kasus Perselisihan", "Kemnaker"],
        [2, "Data Mogok Kerja", "Kemnaker"],
    ]
    records = client._matrix_to_records(matrix, ["Source Name"])
    assert len(records) == 2
    assert records[0]["Source Name"] == "Kasus Perselisihan"
    assert records[0]["No"] == 1


def test_matrix_merges_two_row_header():
    client = SharePointClient()
    matrix = [
        ["No", "Source Name", "Data Engineer", None],
        [None, None, "Raw Data", "Raw Minio (Bucket)"],
        [1, "Kasus Perselisihan", False, "bucket-1"],
    ]
    records = client._matrix_to_records(matrix, ["Source Name"])
    assert len(records) == 1
    assert records[0]["Source Name"] == "Kasus Perselisihan"
    assert records[0]["Data Engineer"] is False
    assert records[0]["Raw Minio (Bucket)"] == "bucket-1"


def test_parse_catalog_row_and_filter():
    row = {
        "No": 2,
        "Source Name": "Kasus Perselisihan",
        "Publisher": "Kemnaker",
        "Data Dictionary": "DD.xlsx",
        "Source Link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
        "Is Official": "Yes",
        "Data Access": "Download Excel",
        "Update Frequency": "Monthly",
        "Last Update": "Juli 2026",
        "Eligible\n(Layak untuk diambil datanya)": True,
    }
    source = parse_catalog_row(row)
    assert source["source_name"] == "Kasus Perselisihan"
    assert source["data_access"] == "Download Excel"
    assert source["is_official"] == "Yes"
    assert source["eligible"] is True
    assert source["last_update"] == "Juli 2026"
    assert is_source_row(source)


def test_section_title_is_not_a_source():
    assert not is_source_row(parse_catalog_row({"Source Name": "Kategori per Data Kemnaker"}))
    assert not is_source_row({"source_name": None, "source_link": None})


def test_data_dictionary_hyperlink_captured():
    row = {
        "Source Name": "Kasus Perselisihan",
        "Data Dictionary": "DD.xlsx",
        "Source Link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
        "Data Access": "Download Excel",
        "_links": {
            "Data Dictionary": "https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/DD.xlsx",
        },
    }
    source = parse_catalog_row(row)
    assert source["data_dictionary_link"] == (
        "https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/DD.xlsx"
    )


def test_eligibility_variants():
    assert is_eligible({"eligible": True})
    assert is_eligible({"eligible": "Yes"})
    assert is_eligible({"eligible": "true"})
    assert not is_eligible({"eligible": False})
    assert not is_eligible({"eligible": "No"})
    assert not is_eligible({})


def test_long_name_slug_and_override():
    long_name = "Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)"
    slug = derive_module_name(long_name)
    assert "mahkamah" not in slug  # parenthetical dropped
    assert len(slug) <= 48
    assert slug == slug.strip("_")

    overridden = source_slug({"source_name": long_name, "module_name": "putusan_phi"})
    assert overridden == "putusan_phi"


def test_source_slug_defaults_to_derived_name():
    assert source_slug({"source_name": "Kasus Perselisihan"}) == "kasus_perselisihan"
