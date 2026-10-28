"""Offline tests for Perubahan Tarif PMK 50-2026 (Bea Cukai)."""

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.beacukai.perubahan_tarif_pmk import extractor as mod
from ingestion.usecases.geopolitik.beacukai.perubahan_tarif_pmk.extractor import (
    Extractor,
    build_records,
    find_pdf_url,
    parse_context,
    parse_effective_date,
    parse_pasal_ii,
    parse_peraturan,
    parse_tariff_lines,
    read_pdf_pages,
)
from ingestion.usecases.geopolitik.beacukai.perubahan_tarif_pmk.models import Record

LANDING = """
<html><body>
<a href='http://repository.beacukai.go.id/referensi/2011/11/a5d5-user-manual-sistem-direktori-peraturan-djbc.pdf'>User Manual</a>
<table><tr><td>Mulai Berlaku</td><td>:</td><td>28-Jul-2026 s/d </td></tr></table>
<a href="https://repository.beacukai.go.id/peraturan/2026/07/abc-pmk-50-tahun-2026.pdf">Unduh</a>
</body></html>
"""

PAGE1 = """ PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
NOMOR 50 TAHUN 2026
TENTANG
PERUBAHAN KETIGA ATAS PERATURAN MENTERI KEUANGAN
Menimbang  : a.  bahwa untuk meningkatkan daya saing industri
Maintenance, Repair, And Overhaul (MRO) pesawat udara,
pemerintah perlu memberikan insentif fiskal;
  b.  bahwa untuk meningkatkan daya saing industri
petrokimia, pemerintah perlu memberikan dukungan
penurunan tarif bea masuk atas impor  barang Liquefied
Petroleum Gas (LPG);
  c. bahwa untuk memberikan dukungan sebagaimana dimaksud
dalam huruf a  dan huruf b , Peraturan Menteri Keuangan perlu diubah;
"""
PAGE2 = "- 2 - \nMengingat : 1. Pasal 17 ayat (3) Undang-Undang Dasar\n"
PAGE3 = """- 3 -
MEMUTUSKAN:
Pasal I
Catatan Bab 98 diubah.
Pasal II
1. Atas impor LPG yang termasuk dalam pos tarif 9845.10.00
dan 9845.20.00 sebagaimana tercantum dalam
Lampiran III diberikan tarif bea masuk
sebesar 0% (nol persen) selama 6 (enam) bulan sejak
berlakunya Peraturan Menteri ini.
2. Peraturan Menteri ini mulai berlaku setelah 7 (tujuh) hari
terhitung sejak tanggal diundangkan.
"""
PAGES = [PAGE1, PAGE2, PAGE3]

# Lampiran III table pieces (x, y, text) in stream order; columns: no <118, code <190, id <330, en <470, rate.
TABLE_PAGE_10 = [
    (300, 700, "(1) (2) (3) (4)"), (480, 700, "(5)"),
    (50, 600, "1234"), (130, 600, "3901.10.10"), (200, 600, "Polietilena"), (340, 600, "Polyethylene"), (480, 600, "5.00 %"),
    (50, 560, "1235"), (130, 560, "3901.10.20"), (200, 560, "Lainnya"), (480, 560, "Tetap"),
    (50, 520, "1236"), (130, 520, "3901.2"), (160, 520, "0.10"), (200, 520, "Polietilena"), (240, 520, "linier"), (480, 520, "7.50 %"),
    (50, 480, "1237"), (130, 480, "3902.10.00"), (200, 480, "Polipropilena,"), (340, 480, "Polypropylene,"),
]
TABLE_PAGE_11 = [
    (300, 700, "(1) (2) (3) (4)"), (480, 700, "(5)"),
    (200, 650, "dalam bentuk primer"), (340, 650, "in primary forms"), (480, 650, "10.00 %"),
    (130, 600, "39.03"),
    (200, 590, "orphan text after a heading"),
    (50, 550, "1238"), (130, 550, "3903.11.10"), (200, 550, "Polistirena"), (480, 550, "Tetap"),
    (50, 500, "1239"), (130, 500, "3903.19.00"), (200, 500, "Lainnya"), (480, 500, "2.50 %"),
    (200, 100, "MENTERI KEUANGAN REPUBLIK INDONESIA,"), (200, 60, "stray text after the signature"),
]
NO_TABLE_PAGE = [(50, 600, "Pasal III"), (130, 600, "1111"), (130, 560, "3901.99.99")]


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeHttp:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(url)
        return FakeResponse(self.routes[url])


