"""Offline tests for PMA Negara Asal (BKPM)."""

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.bkpm.pma_negara_asal import extractor as mod
from ingestion.usecases.geopolitik.bkpm.pma_negara_asal.extractor import (
    Extractor,
    header_period,
    normalize_period,
    parse_pages,
    parse_podium,
    parse_releases,
)
from ingestion.usecases.geopolitik.bkpm.pma_negara_asal.models import Record

# (x, y, text), deliberately listed in a scrambled order like the real PDF text stream.
Q4_PAGE = [
    (640, 86, "Malaysia"), (827, 86, "Jepang"), (445, 85, "R. R."), (483, 83, "Tiongkok"),
    (253, 83, "Hongkong, RRT"), (90, 83, "Singapura"),
    (53, 501, "Realisasi"), (145, 501, "Triwulan"), (232, 501, "IV"), (256, 501, "Tahun"),
    (320, 501, "2025:"), (377, 501, "5 Besar Negara Asal PMA"),
    (107, 441, "USD"), (103, 418, "4,8"), (133, 418, "M"),
    (294, 375, "USD"), (290, 352, "3,4"), (320, 352, "M"),
    (473, 329, "USD"), (469, 305, "2,1"), (499, 305, "M"),
    (658, 294, "USD"), (655, 270, "1,7"), (685, 270, "M"),
    (839, 275, "USD"), (836, 251, "0,8"), (866, 251, "M"),
    (53, 53, "Keterangan"), (119, 53, ": M ="), (267, 53, "Kurs APBN 1 USD = Rp16.000,00"),
    (939, 11, "9"),
]
FY_PAGE = [
    (52, 497, "Realisasi"), (163, 497, "Januari"), (255, 497, "–"), (275, 497, "Desember"),
    (398, 497, "2025:"), (466, 497, "5 Besar Negara Asal PMA"),
    (87, 417, "17,4 M"), (276, 343, "10,6 M"), (463, 310, "7,5"), (493, 310, "M"),
    (646, 276, "4,5 M"), (825, 264, "3,1"), (855, 264, "M"),
    (634, 84, "Malaysia"), (820, 84, "Jepang"), (421, 83, "R. R."), (462, 83, "Tiongkok"),
    (81, 82, "Singapura"), (240, 82, "Hongkong, RRT"),
    (53, 52, "Keterangan"), (936, 11, "17"),
]
OTHER_PAGE = [(50, 500, "Realisasi PMDN"), (60, 400, "1,2")]
# Q1 layout: "US$ 4,6" with a separate "Miliar" below each value.
Q1_PAGE = [
    (178, 152, "Hongkong, RRT"), (48, 151, "Singapura"), (662, 152, "Jepang"),
    (334, 152, "R.R. Tiongkok"), (509, 152, "Malaysia"), (776, 96, "9"),
    (124, 499, "5 Besar Negara Realisasi Investasi PMA:"), (545, 499, "Triwulan I 2025"),
    (53, 448, "US$ 4,6"), (62, 424, "Miliar"), (206, 394, "US$ 2,2"), (215, 370, "Miliar"),
    (353, 372, "US$ 1,8"), (362, 349, "Miliar"), (507, 330, "US$ 1,0"), (517, 306, "Miliar"),
    (651, 330, "US$ 1,0"), (660, 306, "Miliar"),
    (24, 98, "Keterangan"), (79, 98, ": Menggunakan Kurs APBN US$ 1 = Rp 16.000,00"),
]
# Q2/Q3 layout: vertical "<negara> / USD x,y Miliar" list, header split in two lines, kerned pieces.
LIST_PAGE = [
    (110, 426, "Singapura"), (110, 400, "USD"), (148, 400, "3,8"), (176, 400, "Miliar"),
    (108, 347, "Hong Kong, RRT"), (108, 322, "USD"), (146, 322, "2"), (156, 322, ",7"), (175, 322, "Miliar"),
    (107, 271, "R.R."), (142, 271, "Tiongkok"), (107, 246, "USD"), (145, 246, "1"), (155, 246, ",9"), (174, 246, "Miliar"),
    (106, 187, "Malaysia"), (106, 162, "USD"), (144, 162, "1,0"), (173, 162, "Miliar"),
    (106, 109, "Amerika"), (176, 109, "Serikat"), (106, 84, "USD"), (144, 84, "0,8"), (172, 84, "Miliar"),
    (43, 415, "28,8%"), (40, 335, "20,3%"), (40, 258, "14,1"), (73, 258, "%"), (46, 177, "7,4%"), (47, 96, "5,8%"),
    (257, 507, "5 Besar Negara"), (434, 507, "Realisasi"), (545, 507, "Investasi"), (654, 507, "PMA"),
    (401, 480, "Triwulan"), (490, 480, "III 2025"), (933, 2, "8"),
    (9, 16, "Keterangan"), (65, 16, ":"), (70, 16, "Menggunakan"),
]
# 2026 layout: compact infographic, two-line names, page number repeated next to the labels.
COMPACT_PAGE = [
    (674, 33, "8"), (17, 345, "5 Besar Negara Realisasi Investasi PMA"), (17, 324, "Triwulan II Tahun 2026"),
    (28, 35, "Hong Kong,"), (45, 20, "RRT"), (104, 33, "Singapura"), (184, 31, "R.R."), (173, 17, "Tiongkok"),
    (242, 31, "Jepang"), (304, 32, "Malaysia"),
    (102, 200, "USD 4,2"), (108, 186, "Miliar"), (30, 215, "USD 5,0"), (36, 201, "Miliar"),
    (171, 189, "USD 1,7"), (177, 175, "Miliar"), (238, 185, "USD 0,9"), (243, 171, "Miliar"),
    (305, 181, "USD 0,7"), (310, 167, "Miliar"),
    (22, 287, "Top 5 Negara Terbesar"), (22, 274, "sebesar 79,6%"),
    (34, 70, "31,7%"), (105, 70, "27,0%"), (171, 68, "11,0%"), (239, 67, "5,6%"), (310, 65, "4,3%"),
    (292, 6, "Keterangan"), (336, 6, ": Menggunakan Kurs APBN US$ 1 = Rp 16.500,00; T= Triliun"),
]
# 2024 layout: values kerned into pieces ("2" "," "24" "M"), wide names ("Amerika" ... "Serikat").
KERNED_PAGE = [
    (244, 81, "Hongkong, RRT"), (86, 81, "Singapura"), (788, 84, "Amerika"), (862, 84, "Serikat"),
    (430, 83, "R. R."), (475, 83, "Tiongkok"), (637, 84, "Malaysia"),
    (106, 439, "US$"), (95, 413, "5,50"), (139, 413, "M"),
    (293, 366, "US$"), (282, 340, "2"), (293, 340, ","), (298, 340, "24"), (326, 340, "M"),
    (472, 335, "US$"), (461, 309, "1,86"), (506, 309, "M"),
    (658, 292, "US$"), (647, 266, "0"), (658, 266, ","), (663, 266, "99"), (691, 266, "M"),
    (839, 273, "US$"), (828, 247, "0,"), (844, 247, "84"), (872, 247, "M"),
    (47, 503, "Realisasi"), (130, 503, "Triwulan"), (208, 503, "III"), (228, 503, "Tahun"), (286, 503, "2024:"),
    (337, 503, "5 Besar Negara Asal PMA"), (892, 16, "09"),
    (53, 46, "Keterangan"), (119, 46, ": M ="), (295, 46, "APBN 1 US$ = Rp15.000,00"),
]
HILIRISASI_PAGE = [
    (100, 500, "5 Besar Negara Realisasi Investasi PMA Bidang Hilirisasi:"), (500, 500, "Triwulan I 2025"),
    (53, 448, "US$ 2,2"), (62, 424, "Miliar"), (48, 151, "Hongkong, RRT"), (24, 98, "Keterangan"),
]

