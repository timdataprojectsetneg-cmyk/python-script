"""Offline unit tests for Kemendag Ekspor Sektor / Impor Golongan (shared Satu Data reader)."""

from types import SimpleNamespace

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.kemendag import satudata_exim
from ingestion.usecases.geopolitik.kemendag.ekspor_sektor.extractor import COLUMNS as EKSPOR_COLUMNS
from ingestion.usecases.geopolitik.kemendag.ekspor_sektor.extractor import Extractor as EksporExtractor
from ingestion.usecases.geopolitik.kemendag.ekspor_sektor.models import Record as EksporRecord
from ingestion.usecases.geopolitik.kemendag.impor_golongan.extractor import COLUMNS as IMPOR_COLUMNS
from ingestion.usecases.geopolitik.kemendag.impor_golongan.extractor import Extractor as ImporExtractor
from ingestion.usecases.geopolitik.kemendag.impor_golongan.models import Record as ImporRecord

FORM = (
    '<form><input type="hidden" name="csrf_baseben" value="tok1">'
    '<select id="choices-tahun" name="period"><option value="2025">2025</option>'
    '<option value="2024">2024</option><option value="2016">2016</option></select></form>'
)


def _tables(year):
    return f"""
    <table id="example"><thead><tr><th>Tahun</th><th>Total</th><th>MIGAS</th><th>NON MIGAS</th>
    <th>Agriculture</th><th>Industry</th><th>Mining</th><th>Others</th></tr></thead><tbody>
    <tr><td>Februari</td><td>2,000.50</td><td>100</td><td>1,900.50</td><td>10</td><td>1,500</td><td>390</td><td>0.5</td></tr>
    <tr><td>Januari</td><td>1,000.25</td><td>-</td><td>1,000.25</td><td>5</td><td>900</td><td>95</td><td>0.25</td></tr>
    <tr><td>{year}</td><td>3000</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    </tbody></table>
    <table id="impor"><thead><tr><th>Tahun</th><th>Total</th><th>Consumption Goods</th>
    <th>Raw Material Support</th><th>Capital Goods</th></tr></thead><tbody>
    <tr><td>Januari</td><td>900.1</td><td>90</td><td>700</td><td>110.1</td></tr>
    </tbody></table>"""


class _StubHttp:
    def __init__(self, form=FORM):
        self.form = form
        self.posts = []

    def get(self, url, **kw):
        return SimpleNamespace(text=self.form)

    def post(self, url, data=None, **kw):
        self.posts.append(data)
        return SimpleNamespace(text=_tables(data["period"]) + '<input name="csrf_baseben" value="tok2">')


def test_parse_number():
    assert satudata_exim.parse_number("26,612.18") == 26612.18
    assert satudata_exim.parse_number("-") is None
    assert satudata_exim.parse_number("") is None
    assert satudata_exim.parse_number(None) is None
    assert satudata_exim.parse_number("abc") is None


def test_parse_years():
    avail = [2026, 2025, 2024, 2016]
    assert satudata_exim.parse_years("", avail) == [2016, 2024, 2025, 2026]
    assert satudata_exim.parse_years("2024-2026", avail) == [2024, 2025, 2026]
    assert satudata_exim.parse_years("2025,2010", avail) == [2025]


def test_parse_csrf_and_year_options():
    assert satudata_exim.parse_csrf(FORM) == ("csrf_baseben", "tok1")
    assert satudata_exim.parse_csrf("<html>") is None
    assert satudata_exim.parse_year_options(FORM) == [2025, 2024, 2016]


def test_parse_table_ekspor_sorted_and_skips_non_month_rows():
    rows = satudata_exim.parse_table(_tables(2024), "example", EKSPOR_COLUMNS, 2024)
    assert [r["periode"] for r in rows] == ["2024-01", "2024-02"]
    assert rows[0]["migas"] is None
    assert rows[1] == {
        "periode": "2024-02",
        "total_ekspor": 2000.5,
        "migas": 100.0,
        "nonmigas": 1900.5,
        "pertanian": 10.0,
        "industri": 1500.0,
        "pertambangan": 390.0,
        "lainnya": 0.5,
    }
    EksporRecord(**rows[1])


def test_parse_table_impor():
    rows = satudata_exim.parse_table(_tables(2024), "impor", IMPOR_COLUMNS, 2024)
    assert rows == [
        {"periode": "2024-01", "total_impor": 900.1, "barang_konsumsi": 90.0, "bahan_baku_penolong": 700.0, "barang_modal": 110.1}
    ]
    ImporRecord(**rows[0])


def test_parse_table_layout_change_raises():
    with pytest.raises(SourceUnavailable):
        satudata_exim.parse_table("<html></html>", "example", EKSPOR_COLUMNS, 2024)
    with pytest.raises(SourceUnavailable):
        satudata_exim.parse_table(_tables(2024), "impor", {"unknown col": "x"}, 2024)


def test_ekspor_extractor_posts_csrf_per_year():
    ext = EksporExtractor({"url": "https://example.test/x", "years": "2024,2025"})
    ext.http = _StubHttp()
    out = list(ext.extract())
    assert [r["periode"] for r in out] == ["2024-01", "2024-02", "2025-01", "2025-02"]
    assert ext.http.posts[0] == {"csrf_baseben": "tok1", "period": "2024"}
    assert ext.http.posts[1] == {"csrf_baseben": "tok2", "period": "2025"}


def test_impor_extractor_default_years_cover_every_offered_year():
    ext = ImporExtractor({"url": "https://example.test/x"})
    ext.http = _StubHttp()
    list(ext.extract())
    assert [p["period"] for p in ext.http.posts] == ["2016", "2024", "2025"]


def test_extractor_missing_form_raises():
    ext = EksporExtractor({"url": "https://example.test/x"})
    ext.http = _StubHttp(form="<html></html>")
    with pytest.raises(SourceUnavailable):
        list(ext.extract())


def test_extractor_unknown_year_raises():
    ext = EksporExtractor({"url": "https://example.test/x", "years": "1999"})
    ext.http = _StubHttp()
    with pytest.raises(SourceUnavailable):
        list(ext.extract())
