from __future__ import annotations

import pytest
from ingestion.usecases.kunjungan_presiden.bmkg.prakiraan_cuaca.models import Record
from ingestion.usecases.kunjungan_presiden.bmkg.prakiraan_cuaca.extractor import Extractor


def test_bmkg_cuaca_model_validation():
    raw_data = {
        "adm4": "31.71.03.1001",
        "provinsi": "DKI Jakarta",
        "kotkab": "Kota Adm. Jakarta Pusat",
        "kecamatan": "Kemayoran",
        "desa": "Kemayoran",
        "lon": 106.84538,
        "lat": -6.16472,
        "timezone": "+0700",
        "local_datetime": "2026-10-14 12:00:00",
        "t": 32.0,
        "hu": 58.0,
        "weather_desc": "Cerah",
        "ws": 14.1,
        "wd": "NW",
        "tcc": 47.0,
    }
    rec = Record(**raw_data)
    assert rec.adm4 == "31.71.03.1001"
    assert rec.t == 32.0
    assert rec.weather_desc == "Cerah"
    dumped = rec.model_dump()
    assert dumped["desa"] == "Kemayoran"


def test_bmkg_cuaca_extractor_records_from():
    sample_payload = {
        "lokasi": {
            "adm4": "31.71.03.1001",
            "provinsi": "DKI Jakarta",
            "kotkab": "Jakarta Pusat",
            "kecamatan": "Kemayoran",
            "desa": "Kemayoran",
            "lon": 106.84,
            "lat": -6.16,
            "timezone": "Asia/Jakarta",
        },
        "data": [
            {
                "cuaca": [
                    [
                        {
                            "local_datetime": "2026-10-14 12:00:00",
                            "t": 32,
                            "hu": 55,
                            "weather_desc": "Cerah",
                            "ws": 10.5,
                            "wd": "N",
                            "tcc": 20,
                        },
                        {
                            "local_datetime": "2026-10-14 15:00:00",
                            "t": 30,
                            "hu": 60,
                            "weather_desc": "Hujan Ringan",
                            "ws": 12.0,
                            "wd": "NW",
                            "tcc": 80,
                        },
                    ]
                ]
            }
        ],
    }
    extractor = Extractor({"url": "https://dummy.bmkg.go.id"})
    records = extractor._records_from(sample_payload)
    assert len(records) == 2
    assert records[0]["adm4"] == "31.71.03.1001"
    assert records[0]["desa"] == "Kemayoran"
    assert records[0]["weather_desc"] == "Cerah"
    assert records[1]["weather_desc"] == "Hujan Ringan"
