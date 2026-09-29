"""Tests for Data Dictionary matrix parsing and snake_case column names."""

from ingestion.sharepoint.metadata_parser import parse_dictionary_matrix, to_snake_case


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
