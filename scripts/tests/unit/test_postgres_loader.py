"""PostgreSQL loader helpers: upsert batch de-duplication and table prep."""

from psycopg2 import sql

from ingestion.core.loaders.postgres_loader import _dedupe_rows, _prepare_table


def _as_sql(node) -> str:
    """Flatten a psycopg2.sql object to text without a live connection."""
    if isinstance(node, sql.Composed):
        return "".join(_as_sql(part) for part in node.seq)
    if isinstance(node, sql.Identifier):
        return ".".join(node._wrapped)
    if isinstance(node, sql.Literal):
        return repr(node._wrapped)
    if isinstance(node, sql.SQL):
        return node._wrapped
    return str(node)


class _FakeCursor:
    def __init__(self):
        self.statements = []

    def execute(self, statement, params=None):
        self.statements.append(_as_sql(statement))


ROWS = [{"nomor_perkara": "A", "nilai": 5}]


def test_prepare_table_replace_drops_then_creates_with_comment():
    cur = _FakeCursor()

    _prepare_table(
        cur, sql, "raw_x", "data_y", ["nomor_perkara", "nilai"], ROWS, [],
        "replace", {"nomor_perkara": "Nomor perkara."}, "https://example.org/sumber",
    )

    assert cur.statements[0] == "DROP TABLE IF EXISTS raw_x.data_y"
    assert any(s.startswith("CREATE TABLE IF NOT EXISTS raw_x.data_y") for s in cur.statements)
    assert "COMMENT ON TABLE raw_x.data_y IS 'https://example.org/sumber'" in cur.statements


def test_prepare_table_upsert_keeps_table_and_ensures_unique_index():
    cur = _FakeCursor()

    _prepare_table(
        cur, sql, "raw_x", "data_y", ["nomor_perkara", "nilai"], ROWS, ["nomor_perkara"],
        "upsert", {}, "",
    )

    assert not any(s.startswith("DROP TABLE") for s in cur.statements)
    assert any(s.startswith("CREATE UNIQUE INDEX IF NOT EXISTS") for s in cur.statements)
    assert not any(s.startswith("COMMENT ON TABLE") for s in cur.statements)



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
