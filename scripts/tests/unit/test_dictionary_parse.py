"""Tests for Data Dictionary matrix parsing and snake_case column names."""

from ingestion.sharepoint.metadata_parser import (
    parse_dictionary_matrix,
    to_pydantic_source,
    to_snake_case,
)


def test_to_snake_case():
    assert to_snake_case("Jenis Perselisihan") == "jenis_perselisihan"
    assert to_snake_case("Jumlah_Pusat") == "jumlah_pusat"
    assert to_snake_case("Tenaga Kerja yang Terlibat (orang)") == "tenaga_kerja_yang_terlibat_orang"


def test_parse_dictionary_matrix_start_and_end():
    matrix = [
        ["Metadata Statistik"],
        [],
        ["No.", "Nama Indikator", "Konsep"],
        ["Label", "Tipe Data", "Satuan", "Deskripsi"],
        ["Jenis_Perselisihan", "String", "-", "Jenis kasus"],
        ["Jumlah_Pusat", "Integer", "Kasus", "Tingkat pusat"],
        [],  # first fully-empty row -> end
        ["Ignored", "String", "-", "after the blank row"],
    ]
    schema = parse_dictionary_matrix(matrix)
    assert len(schema) == 2
    assert schema[0] == {
        "label": "Jenis_Perselisihan",
        "name": "jenis_perselisihan",
        "type": "String",
        "satuan": "-",
        "deskripsi": "Jenis kasus",
    }
    assert schema[1]["name"] == "jumlah_pusat"


def test_parse_dictionary_matrix_no_header():
    assert parse_dictionary_matrix([["a", "b"], ["c", "d"]]) == []
    assert parse_dictionary_matrix([]) == []


def test_parse_dictionary_matrix_partial_row_kept():
    matrix = [
        ["Label", "Tipe Data", "Satuan", "Deskripsi"],
        ["A", "String", None, "x"],
    ]
    schema = parse_dictionary_matrix(matrix)
    assert len(schema) == 1
    assert schema[0]["satuan"] is None


NESTED_MATRIX = [
    ["Data Dictionary", None, None, None],
    [],
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["nomor_perkara", "String", "-", "Nomor perkara"],
    ["putusan", "json", None, None],
    ["link_file", "String", None, "link url pdf"],
    [],
    ["Data Dictionary : putusan", None, None, None],
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["Nomor_Perkara", "String", "-", "Nomor putusan"],
    ["Tahun", "Integer", "-", "Tahun perkara"],
]


def test_parse_dictionary_matrix_nested_json_fields():
    schema = parse_dictionary_matrix(NESTED_MATRIX)
    assert [field["name"] for field in schema] == ["nomor_perkara", "putusan", "link_file"]
    assert "fields" not in schema[0]
    assert [sub["name"] for sub in schema[1]["fields"]] == ["nomor_perkara", "tahun"]
    assert schema[1]["fields"][0]["deskripsi"] == "Nomor putusan"


def test_to_pydantic_source_json_nested():
    schema = parse_dictionary_matrix(NESTED_MATRIX)
    source = to_pydantic_source("PerkaraRecord", schema)
    assert "class Putusan(BaseModel):" in source
    assert 'putusan: Putusan | None = Field(default=None, alias="putusan"' in source
    assert 'description="Nomor perkara"' in source
    assert "nomor_perkara: str | None" in source
