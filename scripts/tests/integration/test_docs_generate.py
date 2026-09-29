"""Integration test for the ``docs`` CLI command with a stubbed SharePoint client."""

from ingestion.cli import _generate_docs
from ingestion.sharepoint.client import SharePointClient

CATALOG = "Available Data Source per Usecase.xlsx"
DICTIONARY = "Data Dictionary - Ketenagakerjaan.xlsx"

CATALOG_ROWS = [
    {
        "Source Name": "Kasus Perselisihan",
        "Publisher": "Kemnaker",
        "Data Dictionary": DICTIONARY,
        "Source Link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
        "Data Access": "Download Excel",
        "Update Frequency": "Monthly",
        "Eligible": True,
    },
    {
        "Source Name": "Data Mogok Kerja",
        "Publisher": "Kemnaker",
        "Data Dictionary": DICTIONARY,
        "Source Link": "https://satudata.kemnaker.go.id/data/kumpulan-data/3616",
        "Data Access": "Download Excel",
        "Update Frequency": "Monthly",
        "Eligible": True,
    },
]

DICTIONARY_ROWS = [
    {"Label": "Jenis_Perselisihan", "Tipe Data": "String", "Satuan": "-", "Deskripsi": "Jenis kasus"},
    {"Label": "Jumlah_Pusat", "Tipe Data": "Integer", "Satuan": "Kasus", "Deskripsi": "Tingkat pusat"},
]


DICTIONARY_MATRIX = [
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["Jenis_Perselisihan", "String", "-", "Jenis kasus"],
    ["Jumlah_Pusat", "Integer", "Kasus", "Tingkat pusat"],
]


def _install_stub(monkeypatch):
    def list_sheets(self, path):
        if path == CATALOG:
            return ["Ketenagakerjaan", "Ketahanan Pangan"]
        return ["Kasus Perselisihan", "Data Mogok Kerja"]

    monkeypatch.setattr(SharePointClient, "list_sheets", list_sheets)
    monkeypatch.setattr(
        SharePointClient,
        "read_sheet",
        lambda self, ref, sheet, **kwargs: CATALOG_ROWS if ref == CATALOG else DICTIONARY_ROWS,
    )
    monkeypatch.setattr(
        SharePointClient, "read_matrix", lambda self, ref, sheet: DICTIONARY_MATRIX
    )


def test_generate_docs_all(monkeypatch, tmp_path):
    _install_stub(monkeypatch)
    out = tmp_path / "docs"
    _generate_docs("ketenagakerjaan", None, str(out), None)

    assert (out / "usecase_ketenagakerjaan.md").exists()
    assert (out / "dictionary_ketenagakerjaan_kasus_perselisihan.md").exists()
    assert (out / "dictionary_ketenagakerjaan_data_mogok_kerja.md").exists()
    assert "Jenis_Perselisihan" in (out / "dictionary_ketenagakerjaan_kasus_perselisihan.md").read_text()


def test_generate_docs_single_source(monkeypatch, tmp_path):
    _install_stub(monkeypatch)
    out = tmp_path / "docs"
    _generate_docs("ketenagakerjaan", "Data Mogok Kerja", str(out), None)

    assert (out / "usecase_ketenagakerjaan.md").exists()
    assert (out / "dictionary_ketenagakerjaan_data_mogok_kerja.md").exists()
    assert not (out / "dictionary_ketenagakerjaan_kasus_perselisihan.md").exists()


def test_generate_docs_prefers_file_id(monkeypatch, tmp_path):
    monkeypatch.setenv("SHAREPOINT__FILE_ID", "01ABCDEF23GHIJKL45MNOPQR")
    monkeypatch.setenv("SHAREPOINT__CATALOG_PATH", "Available Data Source per Usecase.xlsx")

    refs = []

    def list_sheets(self, ref):
        refs.append(ref)
        if ref == "01ABCDEF23GHIJKL45MNOPQR":
            return ["Ketenagakerjaan"]
        return ["Kasus Perselisihan", "Data Mogok Kerja"]

    monkeypatch.setattr(SharePointClient, "list_sheets", list_sheets)
    monkeypatch.setattr(
        SharePointClient, "read_sheet", lambda self, ref, sheet, **kwargs: CATALOG_ROWS
    )
    monkeypatch.setattr(
        SharePointClient, "read_matrix", lambda self, ref, sheet: DICTIONARY_MATRIX
    )

    _generate_docs("ketenagakerjaan", None, str(tmp_path / "docs"), None)
    assert refs[0] == "01ABCDEF23GHIJKL45MNOPQR"