def test_parse_effective_date_handles_english_and_indonesian_months():
    assert parse_effective_date(LANDING) == "2026-07-28"
    assert parse_effective_date("<td>Mulai Berlaku</td><td>:</td><td>05-Agu-2026</td>") == "2026-08-05"
    assert parse_effective_date("<p>tidak ada</p>") is None


def test_find_pdf_url_skips_user_manual():
    assert find_pdf_url(LANDING, "https://peraturan.beacukai.go.id/index.html") == (
        "https://repository.beacukai.go.id/peraturan/2026/07/abc-pmk-50-tahun-2026.pdf"
    )
    assert find_pdf_url("<a href='/x.html'>x</a>", "https://a.b/") is None


def test_parse_peraturan():
    assert parse_peraturan(PAGE1) == "PMK Nomor 50 Tahun 2026"
    assert parse_peraturan("tidak relevan") is None


def test_parse_pasal_ii():
    article = parse_pasal_ii(PAGES)
    assert article == {
        "halaman_pdf": 3,
        "kode_hs": ["9845.10.00", "9845.20.00"],
        "tarif_bea_masuk": 0.0,
        "masa_berlaku_tarif": "6 bulan",
        "komoditas": "LPG",
    }


def test_parse_context_prefers_clause_mentioning_commodity():
    context = parse_context(PAGES, "LPG")
    assert context.startswith("bahwa untuk meningkatkan daya saing industri petrokimia")
    assert "(LPG)" in context
    assert "MRO" in parse_context(PAGES, None)


def test_build_records_one_per_hs_code_and_validates():
    records = build_records(PAGES, "2026-07-28")
    assert [r["kode_hs"] for r in records] == ["9845.10.00", "9845.20.00"]
    rec = Record(**records[0])
    assert rec.tanggal_berlaku.isoformat() == "2026-07-28"
    assert rec.tarif_bea_masuk == 0.0 and rec.halaman_pdf == 3


def test_build_records_raises_without_pasal_ii():
    with pytest.raises(SourceUnavailable):
        build_records([PAGE1, PAGE2], None)


def test_extract_follows_landing_page_to_pdf(monkeypatch):
    monkeypatch.setattr(mod, "read_pdf_pages", lambda content, max_pages=None: PAGES)
    monkeypatch.setattr(mod, "read_tariff_fragments", lambda content, pages: {})
    landing = "https://peraturan.beacukai.go.id/index.html?page=detail"
    pdf = "https://repository.beacukai.go.id/peraturan/2026/07/abc-pmk-50-tahun-2026.pdf"
    ext = Extractor({"url": landing})
    ext.http = FakeHttp({landing: LANDING.encode(), pdf: b"%PDF"})
    rows = list(ext.extract())
    assert ext.http.calls == [landing, pdf]
    assert len(rows) == 2 and rows[0]["tanggal_berlaku"] == "2026-07-28"


def test_extract_pdf_url_override_skips_landing(monkeypatch):
    monkeypatch.setattr(mod, "read_pdf_pages", lambda content, max_pages=None: PAGES)
    monkeypatch.setattr(mod, "read_tariff_fragments", lambda content, pages: {})
    ext = Extractor({"pdf_url": "https://x.test/a.pdf"})
    ext.http = FakeHttp({"https://x.test/a.pdf": b"%PDF"})
    rows = list(ext.extract())
    assert ext.http.calls == ["https://x.test/a.pdf"]
    assert rows[0]["tanggal_berlaku"] is None