LANDING = """
<div><p>15 Jan 2026</p><h2 class="x">Laporan Realisasi Investasi Triwulan IV dan Semester II 2025</h2>
<button data-remote="https://bkpm.go.id/modal/personal?filename=a.pdf&amp;saved_name=1768555595.pdf&amp;code=k">Unduh</button></div>
<div><h2>Realisasi Investasi TW III 2025</h2>
<button data-remote="https://bkpm.go.id/modal/personal?filename=b.pdf&amp;saved_name=1760686757.pdf&amp;code=x">Unduh</button></div>
"""


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


def test_normalize_period():
    assert normalize_period("Triwulan IV Tahun 2025") == "2025-Q4"
    assert normalize_period("Januari – Desember 2025") == "2025-FY"
    assert normalize_period("Januari - September 2025") == "2025-YTD09"
    assert normalize_period("Semester I 2025") == "2025-YTD06"
    assert normalize_period("Semester I Tahun 2026") == "2026-YTD06"
    assert normalize_period("Triwulan I I 2025") == "2025-Q2"
    assert normalize_period("Triwulan III 2025") == "2025-Q3"
    assert normalize_period("Januari–September 2024") == "2024-YTD09"
    assert normalize_period("Semester II 2025") is None


def test_header_period_reads_the_header_row():
    assert header_period(Q4_PAGE) == "2025-Q4"
    assert header_period(FY_PAGE) == "2025-FY"
    assert header_period(OTHER_PAGE) is None
    assert header_period(Q1_PAGE) == "2025-Q1"
    assert header_period(LIST_PAGE) == "2025-Q3"
    assert header_period(COMPACT_PAGE) == "2026-Q2"
    assert header_period(HILIRISASI_PAGE) is None


