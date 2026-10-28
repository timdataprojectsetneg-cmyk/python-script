"""Offline tests for Kemlu Kasus Pelindungan WNI (LKJ Dit. PWNI)."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.kemlu.kasus_pelindungan_wni import extractor as ext
from ingestion.usecases.geopolitik.kemlu.kasus_pelindungan_wni.models import Record

PAGE_1 = """
  130|
III. Matriks Informasi Kinerja

DATA DUKUNG
    KASUS WNI DI LUAR NEGERI
    DITANGANI SELESAI
KASUS UMUM
62.120 55.984
Pidana 300 200
  KDRT 100 90
  Penipuan 200 110
      
Peyalahgunaan Visa, Izin Tinggal dan
Dokumen Lainnya 33.768 32.177
  Overstay 19602 18671
   
Masuk Negara Lain secara
Illegal 14166 13506

Lainnya   50 30
  Sakit 20 10
  Lainnya 30 20
"""
PAGE_2 = """
1 |
LAPORAN KINERJA

Eksploitasi Ketenagakerjaan
di Bawah Umur 7 7
KASUS KHUSUS 5 4
TPPO 7 7
  Eksploitasi Seksual 3 3

Eksploitasi Ketenagakerjaan
di Bawah Umur 4 4
 TOTAL 1 1
Kasus Awak Kapal Migran   767
"""


def test_parse_cases_groups_children_and_wrapped_labels():
    rows = ext.parse_cases([(130, PAGE_1)])
    got = [(r["kelompok_kasus"], r["jenis_kasus"], r["ditangani"], r["selesai"]) for r in rows]
    assert got[:2] == [("Pidana", "KDRT", 100, 90), ("Pidana", "Penipuan", 200, 110)]
    assert ("Visa, Izin Tinggal dan Dokumen", "Overstay", 19602, 18671) in got
    assert ("Visa, Izin Tinggal dan Dokumen", "Masuk Negara Lain secara Illegal", 14166, 13506) in got
    assert ("Lainnya", "Lainnya", 30, 20) in got and ("Lainnya", "Sakit", 20, 10) in got
    assert all(r["halaman_pdf"] == 130 for r in rows)


def test_group_carries_across_pages_and_totals_are_skipped():
    rows = ext.parse_cases([(131, "TPPO 3 3\n  Eksploitasi Seksual 3 3\n"), (132, "  Terorisme 76 24\n TOTAL 79 27\n")])
    assert rows[-1]["kelompok_kasus"] == "TPPO" and rows[-1]["jenis_kasus"] == "Terorisme"
    assert rows[-1]["halaman_pdf"] == 132
    assert len(rows) == 2


def test_subtotal_mismatch_is_logged_not_fixed(caplog):
    with caplog.at_level("WARNING"):
        rows = ext.parse_cases([(1, "Pidana 10 10\n  KDRT 3 3\n  Penipuan 4 4\n")])
    assert [r["ditangani"] for r in rows] == [3, 4]
    assert "subtotal" in caplog.text


def test_find_table_pages_stops_at_total():
    pages = ["x", PAGE_1, PAGE_2, "later page"]
    assert ext.find_table_pages(pages) == [1, 2]
    assert ext.find_table_pages(["x"]) == []


def test_detect_year_priority():
    assert ext.detect_year("https://k/174_LKJ_Dit__PWNI_2024.pdf", [], None) == 2024
    assert ext.detect_year("local.pdf", ["LAPORAN KINERJA TAHUN 2023"], None) == 2023
    assert ext.detect_year("x", [], "2022") == 2022
    assert ext.detect_year("x", [], None) is None


def test_missing_table_raises(monkeypatch):
    monkeypatch.setattr(ext, "load_pdf", lambda *a, **k: (b"", "x"))
    monkeypatch.setattr(ext, "read_pages", lambda c: ["nothing here"])
    with pytest.raises(SourceUnavailable):
        list(ext.Extractor({}).extract())


def test_extract_yields_year_and_validates(monkeypatch):
    monkeypatch.setattr(ext, "load_pdf", lambda *a, **k: (b"", "LKJ_Dit__PWNI_2024.pdf"))
    monkeypatch.setattr(ext, "read_pages", lambda c: [PAGE_1])
    rows = list(ext.Extractor({}).extract())
    assert rows and rows[0]["tahun"] == 2024
    assert Record(**rows[0]).kelompok_kasus == "Pidana"


def _filler_page(index):
    return f"  Jenis {chr(ord('A') + index)}ku 2 1\n"


def test_table_spanning_many_pages_is_read_to_the_total_row():
    pages = ["intro", PAGE_1] + [_filler_page(i) for i in range(8)] + [PAGE_2, "later page"]
    idx = ext.find_table_pages(pages)
    assert idx == list(range(1, 11))
    rows = ext.parse_cases([(i + 1, pages[i]) for i in idx])
    filler = [r for r in rows if r["jenis_kasus"].endswith("ku")]
    assert len(filler) == 8 and {r["kelompok_kasus"] for r in filler} == {"Lainnya"}
    assert [r["halaman_pdf"] for r in filler] == list(range(3, 11))


def test_table_without_total_row_is_read_to_the_last_page_and_warns(caplog):
    pages = ["intro", PAGE_1] + [_filler_page(i) for i in range(5)]
    with caplog.at_level("WARNING"):
        assert ext.find_table_pages(pages) == list(range(1, 7))
    assert "TOTAL row not found" in caplog.text
