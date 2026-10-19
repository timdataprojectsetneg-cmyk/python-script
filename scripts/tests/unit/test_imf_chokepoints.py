from __future__ import annotations

import pytest
from ingestion.usecases.geopolitik.imf.chokepoints_maritim.models import Record
from ingestion.usecases.geopolitik.imf.chokepoints_maritim.extractor import Extractor


def test_imf_chokepoint_model_validation():
    raw_data = {
        "date": "2026-10-04",
        "year": 2026,
        "month": 10,
        "day": 4,
        "portid": "chokepoint5",
        "portname": "Malacca Strait",
        "n_container": 52,
        "n_dry_bulk": 59,
        "n_general_cargo": 19,
        "n_roro": 4,
        "n_tanker": 75,
        "n_cargo": 134,
        "n_total": 209,
        "capacity_container": 1838433.0,
        "capacity_dry_bulk": 2790327.0,
        "capacity_general_cargo": 100101.0,
        "capacity_roro": 11895.0,
        "capacity_tanker": 3758366.0,
        "capacity_cargo": 4740758.0,
        "capacity": 8499124.0,
        "ObjectId": 15770,
    }
    rec = Record(**raw_data)
    assert rec.portid == "chokepoint5"
    assert rec.portname == "Malacca Strait"
    assert rec.n_total == 209
    assert rec.object_id == 15770
    dumped = rec.model_dump()
    assert dumped["date"] == "2026-10-04"
    assert dumped["n_tanker"] == 75


def test_imf_chokepoint_extractor_records_from():
    sample_payload = {
        "features": [
            {
                "attributes": {
                    "date": "2026-10-04",
                    "portid": "chokepoint1",
                    "portname": "Suez Canal",
                    "n_total": 46,
                    "ObjectId": 2875,
                }
            },
            {
                "attributes": {
                    "date": "2026-10-04",
                    "portid": "chokepoint4",
                    "portname": "Bab el-Mandeb Strait",
                    "n_total": 34,
                    "ObjectId": 11037,
                }
            },
        ]
    }
    extractor = Extractor({"url": "https://dummy.arcgis.com"})
    records = extractor._records_from(sample_payload)
    assert len(records) == 2
    assert records[0]["portid"] == "chokepoint1"
    assert records[0]["portname"] == "Suez Canal"
    assert records[1]["portname"] == "Bab el-Mandeb Strait"