def test_parse_podium_pairs_by_x_and_ranks_by_value():
    assert parse_podium(Q4_PAGE) == [
        (1, "Singapura", 4.8),
        (2, "Hongkong, RRT", 3.4),
        (3, "R. R. Tiongkok", 2.1),
        (4, "Malaysia", 1.7),
        (5, "Jepang", 0.8),
    ]
    fy = parse_podium(FY_PAGE)
    assert fy[0] == (1, "Singapura", 17.4) and fy[2] == (3, "R. R. Tiongkok", 7.5)


def test_parse_podium_reads_q1_values_with_separate_unit():
    assert parse_podium(Q1_PAGE) == [
        (1, "Singapura", 4.6),
        (2, "Hongkong, RRT", 2.2),
        (3, "R.R. Tiongkok", 1.8),
        (4, "Malaysia", 1.0),
        (5, "Jepang", 1.0),
    ]


def test_parse_podium_reads_vertical_list_layout():
    assert parse_podium(LIST_PAGE) == [
        (1, "Singapura", 3.8),
        (2, "Hong Kong, RRT", 2.7),
        (3, "R.R. Tiongkok", 1.9),
        (4, "Malaysia", 1.0),
        (5, "Amerika Serikat", 0.8),
    ]


def test_parse_podium_pairs_compact_layout_by_nearest_column():
    assert parse_podium(COMPACT_PAGE) == [
        (1, "Hong Kong, RRT", 5.0),
        (2, "Singapura", 4.2),
        (3, "R.R. Tiongkok", 1.7),
        (4, "Jepang", 0.9),
        (5, "Malaysia", 0.7),
    ]


def test_parse_podium_joins_kerned_values_and_wide_names():
    assert parse_podium(KERNED_PAGE) == [
        (1, "Singapura", 5.5),
        (2, "Hongkong, RRT", 2.24),
        (3, "R. R. Tiongkok", 1.86),
        (4, "Malaysia", 0.99),
        (5, "Amerika Serikat", 0.84),
    ]


def test_parse_podium_skips_page_when_a_value_has_no_label():
    assert parse_podium([f for f in Q4_PAGE if f[0] < 800 or f[1] > 200]) == []


def test_parse_pages_scans_every_page_and_skips_hilirisasi():
    pages = [OTHER_PAGE] * 20 + [Q1_PAGE, HILIRISASI_PAGE, LIST_PAGE, KERNED_PAGE, COMPACT_PAGE]
    rows = parse_pages(pages)
    assert [(r["periode"], r["halaman_pdf"]) for r in rows[::5]] == [
        ("2025-Q1", 21), ("2025-Q3", 23), ("2024-Q3", 24), ("2026-Q2", 25),
    ]
    assert len(rows) == 20


def test_parse_pages_adds_period_and_page_number():
    rows = parse_pages([OTHER_PAGE, Q4_PAGE, FY_PAGE])
    assert len(rows) == 10
    assert {r["periode"] for r in rows} == {"2025-Q4", "2025-FY"}
    assert rows[0] == {
        "periode": "2025-Q4", "peringkat": 1, "negara_asal": "Singapura", "realisasi_pma": 4.8, "halaman_pdf": 2,
    }
    assert Record(**rows[5]).realisasi_pma == 17.4


def test_parse_releases_builds_storage_urls_newest_first():
    releases = parse_releases(LANDING, "https://bkpm.go.id/id/info/realisasi-investasi/2025")
    assert releases[0] == (
        "Laporan Realisasi Investasi Triwulan IV dan Semester II 2025",
        "https://bkpm.go.id/storage/file/pdf/1768555595.pdf",
    )
    assert len(releases) == 2


