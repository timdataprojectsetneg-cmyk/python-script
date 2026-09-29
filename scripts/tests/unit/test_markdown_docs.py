"""Unit tests for Markdown doc rendering."""

from ingestion.sharepoint.metadata_parser import derive_access, resolve_sheet_name
from ingestion.sharepoint.markdown_docs import (
    dictionary_filename,
    render_dictionary_markdown,
    render_usecase_markdown,
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
    assert usecase_filename("ketenagakerjaan") == "usecase_ketenagakerjaan.md"
    assert (
        dictionary_filename("ketenagakerjaan", "Kasus Perselisihan")
        == "dictionary_ketenagakerjaan_kasus_perselisihan.md"
    )


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
    assert "usecases/ketenagakerjaan/" in md
    assert "├── kasus_perselisihan/" in md
    assert "└── excel/" in md
    assert "└── api/" in md
    assert "extractor.py" in md
    assert "KETENAGAKERJAAN__KASUS_PERSELISIHAN__EXCEL__URL=" in md


def test_render_usecase_markdown_targets():
    sources = [
        {
            "source_name": "Kasus Perselisihan",
            "publisher": "Kemnaker",
            "data_access": "Download Excel",
            "update_frequency": "Monthly",
            "raw_minio_bucket": "setneg-raw",
            "raw_postgre_schema": "raw_ketenagakerjaan",
        }
    ]
    md = render_usecase_markdown("ketenagakerjaan", sources, "catalog.xlsx")
    assert "## Targets" in md
    assert "setneg-raw" in md
    assert "raw_ketenagakerjaan" in md


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
