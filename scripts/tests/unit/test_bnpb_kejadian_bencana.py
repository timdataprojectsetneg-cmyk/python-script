"""Offline tests for BNPB Kejadian Bencana."""

import datetime as dt
import io

import pytest
from openpyxl import Workbook

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.bnpb.kejadian_bencana.extractor import (
    Extractor,
    map_row,
    parse_arcgis_page,
    parse_excel,
)
from ingestion.usecases.geopolitik.bnpb.kejadian_bencana.models import Record


def _xlsx(header, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def test_parse_excel_with_dictionary_labels():
    header = ["No.", "Kode Identitas Bencana", "ID Kabupaten", "Tanggal Kejadian", "Kejadian",
              "Lokasi", "Kabupaten", "Provinsi", "Kronologi & Dokumentasi", "Penyebab",
              "Meninggal", "Hilang", "Terluka", "Rumah Rusak", "Rumah Terendam", "Fasum Rusak"]
    row = [1, None, 3315, dt.datetime(2026, 10, 20), "BANJIR", "Kecamatan: A\\nDesa: B",
           "GROBOGAN", "JAWA TENGAH", "Dokumentasi", None, 1, None, None, 0, None, 2]
    rows = parse_excel(_xlsx(header, [row]))
    assert len(rows) == 1
    rec = Record(**rows[0])
    assert rec.tanggal_kejadian == dt.date(2026, 10, 20)
    assert rec.id_kabupaten == 3315
    assert rec.lokasi == "Kecamatan: A, Desa: B"
    assert rec.meninggal == 1 and rec.hilang is None and rec.fasum_rusak == 2


def test_parse_excel_with_arcgis_field_names():
    header = ["level1", "nprop", "nkab", "kejadian", "lokasi", "tahun", "bulan", "tanggal", "kib", "terendam"]
    row = [6403, "KALIMANTAN TIMUR", "KUTAI KERTANEGARA", "BANJIR", "Kec. X\nDs. Y", 2021, 1, 1, "6403 101", 12]
    rec = Record(**parse_excel(_xlsx(header, [row]))[0])
    assert rec.tanggal_kejadian == dt.date(2021, 1, 1)
    assert rec.kabupaten == "KUTAI KERTANEGARA"
    assert rec.rumah_terendam == 12
    assert rec.kode_identitas_bencana == "6403 101"


def test_map_row_drops_rows_without_date_and_parses_epoch_ms():
    assert map_row({"kejadian": "BANJIR", "tahun": None}) is None
    row = map_row({"Tanggal Kejadian": 1760918400000, "Kejadian": "BANJIR", "Terluka": "3"})
    assert row["tanggal_kejadian"] == "2025-10-20"
    assert row["terluka"] == 3


def test_excel_without_header_raises():
    with pytest.raises(SourceUnavailable):
        parse_excel(_xlsx(["foo", "bar"], [[1, 2]]))


def test_arcgis_error_payload_raises_with_hint():
    with pytest.raises(SourceUnavailable, match="DOWNLOAD_URL"):
        parse_arcgis_page({"error": {"code": 500}}, "https://x/query")
    page = parse_arcgis_page({"features": [{"attributes": {"kejadian": "BANJIR"}}]})
    assert page == [{"kejadian": "BANJIR"}]


def test_extractor_reads_source_file(tmp_path):
    path = tmp_path / "bnpb.xlsx"
    path.write_bytes(_xlsx(["Tanggal Kejadian", "Kejadian", "Kabupaten"], [[dt.datetime(2026, 1, 2), "BANJIR", "X"]]).read())
    out = list(Extractor({"source_file": str(path)}).extract())
    assert out[0]["tanggal_kejadian"] == "2026-01-02"
