from __future__ import annotations

from ingestion.usecases.geopolitik.world_bank.profil_negara_mitra.extractor import DEFAULT_URL, Extractor
from ingestion.usecases.geopolitik.world_bank.profil_negara_mitra.models import Record
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer

ABW = {
    "id": "ABW",
    "iso2Code": "AW",
    "name": "Aruba",
    "region": {"id": "LCN", "iso2code": "ZJ", "value": "Latin America & Caribbean "},
    "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
    "capitalCity": "Oranjestad",
    "longitude": "-70.0167",
    "latitude": "12.5167",
}
AFE = {
    "id": "AFE",
    "name": "Africa Eastern and Southern",
    "region": {"id": "NA", "value": "Aggregates"},
    "incomeLevel": {"id": "NA", "value": "Aggregates"},
    "capitalCity": "",
    "longitude": "",
    "latitude": "",
}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload

    def get(self, url, **kwargs):
        return FakeResp(self.payload)


def make_extractor(rows):
    ex = Extractor({})
    ex.http = FakeHttp([{"page": 1, "pages": 1, "total": len(rows)}, rows])
    return ex


def test_default_url_is_catalog_url():
    assert Extractor({}).url == DEFAULT_URL == "https://api.worldbank.org/v2/country?format=json&per_page=400"


def test_extract_flattens_nested_labels():
    rows = list(make_extractor([ABW]).extract())
    assert rows == [
        {
            "id": "ABW",
            "name": "Aruba",
            "capitalCity": "Oranjestad",
            "region": "Latin America & Caribbean ",
            "incomeLevel": "High income",
            "latitude": "12.5167",
            "longitude": "-70.0167",
        }
    ]


def test_normalizer_cleans_strings_and_coerces_coordinates():
    normalizer = resolve_normalizer("geopolitik", "world_bank", "profil_negara_mitra", {})
    out = {r["id"]: r for r in normalizer.normalize(make_extractor([ABW, AFE]).extract())}
    assert out["ABW"]["region"] == "Latin America & Caribbean"
    assert out["ABW"]["latitude"] == 12.5167 and out["ABW"]["longitude"] == -70.0167
    assert out["ABW"]["capitalcity"] == "Oranjestad"
    assert out["ABW"]["incomelevel"] == "High income"
    assert out["AFE"]["capitalcity"] is None
    assert out["AFE"]["latitude"] is None
    assert out["AFE"]["region"] == "Aggregates"


def test_model_requires_id_and_registry():
    assert Record(id="IDN").name is None
    assert resolve_extractor_class("geopolitik", "world_bank", "profil_negara_mitra") is Extractor