def test_extract_reads_every_release_and_keeps_the_newest_per_period(monkeypatch):
    by_content = {b"new": [Q4_PAGE], b"old": [Q4_PAGE, Q1_PAGE]}
    monkeypatch.setattr(mod, "read_pdf_fragments", lambda content, max_pages=None: by_content[content])
    landing = "https://bkpm.go.id/id/info/realisasi-investasi/2025"
    new = "https://bkpm.go.id/storage/file/pdf/1768555595.pdf"
    old = "https://bkpm.go.id/storage/file/pdf/1760686757.pdf"
    ext = Extractor({"url": landing})
    ext.http = FakeHttp({landing: LANDING.encode(), new: b"new", old: b"old"})
    rows = list(ext.extract())
    assert ext.http.calls == [landing, new, old]
    assert [r["periode"] for r in rows] == ["2025-Q4"] * 5 + ["2025-Q1"] * 5


def test_extract_follows_sibling_year_pages_newest_year_first(monkeypatch):
    by_content = {b"y26": [Q1_PAGE], b"y25": [Q4_PAGE]}
    monkeypatch.setattr(mod, "read_pdf_fragments", lambda content, max_pages=None: by_content[content])
    landing = "https://bkpm.go.id/id/info/realisasi-investasi/2025"
    html25 = (
        '<a href="/id/info/realisasi-investasi/2026">2026</a><a href="/id/info/realisasi-investasi/2025">2025</a>'
        '<h2>A</h2><button data-remote="https://bkpm.go.id/m?saved_name=25.pdf"></button>'
    )
    html26 = '<h2>B</h2><button data-remote="https://bkpm.go.id/m?saved_name=26.pdf"></button>'
    ext = Extractor({"url": landing})
    ext.http = FakeHttp({
        landing: html25.encode(),
        "https://bkpm.go.id/id/info/realisasi-investasi/2026": html26.encode(),
        "https://bkpm.go.id/storage/file/pdf/25.pdf": b"y25",
        "https://bkpm.go.id/storage/file/pdf/26.pdf": b"y26",
    })
    rows = list(ext.extract())
    assert [r["periode"] for r in rows] == ["2025-Q1"] * 5 + ["2025-Q4"] * 5


def test_extract_passes_max_pages_from_config(monkeypatch):
    seen = []

    def fake(content, max_pages=None):
        seen.append(max_pages)
        return [Q4_PAGE]

    monkeypatch.setattr(mod, "read_pdf_fragments", fake)
    ext = Extractor({"pdf_url": "https://x.test/a.pdf", "max_pages": "3"})
    ext.http = FakeHttp({"https://x.test/a.pdf": b"%PDF"})
    list(ext.extract())
    assert seen == [3]


def test_extract_skips_a_failing_release_when_others_work(monkeypatch):
    def fake(content, max_pages=None):
        if content == b"bad":
            raise SourceUnavailable("broken")
        return [Q4_PAGE]

    monkeypatch.setattr(mod, "read_pdf_fragments", fake)
    landing = "https://bkpm.go.id/id/info/realisasi-investasi/2025"
    ext = Extractor({"url": landing})
    ext.http = FakeHttp({
        landing: LANDING.encode(),
        "https://bkpm.go.id/storage/file/pdf/1768555595.pdf": b"bad",
        "https://bkpm.go.id/storage/file/pdf/1760686757.pdf": b"%PDF",
    })
    assert len(list(ext.extract())) == 5


def test_extract_pdf_url_skips_landing(monkeypatch):
    monkeypatch.setattr(mod, "read_pdf_fragments", lambda content, max_pages=None: [FY_PAGE])
    ext = Extractor({"pdf_url": "https://x.test/a.pdf", "url": "https://bkpm.go.id/landing"})
    ext.http = FakeHttp({"https://x.test/a.pdf": b"%PDF"})
    assert len(list(ext.extract())) == 5
    assert ext.http.calls == ["https://x.test/a.pdf"]


def test_extract_raises_when_no_podium_pages(monkeypatch):
    monkeypatch.setattr(mod, "read_pdf_fragments", lambda content, max_pages=None: [OTHER_PAGE])
    ext = Extractor({"pdf_url": "https://x.test/a.pdf"})
    ext.http = FakeHttp({"https://x.test/a.pdf": b"%PDF"})
    with pytest.raises(SourceUnavailable):
        list(ext.extract())


def test_extract_requires_url_or_pdf_url():
    with pytest.raises(ConfigError):
        list(Extractor({}).extract())
