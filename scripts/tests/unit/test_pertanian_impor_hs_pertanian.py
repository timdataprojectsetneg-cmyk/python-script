"""Offline tests for Impor HS Pertanian (Kementan Eksim)."""

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.pertanian._eksim import (
    parse_result_tables,
    parse_select_options,
    parse_years,
    to_number,
)
from ingestion.usecases.geopolitik.pertanian.impor_hs_pertanian.extractor import Extractor
from ingestion.usecases.geopolitik.pertanian.impor_hs_pertanian.models import Record

FORM_HTML = """
<form name="registrasi" action="hasilImporHs.php" method="post">
<select name="prop" id="prop"><option value="">-- Pilih Tahun --</option>
<option value=2024>2024</option><option value=2025>2025</option><option value=2026>2026</option></select>
<select name="subsektor"><option value="">-- Pilih Subsektor --</option>
<option value=1>Tanaman Pangan</option><option value=2>Hortikultura</option></select>
</form>
"""


def _cells(values):
    return "".join(f"<td align='right'>{v}</td>" for v in values)


def _row(kode, deskripsi, monthly):
    flat = [x for pair in monthly for x in pair]
    return f"<tr><td>'{kode}</td><td width='250'>{deskripsi}</td>{_cells(flat)}{_cells(['0', '0'])}</tr>"


def _result_html():
    header = (
        "<tr><td rowspan='2'>Kode HS</td><td rowspan='2'>Deskripsi</td>"
        + "".join("<td colspan='2'>M</td>" for _ in range(13))
        + "</tr><tr>"
        + "".join("<td>Volume (Kg)</td><td>Nilai (US$)</td>" for _ in range(13))
        + "</tr>"
    )
    zero = ("0", "0")
    jan = ("14,500.00", "163,125.00")
    mar = ("1,707.57", "3,836.62")
    r1 = _row("10061010", "Beras berkulit", [jan, zero, mar] + [zero] * 9)
    r2 = _row("10061090", "Beras lain", [zero] * 11 + [("5.00", "9.50")])
    total = "<tr><td></td><td>Total</td>" + _cells(["1"] * 26) + "</tr>"
    return (
        "<center>Kementerian Pertanian</center>"
        "<div><b>Gabah</b></div><table class='table'>" + header + r1 + r2 + total + "</table>"
        "<div><b>Beras</b></div><table class='table'>" + header + _row("10063000", "Beras setengah giling", [mar] + [zero] * 11) + "</table>"
    )


class FakeResponse:
    def __init__(self, text):
        self.content = text.encode("utf-8")


class FakeHttp:
    def __init__(self):
        self.posts = []

    def get(self, url, **kwargs):
        return FakeResponse(FORM_HTML)

    def post(self, url, data=None, **kwargs):
        self.posts.append((url, data))
        return FakeResponse(_result_html())


def test_to_number_handles_thousands_and_zero():
    assert to_number("14,500.00") == 14500.0
    assert to_number("0") == 0.0
    assert to_number("") is None


def test_parse_select_options_skips_placeholder():
    assert parse_select_options(FORM_HTML, "prop") == [("2024", "2024"), ("2025", "2025"), ("2026", "2026")]
    assert parse_select_options(FORM_HTML, "subsektor")[0] == ("1", "Tanaman Pangan")


def test_parse_years_variants():
    assert parse_years("", [2023, 2024, 2025]) == [2023, 2024, 2025]
    assert parse_years("2022-2024", []) == [2022, 2023, 2024]
    assert parse_years("2021, 2025", []) == [2021, 2025]
    with pytest.raises(ConfigError):
        parse_years("abc", [])


def test_parse_result_tables_unpivots_months_and_skips_zero_and_total():
    rows = parse_result_tables(_result_html(), tahun=2025, arus="Impor", subsektor="Tanaman Pangan")
    keys = {(r["kelompok_komoditas"], r["kode_hs"], r["nomor_bulan"]) for r in rows}
    assert keys == {
        ("Gabah", "10061010", 1),
        ("Gabah", "10061010", 3),
        ("Gabah", "10061090", 12),
        ("Beras", "10063000", 1),
    }
    jan = next(r for r in rows if r["kode_hs"] == "10061010" and r["nomor_bulan"] == 1)
    assert jan["volume"] == 14500.0 and jan["nilai"] == 163125.0 and jan["bulan"] == "Januari"
    assert all(r["kode_hs"] != "" and not r["kode_hs"].startswith("'") for r in rows)


def test_parse_result_tables_include_zero_keeps_all_months():
    rows = parse_result_tables(_result_html(), tahun=2025, arus="Impor", subsektor="x", include_zero=True)
    assert len(rows) == 12 * 3


def test_record_types():
    rows = parse_result_tables(_result_html(), tahun=2025, arus="Impor", subsektor="Tanaman Pangan")
    rec = Record(**rows[0])
    assert rec.tahun == 2025 and rec.arus == "Impor"
    assert isinstance(rec.kode_hs, str) and isinstance(rec.volume, float)


def test_extract_posts_one_request_per_year_and_subsector():
    ext = Extractor({"years": "2025", "subsektor": "1"})
    ext.http = FakeHttp()
    rows = list(ext.extract())
    assert len(ext.http.posts) == 1
    url, data = ext.http.posts[0]
    assert url.endswith("/eksim/hasilImporHs.php")
    assert data["prop"] == "2025" and data["subsektor"] == "1" and data["kec"] == "12"
    assert {r["tahun"] for r in rows} == {2025} and {r["subsektor"] for r in rows} == {"Tanaman Pangan"}


def test_extract_defaults_to_every_offered_year_and_all_subsectors():
    ext = Extractor({})
    ext.http = FakeHttp()
    list(ext.extract())
    assert len(ext.http.posts) == len(parse_years('', [int(v) for v, _ in parse_select_options(FORM_HTML, 'prop')])) * 2


def test_extract_raises_when_nothing_found():
    ext = Extractor({"years": "2025", "subsektor": "1"})
    http = FakeHttp()
    http.post = lambda url, data=None, **kw: FakeResponse("<html>kosong</html>")
    ext.http = http
    with pytest.raises(SourceUnavailable):
        list(ext.extract())


def test_options_can_come_from_params_json():
    ext = Extractor({"years": "2025", "params": '{"subsektor": "2", "include_zero": true}'})
    ext.http = FakeHttp()
    rows = list(ext.extract())
    assert [d["subsektor"] for _, d in ext.http.posts] == ["2"]
    assert len(rows) == 12 * 3


def test_invalid_params_json_is_a_config_error():
    ext = Extractor({"years": "2025", "params": "{oops"})
    ext.http = FakeHttp()
    with pytest.raises(ConfigError):
        list(ext.extract())
