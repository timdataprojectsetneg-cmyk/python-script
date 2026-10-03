"""BPS WebAPI extractors: model-derived month maps and payload parsing."""

from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.api.extractor import (  # noqa: E501
    Extractor as CpiExtractor,
    strip_year_key,
    to_float,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.models import (
    Record as CpiRecord,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.api.extractor import (
    Extractor as MomExtractor,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.models import Record as MomRecord


def test_month_columns_and_label_map_derived_from_model():
    assert len(CpiRecord.month_columns()) == 12
    assert "tahun" not in CpiRecord.month_columns()
    assert CpiRecord.label_map()["january"] == "januari"
    assert CpiRecord.label_map()["desember"] == "desember"
    assert CpiRecord.value_columns() == CpiRecord.month_columns()

    assert MomRecord.month_columns() == CpiRecord.month_columns()
    assert MomRecord.value_columns() == MomRecord.month_columns() + ["tahunan"]
    assert MomRecord.label_map()["tahunan"] == "tahunan"


def test_strip_year_key_and_to_float():
    base = "https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/1"
    assert strip_year_key(base + "/th/126/key/ABC") == base
    assert to_float("105,5") == 105.5
    assert to_float("-") is None
    assert to_float(None) is None


def test_cpi_parse_payload():
    payload = {
        "status": "OK",
        "data-availability": "available",
        "var": [{"val": 2261}],
        "vervar": [{"val": 1, "label": "INDONESIA"}, {"val": 2, "label": "ACEH"}],
        "turvar": [{"val": 0, "label": "General"}],
        "tahun": [{"val": 126, "label": "2026"}],
        "turtahun": [{"val": 1, "label": "January"}, {"val": 13, "label": "Annual"}],
        "datacontent": {"1226101261": "105,5", "2226101261": 99.1},
    }
    extractor = CpiExtractor({"url": "https://webapi.bps.go.id/x", "api_key": "k"})
    rows = extractor._parse(payload, 2026)
    assert rows[0]["provinsi"] == "INDONESIA"
    assert rows[0]["januari"] == 105.5
    assert rows[0]["februari"] is None
    assert rows[0]["tahun"] == "2026"
    assert CpiRecord(**rows[0]).model_dump()["januari"] == 105.5


def test_mom_parse_payload_maps_tahunan():
    payload = {
        "status": "OK",
        "data-availability": "available",
        "var": [{"val": 1}],
        "vervar": [{"val": 10, "label": "KOTA MEDAN"}],
        "turvar": [],
        "tahun": [{"val": 126, "label": "2026"}],
        "turtahun": [{"val": 1, "label": "Januari"}, {"val": 13, "label": "Tahunan"}],
        "datacontent": {"10101261": 0.4, "101012613": 3.2},
    }
    extractor = MomExtractor({"url": "https://webapi.bps.go.id/x", "api_key": "k"})
    rows = extractor._parse(payload, 2026)
    assert rows[0]["kota_inflasi"] == "KOTA MEDAN"
    assert rows[0]["januari"] == 0.4
    assert rows[0]["tahunan"] == 3.2
    assert MomRecord(**rows[0]).model_dump()["tahunan"] == 3.2