def test_parse_tariff_lines_follows_rows_across_pages_and_skips_tetap():
    lines = parse_tariff_lines({10: TABLE_PAGE_10, 11: TABLE_PAGE_11, 12: NO_TABLE_PAGE})
    assert [(l["kode_hs"], l["uraian"], l["tarif_bea_masuk"], l["halaman_pdf"]) for l in lines] == [
        ("3901.10.10", "Polietilena", 5.0, 10),
        ("3901.20.10", "Polietilenalinier", 7.5, 10),
        ("3902.10.00", "Polipropilena, dalam bentuk primer", 10.0, 10),
        ("3903.19.00", "Lainnya", 2.5, 11),
    ]


def test_parse_tariff_lines_does_not_duplicate_or_lose_a_row_at_the_page_break():
    lines = parse_tariff_lines({10: TABLE_PAGE_10, 11: TABLE_PAGE_11})
    codes = [l["kode_hs"] for l in lines]
    assert len(codes) == len(set(codes)) == 4


def test_build_records_adds_every_changed_tariff_line_and_the_article_codes():
    fragments = {
        10: [
            (480, 700, "(5)"),
            (50, 600, "1234"), (130, 600, "9845.10.00"), (200, 600, "LPG"), (480, 600, "0.00 %"),
            (50, 560, "1235"), (130, 560, "3901.10.10"), (200, 560, "Polietilena"), (480, 560, "5.00 %"),
        ]
    }
    records = build_records(PAGES, "2026-07-28", fragments)
    assert [r["kode_hs"] for r in records] == ["9845.10.00", "3901.10.10", "9845.20.00"]
    in_article, other, absent = records
    assert in_article["tarif_bea_masuk"] == 0.0 and in_article["masa_berlaku_tarif"] == "6 bulan"
    assert other["tarif_bea_masuk"] == 5.0 and other["masa_berlaku_tarif"] is None
    assert other["komoditas"] == "Polietilena" and other["halaman_pdf"] == 10
    assert absent["komoditas"] == "LPG" and absent["halaman_pdf"] == 3
    assert all(Record(**r) for r in records)


def test_build_records_restores_spaces_lost_to_kerning_from_the_plain_text_row():
    plain = "- 10 -\n1236 3901.20.10 Polietilena linier Polyethylene linear 7.50 %\n"
    fragments = {
        10: [
            (480, 700, "(5)"),
            (50, 520, "1236"), (130, 520, "3901.20.10"), (200, 520, "Polietilena"), (240, 520, "linier"),
            (480, 520, "7.50 %"),
        ]
    }
    records = build_records(PAGES + [plain], "2026-07-28", fragments)
    assert records[0]["komoditas"] == "Polietilena linier" and records[0]["tarif_bea_masuk"] == 7.5


class FakePdfPage:
    def __init__(self, text):
        self.text = text

    def extract_text(self, *args, **kwargs):
        return self.text


class FakeReader:
    def __init__(self, pages):
        self.pages = [FakePdfPage(t) for t in pages]


def test_read_pdf_pages_reads_every_page_without_a_default_cap(monkeypatch):
    monkeypatch.setattr(mod, "_pdf_reader", lambda content: FakeReader([f"p{i}" for i in range(500)]))
    assert len(read_pdf_pages(b"%PDF")) == 500


def test_read_pdf_pages_max_pages_limits_and_warns(monkeypatch, caplog):
    monkeypatch.setattr(mod, "_pdf_reader", lambda content: FakeReader([f"p{i}" for i in range(10)]))
    with caplog.at_level("WARNING"):
        assert read_pdf_pages(b"%PDF", 3) == ["p0", "p1", "p2"]
    assert "MAX_PAGES" in caplog.text


def test_extract_requires_url_or_pdf_url():
    with pytest.raises(ConfigError):
        list(Extractor({}).extract())
