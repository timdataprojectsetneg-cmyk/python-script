"""Offline tests for the Caldara-Iacoviello GPR index."""

import io

import pandas as pd
import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.caldara_iacoviello.indeks_risiko_geopolitik.extractor import (
    frame_to_records,
    read_frame,
)
from ingestion.usecases.geopolitik.caldara_iacoviello.indeks_risiko_geopolitik.models import Record


def _frame():
    return pd.DataFrame(
        {
            "month": pd.to_datetime(["1900-01-01", "1985-01-01", "1985-02-01"]),
            "GPR": [float("nan"), 102.5, 117.1],
            "GPRT": [float("nan"), 107.6, float("nan")],
            "GPRA": [float("nan"), 89.6, 96.6],
            "GPRH": [1.0, 2.0, 3.0],
        }
    )


def test_frame_to_records_drops_all_nan_rows_and_formats_month():
    rows = frame_to_records(_frame())
    assert [r["month"] for r in rows] == ["1985-01", "1985-02"]
    assert rows[0]["gpr"] == 102.5
    assert rows[1]["gprt"] is None


def test_missing_columns_raise():
    with pytest.raises(SourceUnavailable):
        frame_to_records(pd.DataFrame({"month": [], "GPR": []}))


def test_stata_roundtrip_and_model():
    buf = io.BytesIO()
    _frame().to_stata(buf, write_index=False)
    rows = frame_to_records(read_frame(buf.getvalue(), "https://x/data_gpr_export.dta"))
    rec = Record(**rows[0])
    assert rec.month == "1985-01"
    assert rec.gpra == 89.6
