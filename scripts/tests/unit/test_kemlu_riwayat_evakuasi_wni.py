"""Offline tests for Kemlu Riwayat Evakuasi WNI (Renstra Dit. PWNI 2025-2029)."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.kemlu.riwayat_evakuasi_wni import extractor as ext
from ingestion.usecases.geopolitik.kemlu.riwayat_evakuasi_wni.models import Record

PAGE_HEADER = """
 Evakuasi WNI dari Luar Negeri

   Tahun         Negara                       Jenis Kondisi                 Jumlah     Evacuees



  21  |  RENSTRA DIREKTORAT PELINDUNGAN WNI 2025 - 2029
"""
PAGE_ROWS = """
   2020          RRT                         Bencana Pandemi              312 WNI

   2021          Afghanistan                 Perang/Konflik               26 WNI dan 7 WNA

   2023          Turki, Sudan, dan           Bencana Alam dan             1.119 WNI
                 Palestina                   Perang/Konflik

   2024          Lebanon dan Suriah          Perang/Konflik               259 WNI

 Pemulangan Kelompok Rentan dari Malaysia

   2021  901  chartered flight
"""


def test_rows_split_by_column_and_wrapped_cells_rejoined():
    rows = ext.parse_evacuations(["intro", PAGE_HEADER, PAGE_ROWS])
    assert [r["tahun"] for r in rows] == [2020, 2021, 2023, 2024]
    assert rows[0]["negara_wilayah"] == "China" and rows[0]["konteks"] == "Bencana Pandemi"
    assert rows[1]["wni_dievakuasi"] == 26 and rows[1]["wna_dievakuasi"] == 7
    assert rows[2]["negara_wilayah"] == "Turki; Sudan; Palestina"
    assert rows[2]["konteks"] == "Bencana Alam dan Perang/Konflik"
    assert rows[2]["wni_dievakuasi"] == 1119 and rows[2]["wna_dievakuasi"] is None
    assert rows[3]["negara_wilayah"] == "Lebanon; Suriah"
    assert all(r["halaman_pdf"] == 3 for r in rows)


def test_parse_stops_at_next_section():
    rows = ext.parse_evacuations([PAGE_HEADER, PAGE_ROWS])
    assert len(rows) == 4  # the 2021 Malaysia repatriation table below is not evacuation data


def test_no_header_returns_empty_and_extract_raises(monkeypatch):
    assert ext.parse_evacuations(["nothing"]) == []
    monkeypatch.setattr(ext, "load_pdf", lambda *a, **k: (b"", "x"))
    monkeypatch.setattr(ext, "read_pages", lambda c, layout=False: ["nothing"])
    with pytest.raises(SourceUnavailable):
        list(ext.Extractor({}).extract())


def test_counts_and_record():
    assert ext.parse_count("1.119 WNI", "WNI") == 1119
    assert ext.parse_count("1.119 WNI", "WNA") is None
    rec = Record(**ext.parse_evacuations([PAGE_HEADER, PAGE_ROWS])[0])
    assert rec.tahun == 2020 and rec.wni_dievakuasi == 312


ROWS_PAGE_A = """
   2020          RRT                         Bencana Pandemi              312 WNI

   2021          Afghanistan                 Perang/Konflik               26 WNI dan 7 WNA
"""
ROWS_PAGE_B = """
   2022          Ukraina                     Perang/Konflik               90 WNI

   2025          Iran                        Perang/Konflik               13 WNI
"""


def test_rows_on_later_pages_are_read_with_their_own_page_number():
    rows = ext.parse_evacuations(["intro", PAGE_HEADER, ROWS_PAGE_A, ROWS_PAGE_B])
    assert [(r["tahun"], r["halaman_pdf"]) for r in rows] == [(2020, 3), (2021, 3), (2022, 4), (2025, 4)]
    assert rows[3]["negara_wilayah"] == "Iran"
