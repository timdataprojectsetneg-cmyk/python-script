"""Offline tests for BP2MI Penempatan PMI (shared BP2MI report parsing)."""

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.bp2mi import _laporan as lap
from ingestion.usecases.geopolitik.bp2mi.penempatan_pmi import extractor as ext
from ingestion.usecases.geopolitik.bp2mi.penempatan_pmi.extractor import Extractor
from ingestion.usecases.geopolitik.bp2mi.penempatan_pmi.models import Record

TABLE_PAGE = """NO NEGARA JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH
1 Malaysia 5.868 5.116 4.976 8.024 7.111 1.611 1.759 2.035 1.675 2.520 3.138 7.890 51.723
2 Hong Kong 8.326 8.113 10.811 10.896 9.268 6.196 8.807 8.018 7.663 8.043 6.695 6.937 99.773
3 Samoa Amerika 0 0 0 0 0 0 0 0 0 4 0 14 18
Jumlah 14.194 13.229 15.787 18.920 16.379 7.807 10.566 10.053 9.338 10.567 9.833 14.841 151.514
Layanan Penempatan Pekerja Migran Indonesia Tahun 2024 (Januari s.d. Desember)
Berdasarkan Negara Layanan Penempatan
*data ditarik per 1 Januari 2025
"""
OTHER_PAGE = """NO NEGARA JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH
1 Malaysia 1.500 825 301 1.223 68 2 - - - - - - 3.919
Data Lintas Kedatangan Pekerja Migran Indonesia Tahun 2024
Berdasarkan Negara Layanan Penempatan
"""


def test_parse_country_table_rows_and_totals():
    rows, totals = lap.parse_country_table(TABLE_PAGE)
    assert [r["negara"] for r in rows] == ["Malaysia", "Hong Kong", "Samoa Amerika"]
    assert rows[0]["jan"] == 5868 and rows[0]["des"] == 7890 and rows[0]["jumlah"] == 51723
    assert rows[2]["jan"] == 0
    assert totals[-1] == 151514


def test_dash_is_none_not_zero():
    rows, _ = lap.parse_country_table(OTHER_PAGE)
    assert rows[0]["jul"] is None and rows[0]["jun"] == 2


def test_title_picks_only_penempatan_country_table():
    pages = ["intro", OTHER_PAGE, TABLE_PAGE]
    rows = list(lap.extract_country_table(pages, ext.TITLE, "t"))
    assert len(rows) == 3
    assert rows[0]["tahun"] == 2024 and rows[0]["halaman_pdf"] == 3
    assert Record(**rows[0]).negara == "Malaysia"


def test_missing_table_raises():
    with pytest.raises(SourceUnavailable):
        list(lap.extract_country_table(["nothing"], ext.TITLE, "t"))


def test_find_report_links_newest_first():
    html = (
        '<a href="file/data_17-01-2024_Laporan_Publikasi_Bulan_Desember_2023.pdf">a</a>'
        '<a href="/statpenempatan/file/data_08-01-2025_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2024.pdf">b</a>'
        '<a href="file/Data_Penempatan_Pekerja_Migran_Indonesia_Tahun_2022.pdf">c</a>'
    )
    links = lap.find_report_links(html, "https://jabar.bp2mi.go.id/statpenempatan/")
    assert links[0].endswith("data_08-01-2025_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2024.pdf")
    assert len(links) == 2


def test_resolve_report_url_direct_pdf_and_landing():
    class Http:
        def get(self, url, **kw):
            class R:
                text = '<a href="file/data_08-01-2025_Laporan_Publikasi_Data_PMI_X.pdf">x</a>'
            if "sdi" in url:
                raise SourceUnavailable("down")
            return R()

    assert lap.resolve_report_url(Http(), "https://x/y.pdf") == "https://x/y.pdf"
    assert lap.resolve_report_url(Http(), None).endswith("data_08-01-2025_Laporan_Publikasi_Data_PMI_X.pdf")


def test_no_links_raises():
    class Http:
        def get(self, url, **kw):
            raise SourceUnavailable("down")

    with pytest.raises(SourceUnavailable):
        lap.resolve_report_url(Http(), None)


def test_source_file_missing(tmp_path):
    with pytest.raises(ConfigError):
        Extractor({"source_file": str(tmp_path / "missing.pdf")}).extract().__next__()


def _row(no, name, per_month, total):
    return f"{no} {name} " + " ".join([str(per_month)] * 12) + f" {total}\n"


