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

    uc = out / "ketenagakerjaan"
    assert (uc / "usecase.md").exists()
    assert (uc / "dictionary_kasus_perselisihan.md").exists()
    assert (uc / "dictionary_data_mogok_kerja.md").exists()
    assert "Jenis_Perselisihan" in (uc / "dictionary_kasus_perselisihan.md").read_text()


def test_generate_docs_single_source(monkeypatch, tmp_path):
    _install_stub(monkeypatch)
    out = tmp_path / "docs"
    _generate_docs("ketenagakerjaan", "Data Mogok Kerja", str(out), None)

    uc = out / "ketenagakerjaan"
    assert (uc / "usecase.md").exists()
    assert (uc / "dictionary_data_mogok_kerja.md").exists()
    assert not (uc / "dictionary_kasus_perselisihan.md").exists()


def test_generate_docs_falls_back_from_empty_summary_sheet(monkeypatch, tmp_path):
    source = dict(CATALOG_ROWS[0], **{"Source Name": "Direktori Putusan PHI"})

    monkeypatch.setattr(
        SharePointClient,
        "list_sheets",
        lambda self, ref: ["Summary (2)", "MA Putusan Perkara PHI (2)"]
        if ref != CATALOG
        else ["Ketenagakerjaan"],
    )
    monkeypatch.setattr(
        SharePointClient,
        "read_sheet",
        lambda self, ref, sheet, **kwargs: [source] if ref == CATALOG else DICTIONARY_ROWS,
    )
    monkeypatch.setattr(
        SharePointClient,
        "read_matrix",
        lambda self, ref, sheet: [] if sheet == "Summary (2)" else DICTIONARY_MATRIX,
    )

    _generate_docs("ketenagakerjaan", "Direktori Putusan PHI", str(tmp_path / "docs"), None)

    content = (tmp_path / "docs" / "ketenagakerjaan" / "dictionary_direktori_putusan_phi.md").read_text()
    assert "Jenis_Perselisihan" in content


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


LINK_URL = (
    "https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/"
    "Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/"
    "1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20"
    "Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660"
)
LINK_PATH = (
    "Sitroom-2026/PROJECT/DATA/1 - Discover/Data Dictionary - Ketenagakerjaan/"
    "1. Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan (1).xlsx"
)

LINK_ROW = {
    "Source Name": "Direktori Putusan PHI",
    "Publisher": "MA RI",
    "Data Dictionary": (
        "Data Dictionary - Ketenagakerjaan - Direktori Putusan Perkara Pengadilan "
        "Hubungan Industrial (Mahkamah Agung RI)"
    ),
    "Source Link": "https://putusan3.mahkamahagung.go.id/search.html?q=PHI",
    "Data Access": "Web Scraping",
    "Update Frequency": "Daily",
    "Eligible": True,
}


def test_generate_docs_uses_dictionary_hyperlink(monkeypatch, tmp_path):
    refs = []

    def list_sheets(self, ref):
        refs.append(ref)
        if ref == CATALOG:
            return ["Ketenagakerjaan"]
        return ["Direktori Putusan PHI"]

    def read_sheet(self, ref, sheet, **kwargs):
        if ref == CATALOG:
            return [dict(LINK_ROW, _links={"Data Dictionary": LINK_URL})]
        return DICTIONARY_ROWS

    monkeypatch.setattr(SharePointClient, "list_sheets", list_sheets)
    monkeypatch.setattr(SharePointClient, "read_sheet", read_sheet)
    monkeypatch.setattr(
        SharePointClient, "read_matrix", lambda self, ref, sheet: DICTIONARY_MATRIX
    )

    _generate_docs("ketenagakerjaan", None, str(tmp_path / "docs"), None)

    uc = tmp_path / "docs" / "ketenagakerjaan"
    assert (uc / "dictionary_direktori_putusan_phi.md").exists()
    assert LINK_PATH in refs


