"""PostgreSQL loader helpers: upsert batch de-duplication and table prep."""

import psycopg2
import pytest
from psycopg2 import sql

from ingestion.core.loaders.postgres_loader import _dedupe_rows, _prepare_table, _run_ddl


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


class _DuplicateCursor(_FakeCursor):
    """Raises the concurrent-DDL unique violation on every CREATE statement."""

    def __init__(self, error=None):
        super().__init__()
        self.error = error or psycopg2.errors.UniqueViolation("duplicate key value")

    def execute(self, statement, params=None):
        if _as_sql(statement).startswith("CREATE"):
            raise self.error
        super().execute(statement, params)


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


def test_run_ddl_releases_savepoint_on_success():
    cur = _FakeCursor()

    _run_ddl(cur, sql.SQL("CREATE TABLE IF NOT EXISTS raw_x.data_y (a TEXT)"))

    assert cur.statements == [
        "SAVEPOINT setneg_ddl",
        "CREATE TABLE IF NOT EXISTS raw_x.data_y (a TEXT)",
        "RELEASE SAVEPOINT setneg_ddl",
    ]


def test_run_ddl_ignores_concurrent_duplicate_error():
    cur = _DuplicateCursor()

    _run_ddl(cur, sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier("raw_goodstats")))

    assert cur.statements[-1] == "ROLLBACK TO SAVEPOINT setneg_ddl"
    assert not any(s.startswith("RELEASE SAVEPOINT") for s in cur.statements)


def test_run_ddl_ignores_duplicate_schema_and_table_errors():
    for error in (psycopg2.errors.DuplicateSchema("ada"), psycopg2.errors.DuplicateTable("ada")):
        cur = _DuplicateCursor(error)

        _run_ddl(cur, sql.SQL("CREATE TABLE IF NOT EXISTS raw_x.data_y (a TEXT)"))

        assert cur.statements[-1] == "ROLLBACK TO SAVEPOINT setneg_ddl"


def test_prepare_table_survives_duplicate_error_from_concurrent_load():
    cur = _DuplicateCursor()

    _prepare_table(
        cur, sql, "raw_x", "data_y", ["nomor_perkara", "nilai"], ROWS, ["nomor_perkara"],
        "upsert", {}, "",
    )

    assert cur.statements.count("ROLLBACK TO SAVEPOINT setneg_ddl") == 2
    assert not any(s.startswith("RELEASE SAVEPOINT") for s in cur.statements)


def test_run_ddl_reraises_other_errors():
    cur = _DuplicateCursor(psycopg2.errors.InsufficientPrivilege("denied"))

    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        _run_ddl(cur, sql.SQL("CREATE TABLE IF NOT EXISTS raw_x.data_y (a TEXT)"))



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
