"""Round-trip tests: generated docs are read back as catalog rows + schemas."""

from ingestion.catalog.docs_reader import read_dictionary_schemas, read_usecase_sources
from ingestion.catalog.markdown_docs import (
    dictionary_filename,
    render_dictionary_markdown,
    render_usecase_markdown,
    write_markdown,
)
from ingestion.catalog.metadata_parser import parse_catalog_row

ROWS = [
    {
        "Source Name": "Kasus Perselisihan",
        "Publisher": "Kemnaker",
        "Data Access": "Download Excel",
        "Update Frequency": "Monthly",
        "Eligible": True,
        "Source Link": "https://example.org/a",
    },
    {
        "Source Name": "Sumber Manual",
        "Publisher": "Kemnaker",
        "Data Access": "Manual",
        "Eligible": False,
        "Source Link": "https://example.org/b",
    },
]

SCHEMA = [
    {
        "label": "Nomor_Perkara",
        "name": "nomor_perkara",
        "type": "String",
        "satuan": None,
        "deskripsi": "Nomor putusan",
    },
    {
        "label": "Putusan",
        "name": "putusan",
        "type": "Json",
        "satuan": "URL",
        "deskripsi": "Detail | pakai pipe",
        "fields": [
            {
                "label": "Tingkat_Proses",
                "name": "tingkat_proses",
                "type": "String",
                "satuan": None,
                "deskripsi": "Tingkat proses",
            }
        ],
    },
]


def _write_docs(tmp_path):
    sources = [parse_catalog_row(row) for row in ROWS]
    docs_dir = tmp_path / "docs" / "ketenagakerjaan"
    write_markdown(render_usecase_markdown("ketenagakerjaan", sources, "catalog.xlsx"), str(docs_dir), "usecase.md")
    write_markdown(
        render_dictionary_markdown("ketenagakerjaan", "Kasus Perselisihan", SCHEMA, sources[0], "x/models.py"),
        str(docs_dir),
        dictionary_filename("Kasus Perselisihan"),
    )
    return docs_dir


def test_read_usecase_sources_round_trips(tmp_path):
    docs_dir = _write_docs(tmp_path)

    sources = read_usecase_sources(docs_dir)

    assert [s["source_name"] for s in sources] == ["Kasus Perselisihan", "Sumber Manual"]
    assert sources[0]["publisher"] == "Kemnaker"
    assert sources[0]["data_access"] == "Download Excel"
    assert sources[1]["eligible"] == "False"


def test_read_dictionary_schemas_round_trips_including_json_field(tmp_path):
    docs_dir = _write_docs(tmp_path)

    schemas = read_dictionary_schemas(docs_dir)

    schema = schemas["kasus_perselisihan"]
    assert [field["name"] for field in schema] == ["nomor_perkara", "putusan"]
    assert schema[1]["deskripsi"] == "Detail | pakai pipe"
    assert schema[1]["fields"][0]["name"] == "tingkat_proses"
