"""Offline tests for BP2MI Pengaduan PMI."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.bp2mi import _laporan as lap
from ingestion.usecases.geopolitik.bp2mi.pengaduan_pmi import extractor as ext
from ingestion.usecases.geopolitik.bp2mi.pengaduan_pmi.models import Record

COMPLAINT_PAGE = """Layanan Pengaduan Pekerja Migran Indonesia Tahun 2024 (Januari s.d. Desember)
Berdasarkan Negara
*data ditarik per 1 Januari 2025
NO NEGARA JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH
1   Malaysia 37 22 53 45 110 16 26 24 30 15 15 31 424
2   United Arab Emirates 1 3 3 3 5 1 3 3 6 5 5 4 42
3   Lainnya 22 13 5 11 17 22 9 15 12 4 10 0 140
Jumlah 60 38 61 59 132 39 38 42 48 24 30 35 606
"""
TOP5_PAGE = """Layanan Pengaduan Pekerja Migran Indonesia pada Desember Tahun 2024
Berdasarkan 5 Negara Tertinggi
NO NEGARA JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH
1 Malaysia 1 1 1 1 1 1 1 1 1 1 1 1 12
"""
PROVINCE_PAGE = """Layanan Pengaduan Pekerja Migran Indonesia Tahun 2024 (Januari s.d. Desember)
Berdasarkan Asal Provinsi Pekerja Migran Indonesia
NO ASAL PROVINSI JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH
"""


def test_only_the_country_table_matches():
    rows = list(lap.extract_country_table([TOP5_PAGE, PROVINCE_PAGE, COMPLAINT_PAGE], ext.TITLE, "t"))
    assert [r["negara"] for r in rows] == ["Malaysia", "United Arab Emirates", "Lainnya"]
    assert rows[0]["halaman_pdf"] == 3 and rows[0]["tahun"] == 2024
    assert rows[2]["des"] == 0 and rows[2]["jumlah"] == 140


def test_record_validates_row():
    row = list(lap.extract_country_table([COMPLAINT_PAGE], ext.TITLE, "t"))[0]
    rec = Record(**row)
    assert rec.jan == 37 and rec.jumlah == 424


def test_table_without_country_page_raises():
    with pytest.raises(SourceUnavailable):
        list(lap.extract_country_table([TOP5_PAGE, PROVINCE_PAGE], ext.TITLE, "t"))
