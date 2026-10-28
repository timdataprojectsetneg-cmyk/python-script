"""Offline tests for Kemlu Daftar Keanggotaan Organisasi Internasional."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.kemlu.daftar_keanggotaan_oi import extractor as ext
from ingestion.usecases.geopolitik.kemlu.daftar_keanggotaan_oi.extractor import (
    Extractor,
    column_of,
    join_spans,
    parse_pages,
)
from ingestion.usecases.geopolitik.kemlu.daftar_keanggotaan_oi.models import Record


def span(x, y, text, size=8.0):
    return (x, y, text, size, x + len(text) * size * 0.5)


def number_row(y):
    return [span(x, y, str(n)) for x, n in zip((40, 120, 260, 400, 520, 600), (1, 2, 3, 4, 6, 7))]


def data_row(y, no, name, status, dasar, unit, ket):
    cells = [(40, str(no)), (95, name), (230, status), (310, dasar), (490, unit), (575, ket)]
    return [span(x, y, text) for x, text in cells if text]


PAGE_1 = (
    [span(40, 700, "1) DPR RI")]
    + number_row(680)
    + data_row(660, 1, "Asia-Pacific Parliamentary Forum", "Anggota 1975", "UU No. 1", "Dit. Sosbud", "Aktif")
    + [span(95, 650, "(APPF)")]
    + data_row(630, 2, "Inter-Parliamentary Union", "Anggota 1950", "UU No. 2", "", "Aktif,")
    + [span(40, 600, "2) BPK RI")]
    + number_row(580)
    + data_row(560, 1, "INTOSAI", "Anggota 1968", "Kepres 3", "Dit. Ekonomi", "")
)
PAGE_2 = [span(575, 700, "disertai iuran")]


def test_column_of_assigns_by_x_position():
    assert column_of(10) == "no"
    assert column_of(100) == "nama"
    assert column_of(240) == "status"
    assert column_of(320) == "dasar"
    assert column_of(500) == "unit"
    assert column_of(600) == "keterangan"


def test_join_spans_glues_split_words_and_keeps_gaps():
    glued = join_spans([(10, 0, "Bali", 8.0, 24.0), (24.0, 0, "tahun", 8.0, 44.0)])
    spaced = join_spans([(10, 0, "Bali", 8.0, 24.0), (30.0, 0, "tahun", 8.0, 50.0)])
    assert glued == "Balitahun"
    assert spaced == "Bali tahun"


def test_parse_pages_groups_rows_and_continues_across_pages():
    rows = parse_pages([PAGE_1, PAGE_2])
    assert [(r["kelompok_instansi"], r["no_pada_kelompok"]) for r in rows] == [
        ("DPR RI", 1),
        ("DPR RI", 2),
        ("BPK RI", 1),
    ]
    first = rows[0]
    assert first["nama_organisasi_internasional"] == "Asia-Pacific Parliamentary Forum (APPF)"
    assert first["status_dan_tahun"] == "Anggota 1975"
    assert first["dasar_hukum"] == "UU No. 1"
    assert first["unit_terkait_di_kemlu"] == "Dit. Sosbud"
    assert first["halaman_pdf"] == 1
    assert rows[1]["unit_terkait_di_kemlu"] is None
    assert rows[2]["keterangan"] == "disertai iuran"
    assert rows[2]["halaman_pdf"] == 1


def test_parse_pages_ignores_text_outside_table():
    stray = [span(40, 760, "Keanggotaan Indonesia pada Organisasi Internasional")]
    assert parse_pages([stray]) == []


def test_record_accepts_parsed_rows():
    rows = parse_pages([PAGE_1, PAGE_2])
    record = Record(**rows[0])
    assert record.kelompok_instansi == "DPR RI"
    assert record.no_pada_kelompok == 1
    assert record.halaman_pdf == 1


def test_extractor_raises_when_nothing_parsed(monkeypatch):
    monkeypatch.setattr(Extractor, "_load_pdf", lambda self: b"%PDF")
    monkeypatch.setattr(ext, "read_pdf_spans", lambda content: [[]])
    with pytest.raises(SourceUnavailable):
        list(Extractor({}).extract())


def test_extractor_yields_rows(monkeypatch):
    monkeypatch.setattr(Extractor, "_load_pdf", lambda self: b"%PDF")
    monkeypatch.setattr(ext, "read_pdf_spans", lambda content: [PAGE_1, PAGE_2])
    assert len(list(Extractor({}).extract())) == 3


def test_group_heading_split_by_kerning_is_still_a_heading():
    heading = [span(40, 700, "1"), span(44, 700, "9"), span(48, 700, ")."), span(60, 700, "KPU")]
    page = heading + number_row(680) + data_row(660, 1, "Electoral Forum", "Anggota 2001", "UU 7", "Dit. Politik", "")
    rows = parse_pages([page])
    assert [(r["kelompok_instansi"], r["no_pada_kelompok"]) for r in rows] == [("KPU", 1)]


def test_many_pages_and_groups_lose_no_rows():
    pages = []
    for p in range(1, 13):
        pages.append(
            [span(40, 700, f"{p}) GROUP{p}")]
            + number_row(680)
            + data_row(660, 1, f"Org {p}a", "Anggota", "UU", "Dit", "")
            + data_row(640, 2, f"Org {p}b", "Anggota", "UU", "Dit", "")
        )
    rows = parse_pages(pages)
    assert len(rows) == 24
    assert [r["halaman_pdf"] for r in rows[::2]] == list(range(1, 13))
    assert rows[-1]["kelompok_instansi"] == "GROUP12"