HEAD = "NO NEGARA JAN FEB MAR APR MEI JUN JUL AGU SEP OKT NOV DES JUMLAH\n"
SPILL_A = HEAD + _row(1, "Malaysia", 1, 12) + _row(2, "Taiwan", 2, 24)
SPILL_B = HEAD + _row(3, "Jepang", 3, 36)
SPILL_C = (
    HEAD + _row(4, "Korea Selatan", 4, 48)
    + "Jumlah " + " ".join(["10"] * 12) + " 120\n"
    + "Layanan Penempatan Pekerja Migran Indonesia Tahun 2023 (Januari s.d. Desember)\n"
    + "Berdasarkan Negara Layanan Penempatan\n"
)


def test_table_spilling_over_pages_is_followed_forward_to_the_total_row():
    first = (
        "Layanan Penempatan Pekerja Migran Indonesia Tahun 2023 (Januari s.d. Desember)\n"
        "Berdasarkan Negara Layanan Penempatan\n" + SPILL_A
    )
    rows = list(lap.extract_country_table(["intro", first, SPILL_B, SPILL_B.replace("Jepang", "Brunei").replace("3 ", "5 "), SPILL_C], ext.TITLE, "t"))
    assert [(r["negara"], r["halaman_pdf"]) for r in rows] == [
        ("Malaysia", 2), ("Taiwan", 2), ("Jepang", 3), ("Brunei", 4), ("Korea Selatan", 5),
    ]
    assert {r["tahun"] for r in rows} == {2023}


def test_table_spilling_over_pages_is_followed_backward_from_the_titled_page():
    rows = list(lap.extract_country_table(["intro", SPILL_A, SPILL_B, SPILL_C], ext.TITLE, "t"))
    assert [(r["negara"], r["halaman_pdf"]) for r in rows] == [
        ("Malaysia", 2), ("Taiwan", 2), ("Jepang", 3), ("Korea Selatan", 4),
    ]


class _Resp:
    def __init__(self, text="", content=b""):
        self.text, self.content = text, content


class _Http:
    def __init__(self, landing_html, pdfs):
        self.landing_html, self.pdfs, self.calls = landing_html, pdfs, []

    def get(self, url, **kw):
        self.calls.append(url)
        if url in self.pdfs:
            return _Resp(content=self.pdfs[url])
        if "sdi.bp2mi" in url:
            raise SourceUnavailable("down")
        return _Resp(text=self.landing_html)


LANDING = (
    '<a href="file/data_08-01-2025_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2024.pdf">a</a>'
    '<a href="file/data_20-12-2024_Laporan_Publikasi_Data_PMI_Januari_s_d__November_2024.pdf">b</a>'
    '<a href="file/data_17-01-2024_Laporan_Publikasi_Bulan_Desember_2023.pdf">c</a>'
    '<a href="file/data_10-01-2023_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2022.pdf">d</a>'
)
BASE = "https://jabar.bp2mi.go.id/statpenempatan/file/"


def test_resolve_report_urls_keeps_the_newest_report_per_data_year():
    urls = lap.resolve_report_urls(_Http(LANDING, {}), None)
    assert urls == [
        BASE + "data_08-01-2025_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2024.pdf",
        BASE + "data_17-01-2024_Laporan_Publikasi_Bulan_Desember_2023.pdf",
        BASE + "data_10-01-2023_Laporan_Publikasi_Data_PMI_Januari_s_d__Desember_2022.pdf",
    ]


def test_extract_reports_reads_every_year_and_skips_a_narrative_report(monkeypatch):
    pdfs = {u: b"%PDF-" + u.encode() for u in lap.resolve_report_urls(_Http(LANDING, {}), None)}
    y2024 = TABLE_PAGE
    y2022 = TABLE_PAGE.replace("Tahun 2024", "Tahun 2022")
    by_name = {
        "Desember_2024": ["x", y2024],
        "Bulan_Desember_2023": ["narrative only, no table"],
        "Desember_2022": [y2022],
    }

    def fake_read(content):
        key = next(k for k in by_name if k.encode() in content)
        return by_name[key]

    monkeypatch.setattr(lap, "read_pages", fake_read)
    http = _Http(LANDING, pdfs)
    rows = list(lap.extract_reports(http, None, None, ext.TITLE, "t"))
    assert [(r["tahun"], r["negara"]) for r in rows] == [(2024, "Malaysia"), (2024, "Hong Kong"), (2024, "Samoa Amerika")] + [
        (2022, "Malaysia"), (2022, "Hong Kong"), (2022, "Samoa Amerika"),
    ]


def test_extract_reports_fails_when_no_report_has_the_table(monkeypatch):
    pdfs = {u: b"%PDF-x" for u in lap.resolve_report_urls(_Http(LANDING, {}), None)}
    monkeypatch.setattr(lap, "read_pages", lambda content: ["no table"])
    with pytest.raises(SourceUnavailable):
        list(lap.extract_reports(_Http(LANDING, pdfs), None, None, ext.TITLE, "t"))
