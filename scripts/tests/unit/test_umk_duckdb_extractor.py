"""Tests for the DuckDB Excel extractor and the shared GoodStats UMK extractor."""

import pytest

from ingestion.core.extractors.duckdb_extractor import DuckDBExcelExtractor
from ingestion.exceptions import ConfigError
from ingestion.usecases.ketenagakerjaan.goodstats._umk import UMKExtractor, _to_int


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Rp4.162.965", 4162965),
        ("Rp3.619.466 ", 3619466),
        ("Rp3.921.088", 3921088),
        (4162965, 4162965),
        ("", None),
        ("Rp", None),
        (None, None),
    ],
)
def test_to_int_strips_currency(value, expected):
    assert _to_int(value) == expected


def test_umk_transform_maps_columns_to_model():
    extractor = UMKExtractor({"url": "s3://raw/goodstats/daftar-umk-aceh-2026.xlsx"})
    record = extractor.transform_row({"Kabupaten/Kota": "Kota Parepare\xa0", "UMK 2026": "Rp3.921.088"})
    assert record == {"kabupaten_kota": "Kota Parepare", "umk": 3921088, "tahun": 2026}


def test_umk_transform_year_falls_back_to_url():
    extractor = UMKExtractor({"url": "s3://raw/goodstats/simak-daftar-umk-lampung-2026.xlsx"})
    record = extractor.transform_row({"Kabupaten/Kota": "Kota Metro", "UMK": "Rp3.050.498"})
    assert record == {"kabupaten_kota": "Kota Metro", "umk": 3050498, "tahun": 2026}


def test_reference_translates_minio_and_passes_s3_through():
    assert DuckDBExcelExtractor({"url": "minio://raw/goodstats/x.xlsx"}).reference() == (
        "s3://raw/goodstats/x.xlsx"
    )
    assert DuckDBExcelExtractor({"url": "s3://raw/goodstats/x.xlsx"}).reference() == (
        "s3://raw/goodstats/x.xlsx"
    )
    with pytest.raises(ConfigError):
        DuckDBExcelExtractor({}).reference()


def test_read_xlsx_sql_options_and_escaping():
    extractor = DuckDBExcelExtractor(
        {
            "url": "s3://raw/goodstats/x.xlsx",
            "sheet": "UMK 2026",
            "header": "false",
            "range": "A1:B3",
        }
    )
    sql = extractor.read_xlsx_sql("s3://raw/goodstats/x.xlsx")
    assert sql == (
        "SELECT * FROM read_xlsx('s3://raw/goodstats/x.xlsx', sheet='UMK 2026', "
        "header=false, range='A1:B3', all_varchar=true)"
    )

    quoted = DuckDBExcelExtractor({"url": "x"}).read_xlsx_sql("s3://raw/a'b.xlsx")
    assert "'s3://raw/a''b.xlsx'" in quoted
