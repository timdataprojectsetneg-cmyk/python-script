"""Offline tests for FAO Indeks Harga Pangan."""

from ingestion.usecases.geopolitik.fao.indeks_harga_pangan.extractor import find_csv_link, parse_csv
from ingestion.usecases.geopolitik.fao.indeks_harga_pangan.models import Record

CSV = (
    "FAO Food Price Index,,,,,,,,\r\n"
    "2014-2016=100,,,,,,,,\r\n"
    "Date,Food Price Index,Meat,Dairy,Cereals,Oils,Sugar,,\r\n"
    ",,,,,,,,\r\n"
    "1990-01,64.4,74.3,53.5,64.1,44.59,87.9,,\r\n"
    "1990-02,64.7,,52.2,62.2,44.50,90.7,,\r\n"
)

HTML = """
<a href="/media/docs/x/ffpi-data-2026-10.xlsx?sfvrsn=1">xlsx</a>
<a href="/media/docs/x/food_price_indices_data.csv?sfvrsn=abc&amp;download=true">csv</a>
"""


def test_parse_csv_skips_headers_and_blank_rows():
    rows = parse_csv(CSV)
    assert [r["date"] for r in rows] == ["1990-01", "1990-02"]
    assert rows[0]["food_price_index"] == 64.4
    assert rows[1]["meat"] is None
    assert rows[1]["oils"] == 44.5


def test_find_csv_link_resolves_relative_and_unescapes():
    link = find_csv_link(HTML, "https://www.fao.org/worldfoodsituation/foodpricesindex/en/")
    assert link == (
        "https://www.fao.org/media/docs/x/food_price_indices_data.csv?sfvrsn=abc&download=true"
    )
    assert find_csv_link("<a href='/other'>x</a>", "https://www.fao.org/") is None


def test_record_validates_row():
    rec = Record(**parse_csv(CSV)[0])
    assert rec.date == "1990-01"
    assert rec.sugar == 87.9
