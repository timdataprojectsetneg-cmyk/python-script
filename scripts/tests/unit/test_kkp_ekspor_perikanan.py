"""Offline tests for Ekspor Perikanan KKP."""

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.kkp.ekspor_perikanan.extractor import (
    Extractor,
    parse_table,
    table_id_from_url,
)
from ingestion.usecases.geopolitik.kkp.ekspor_perikanan.models import Record

PAYLOAD = {
    "judul": "Nilai Ekspor Hasil Perikanan Menurut Komoditas Utama (satuan: USD 1.000)",
    "data": [
        {"VOLUME EKSPOR": "Rumput Laut ", "2019": "324849.98", "2020": "279582.59", "2026": "156249.34"},
        {"VOLUME EKSPOR": " TOTAL NILAI EKSPOR (USD 1.000) ", "2019": "5200000.10", "2020": None, "2026": "2995171.89"},
        {"VOLUME EKSPOR": "", "2019": "1"},
        "bukan-dict",
    ],
}


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.payload)


def test_table_id_from_url():
    assert table_id_from_url("https://portaldata.kkp.go.id/portals/data-statistik/exim/tbl-statis/d/156") == "156"
    with pytest.raises(ConfigError):
        table_id_from_url("https://portaldata.kkp.go.id/portals/data-statistik/exim/summary")


def test_parse_table_strips_names_and_drops_unnamed_rows():
    rows = parse_table(PAYLOAD)
    assert [r["komoditas"] for r in rows] == ["Rumput Laut", "TOTAL NILAI EKSPOR (USD 1.000)"]
    assert rows[0]["2019"] == "324849.98"


def test_parse_table_rejects_unexpected_payload():
    with pytest.raises(SourceUnavailable):
        parse_table({"message": "Not Found"})


def test_record_types_and_extra_year_columns():
    rec = Record(**parse_table(PAYLOAD)[0], **{"2027": "1.5"})
    assert rec.nilai_2019 == 324849.98
    assert rec.nilai_2021 is None
    dumped = rec.model_dump()
    assert dumped["nilai_2026"] == 156249.34
    assert dumped["2027"] == "1.5"


def test_extract_calls_sttk_endpoint_with_table_id():
    ext = Extractor({"url": "https://portaldata.kkp.go.id/portals/data-statistik/exim/tbl-statis/d/156"})
    ext.http = FakeHttp(PAYLOAD)
    rows = list(ext.extract())
    url, kwargs = ext.http.calls[0]
    assert url == "https://portaldata.kkp.go.id/sttk/api/static_table/view/detail"
    assert kwargs["params"] == {"id": "156"}
    assert len(rows) == 2


def test_extract_raises_on_empty_table():
    ext = Extractor({})
    ext.http = FakeHttp({"judul": "x", "data": []})
    with pytest.raises(SourceUnavailable):
        list(ext.extract())