SHARED_TEXT = "Data Dictionary - Ketenagakerjaan - UMK"


def test_generate_docs_shares_dictionary_link_across_sources(monkeypatch, tmp_path):
    """One row's dictionary link serves other rows with the same cell text."""
    rows = [
        dict(
            LINK_ROW,
            **{
                "Source Name": "UMK Aceh",
                "Data Dictionary": SHARED_TEXT,
                "_links": {"Data Dictionary": LINK_URL},
            },
        ),
        dict(LINK_ROW, **{"Source Name": "UMK Sumut", "Data Dictionary": SHARED_TEXT}),
    ]
    refs = []

    def list_sheets(self, ref):
        refs.append(ref)
        if ref == CATALOG:
            return ["Ketenagakerjaan"]
        return ["UMK"]

    monkeypatch.setattr(SharePointClient, "list_sheets", list_sheets)
    monkeypatch.setattr(
        SharePointClient, "read_sheet", lambda self, ref, sheet, **kwargs: rows
    )
    monkeypatch.setattr(
        SharePointClient, "read_matrix", lambda self, ref, sheet: DICTIONARY_MATRIX
    )

    _generate_docs("ketenagakerjaan", None, str(tmp_path / "docs"), None)

    uc = tmp_path / "docs" / "ketenagakerjaan"
    assert (uc / "dictionary_umk_aceh.md").exists()
    assert (uc / "dictionary_umk_sumut.md").exists()
    assert refs.count(LINK_PATH) == 2


GOOGLE_DICT_URL = (
    "https://docs.google.com/spreadsheets/d/DICTWORKBOOKID00000000/edit?gid=0#gid=0"
)

SPREADSHEET_MATRIX = [
    ["Data Dictionary", None, None, None],
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["Nomor_Perkara", "String", "-", "Nomor putusan"],
    ["Putusan", "Json", "URL", "Detail putusan (lihat tabel berikut)"],
    [],
    ["Data Dictionary Putusan", None, None, None],
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["Tingkat_Proses", "String", "-", "Tingkat proses"],
]


def test_generate_docs_spreadsheet_multiple_tables_in_one_sheet(monkeypatch, tmp_path):
    monkeypatch.setenv("DOCS_SOURCE", "spreadsheet")
    from ingestion.spreadsheet.client import SpreadsheetClient

    catalog_row = dict(
        LINK_ROW,
        **{
            "Source Name": "Direktori Putusan PHI",
            "_links": {"Data Dictionary": GOOGLE_DICT_URL},
        },
    )
    resolved = []

    def resolve_dictionary_link(self, link, sheet):
        resolved.append(link)
        return "DICTWORKBOOKID00000000"

    monkeypatch.setattr(
        SpreadsheetClient, "catalog_ref", lambda self, override=None: "CATALOGWORKBOOK"
    )
    monkeypatch.setattr(
        SpreadsheetClient,
        "list_sheets",
        lambda self, ref: ["Ketenagakerjaan"] if ref == "CATALOGWORKBOOK" else ["Direktori Putusan PHI"],
    )
    monkeypatch.setattr(
        SpreadsheetClient, "read_sheet", lambda self, ref, sheet, **kw: [catalog_row]
    )
    monkeypatch.setattr(
        SpreadsheetClient, "read_matrix", lambda self, ref, sheet: SPREADSHEET_MATRIX
    )
    monkeypatch.setattr(SpreadsheetClient, "resolve_dictionary_link", resolve_dictionary_link)
    monkeypatch.setattr(SpreadsheetClient, "link_sheet_hint", lambda self, url: None)

    _generate_docs("ketenagakerjaan", None, str(tmp_path / "docs"), None)

    content = (
        tmp_path / "docs" / "ketenagakerjaan" / "dictionary_direktori_putusan_phi.md"
    ).read_text()
    assert resolved == [GOOGLE_DICT_URL]
    assert "### JSON field: `putusan`" in content
    assert "Tingkat_Proses" in content


