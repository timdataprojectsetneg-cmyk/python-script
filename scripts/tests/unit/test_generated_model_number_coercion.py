"""Generated models enable numeric-to-text coercion, including nested models."""

from decimal import Decimal

from ingestion.catalog.metadata_parser import to_pydantic_source


def test_generated_models_coerce_numbers_only_for_text_fields():
    source = to_pydantic_source("Record", [
        {"name": "label", "label": "Label", "type": "Text"},
        {"name": "volume", "label": "Volume", "type": "Decimal"},
        {"name": "year", "label": "Year", "type": "Integer"},
        {"name": "details", "label": "Details", "fields": [
            {"name": "code", "label": "Code", "type": "Text"},
        ]},
    ])
    namespace = {}
    exec(source, namespace)
    record = namespace["Record"]
    row = record(Label=123, Volume="123.45", Year=2025, Details={"Code": 456})
    assert record.model_config["coerce_numbers_to_str"] is True
    assert row.label == "123"
    assert row.details.code == "456"
    assert row.details.model_config["coerce_numbers_to_str"] is True
    assert row.volume == Decimal("123.45")
    assert isinstance(row.volume, Decimal)
    assert row.year == 2025
    assert isinstance(row.year, int)
    assert record(label=None).label is None
