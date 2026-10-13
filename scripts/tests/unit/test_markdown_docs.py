"""Unit tests for Markdown doc rendering."""

from ingestion.catalog.metadata_parser import derive_access, resolve_sheet_name
from ingestion.catalog.markdown_docs import (
    dictionary_filename,
    env_lines,
    render_dictionary_markdown,
    render_usecase_markdown,
    usecase_dir,
    usecase_filename,
)


def test_derive_access():
    assert derive_access("Download Excel") == "excel"
    assert derive_access("REST API") == "api"
    assert derive_access("Web Scraping") == "scraper"
    assert derive_access("Download PDF") == "pdf"
    assert derive_access("") == "excel"


def test_resolve_sheet_name():
    sheets = ["Ketenagakerjaan", "Ketahanan Pangan", "Pemogokan Kerja"]
    assert resolve_sheet_name(sheets, "ketenagakerjaan") == "Ketenagakerjaan"
    assert resolve_sheet_name(sheets, "pemogokan_kerja") == "Pemogokan Kerja"
    assert resolve_sheet_name(sheets, "Geopolitik") is None


def test_filenames():
    assert usecase_dir("ketenagakerjaan") == "ketenagakerjaan"
    assert usecase_filename("ketenagakerjaan") == "usecase.md"
    assert dictionary_filename("Kasus Perselisihan") == "dictionary_kasus_perselisihan.md"


SOURCES = [
    {
        "source_name": "Kasus Perselisihan",
        "publisher": "Kemnaker",
        "data_dictionary": "Data Dictionary - Ketenagakerjaan.xlsx",
        "source_link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
        "data_access": "Download Excel",
        "update_frequency": "Monthly",
        "eligible": True,
    },
    {
        "source_name": "BPS Inflasi MoM",
        "publisher": "BPS",
        "data_dictionary": "Data Dictionary - Ketenagakerjaan.xlsx",
        "source_link": "https://www.bps.go.id/api/",
        "data_access": "API",
        "update_frequency": "Monthly",
        "eligible": True,
    },
]


def test_render_usecase_markdown():
    md = render_usecase_markdown("ketenagakerjaan", SOURCES, "catalog.xlsx")
    assert "# Use Case: ketenagakerjaan" in md
    assert "Kasus Perselisihan" in md
    assert "BPS Inflasi MoM" in md


def test_env_lines_are_flat_without_access():
    lines = env_lines("ketenagakerjaan", SOURCES)
    assert any(line.startswith("KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL=") for line in lines)
    assert any(line.startswith("KETENAGAKERJAAN__BPS__BPS_INFLASI_MOM__URL=") for line in lines)
    assert all("__EXCEL__" not in line and "__API__" not in line for line in lines)


def test_env_lines_prefer_resource_url():
    sources = [
        {
            "source_name": "Kasus Perselisihan",
            "publisher": "Kemnaker",
            "source_link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
            "resource_url": "https://satudata.kemnaker.go.id/api/v1/data/list_data?search=Kasus",
            "data_access": "Download Excel",
            "eligible": True,
        }
    ]
    lines = env_lines("ketenagakerjaan", sources)
    assert (
        "KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL="
        "https://satudata.kemnaker.go.id/api/v1/data/list_data?search=Kasus"
    ) in lines


def test_render_usecase_markdown_targets():
    sources = [
        {
            "source_name": "Kasus Perselisihan",
            "publisher": "Kemnaker",
            "data_access": "Download Excel",
            "update_frequency": "Monthly",
            "raw_minio_bucket": "setneg-raw",
            "raw_postgre_table": "raw_ketenagakerjaan.kasus_perselisihan",
        }
    ]
    md = render_usecase_markdown("ketenagakerjaan", sources, "catalog.xlsx")
    assert "## Targets" in md
    assert "setneg-raw" in md
    assert "raw_ketenagakerjaan.kasus_perselisihan" in md


def test_render_dictionary_markdown():
    schema = [
        {"label": "Jenis_Perselisihan", "type": "String", "satuan": "-", "deskripsi": "Jenis kasus"},
        {"label": "Jumlah_Pusat", "type": "Integer", "satuan": "Kasus", "deskripsi": "Tingkat pusat"},
    ]
    md = render_dictionary_markdown("ketenagakerjaan", "Kasus Perselisihan", schema, SOURCES[0], "a/b/models.py")
    assert "# Data Dictionary: Kasus Perselisihan" in md
    assert "| Jenis_Perselisihan | `jenis_perselisihan` | String | - | Jenis kasus |" in md
    assert "class KasusPerselisihanRecord(BaseModel):" in md
    assert "jumlah_pusat: int | None" in md


def test_render_dictionary_markdown_json_nested():
    schema = [
        {
            "label": "putusan",
            "name": "putusan",
            "type": "json",
            "fields": [
                {
                    "label": "Nomor_Perkara",
                    "name": "nomor_perkara",
                    "type": "String",
                    "satuan": "-",
                    "deskripsi": "Nomor putusan",
                }
            ],
        }
    ]
    md = render_dictionary_markdown("ketenagakerjaan", "Direktori Putusan", schema, SOURCES[0], "a/b/models.py")
    assert "### JSON field: `putusan`" in md
    assert "| Nomor_Perkara | `nomor_perkara` | String | - | Nomor putusan |" in md
