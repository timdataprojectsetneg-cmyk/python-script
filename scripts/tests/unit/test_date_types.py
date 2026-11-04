"""Date/Datetime dictionary types -> Python date types -> Postgres DATE."""

from datetime import date, datetime

from ingestion.core.loaders.postgres_loader import _column_type, _json_dumps
from ingestion.catalog.metadata_parser import to_pydantic_source


def test_to_pydantic_source_maps_date_and_datetime():
    schema = [
        {"label": "Tanggal", "name": "tanggal", "type": "Date"},
        {"label": "Dicatat", "name": "dicatat", "type": "Datetime"},
        {"label": "Jumlah", "name": "jumlah", "type": "Integer"},
    ]
    source = to_pydantic_source("XRecord", schema)
    assert "from datetime import date as DateType, datetime as DateTimeType" in source
    assert "tanggal: DateType | None" in source
    assert "dicatat: DateTimeType | None" in source
    assert "jumlah: int | None" in source


def test_to_pydantic_source_date_field_does_not_shadow_type():
    schema = [{"label": "date", "name": "date", "type": "Date"}]
    source = to_pydantic_source("DateRecord", schema)
    namespace: dict = {}
    exec(source, namespace)
    assert "date" in namespace["DateRecord"].model_fields


def test_column_type_prefers_date_over_text():
    assert _column_type([date(2021, 8, 11)]) == "DATE"
    assert _column_type([datetime(2021, 8, 11, 10, 0)]) == "TIMESTAMPTZ"
    assert _column_type([date(2021, 8, 11), None]) == "DATE"
    assert _column_type(["2021-08-11"]) == "TEXT"
    assert _column_type([{"a": date(2021, 8, 11)}]) == "JSONB"


def test_json_dumps_handles_dates_inside_jsonb():
    payload = _json_dumps({"register": date(2021, 8, 11)})
    assert '"register": "2021-08-11"' in payload


def test_to_pydantic_source_maps_decimal():
    schema = [{"label": "Nilai", "name": "nilai", "type": "Decimal"}]
    source = to_pydantic_source("XRecord", schema)
    assert "from decimal import Decimal" in source
    assert "nilai: Decimal | None" in source
