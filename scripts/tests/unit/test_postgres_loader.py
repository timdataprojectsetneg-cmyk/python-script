"""PostgreSQL loader helpers: upsert batch de-duplication."""

from ingestion.core.loaders.postgres_loader import _dedupe_rows


def test_dedupe_keeps_last_occurrence():
    rows = [
        {"nomor_perkara": "A", "v": 1},
        {"nomor_perkara": "B", "v": 2},
        {"nomor_perkara": "A", "v": 3},
    ]
    out = _dedupe_rows(rows, ["nomor_perkara"])
    assert [r["nomor_perkara"] for r in out] == ["A", "B"]
    assert out[0]["v"] == 3


def test_dedupe_keeps_missing_key_rows():
    rows = [
        {"nomor_perkara": None, "v": 1},
        {"nomor_perkara": None, "v": 2},
        {"nomor_perkara": "A", "v": 3},
        {"nomor_perkara": "A", "v": 4},
    ]
    out = _dedupe_rows(rows, ["nomor_perkara"])
    assert sum(1 for r in out if r["nomor_perkara"] is None) == 2
    assert sum(1 for r in out if r["nomor_perkara"] == "A") == 1


def test_dedupe_composite_key_and_no_keys():
    rows = [{"a": 1, "b": 1}, {"a": 1, "b": 2}, {"a": 1, "b": 1}]
    assert _dedupe_rows(rows, ["a", "b"]) == [{"a": 1, "b": 1}, {"a": 1, "b": 2}]
    assert _dedupe_rows(rows, []) is rows
