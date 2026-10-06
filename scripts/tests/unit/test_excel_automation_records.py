"""Tests for excel_automation record/format helpers."""

import json

import pandas as pd

from ingestion.core.extractors.excel_automation import (
    tables_to_records,
    to_records,
    write_tables,
)


def test_to_records_converts_nan_and_numpy():
    df = pd.DataFrame(
        {"a": pd.array([1, None], dtype="Int64"), "b": [1.5, float("nan")], "c": ["x", None]}
    )
    records = to_records(df)
    assert records[0] == {"a": 1, "b": 1.5, "c": "x"}
    assert records[1] == {"a": None, "b": None, "c": None}


def test_tables_to_records():
    tables = {"t": pd.DataFrame({"a": [1, 2]})}
    assert tables_to_records(tables) == {"t": [{"a": 1}, {"a": 2}]}


def test_write_tables_json_and_ndjson(tmp_path):
    tables = {"t": pd.DataFrame({"a": [1], "b": [None]})}

    json_path = write_tables(tables, str(tmp_path / "json"), "json")[0]
    assert json.loads(open(json_path, encoding="utf-8").read()) == [{"a": 1, "b": None}]

    ndjson_path = write_tables(tables, str(tmp_path / "ndjson"), "ndjson")[0]
    assert json.loads(open(ndjson_path, encoding="utf-8").read().strip()) == {"a": 1, "b": None}
