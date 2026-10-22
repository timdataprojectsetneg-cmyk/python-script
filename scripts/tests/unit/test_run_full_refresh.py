"""Tests for run --full-refresh: drop/create the table also when METHOD=upsert."""

import psycopg2
import psycopg2.extras
from click.testing import CliRunner

import ingestion.cli as cli
from ingestion.core.loaders.postgres_loader import PostgresLoader, _prepare_table
from psycopg2 import sql


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


class _Cursor:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, statement, params=None):
        self.log.append(_as_sql(statement))


class _Conn:
    def __init__(self, log):
        self.log = log

    def cursor(self):
        return _Cursor(self.log)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def close(self):
        pass


def _install_fake_db(monkeypatch, log):
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: _Conn(log))
    # ``query.as_string(conn)`` needs a real connection for identifier quoting.
    monkeypatch.setattr(
        psycopg2.extensions, "quote_ident", lambda ident, scope: '"%s"' % ident
    )
    monkeypatch.setattr(
        psycopg2.extras, "execute_values", lambda cur, query, values, **kw: log.append(query)
    )


def _config(**overrides):
    config = {
        "usecase": "ketenagakerjaan",
        "source": "kasus_perselisihan",
        "table": "data_y",
        "postgre_schema": "raw_x",
        "method": "upsert",
        "unique_key": "nomor_perkara",
    }
    config.update(overrides)
    return config


def test_prepare_table_upsert_keeps_table_without_full_refresh():
    log = []
    cur = _Cursor(log)

    _prepare_table(
        cur, sql, "raw_x", "data_y", ["nomor_perkara"], [{"nomor_perkara": "A"}],
        ["nomor_perkara"], "upsert", {}, "",
    )

    assert not any(statement.startswith("DROP TABLE") for statement in log)


def test_prepare_table_upsert_drops_table_with_full_refresh():
    log = []
    cur = _Cursor(log)

    _prepare_table(
        cur, sql, "raw_x", "data_y", ["nomor_perkara"], [{"nomor_perkara": "A"}],
        ["nomor_perkara"], "upsert", {}, "", full_refresh=True,
    )

    assert log[0] == "DROP TABLE IF EXISTS raw_x.data_y"
    assert any(statement.startswith("CREATE TABLE IF NOT EXISTS") for statement in log)
    assert any(statement.startswith("CREATE UNIQUE INDEX IF NOT EXISTS") for statement in log)


def test_loader_full_refresh_drops_and_still_upserts(monkeypatch):
    log = []
    _install_fake_db(monkeypatch, log)

    count = PostgresLoader(_config(full_refresh=True)).load([{"nomor_perkara": "A"}])

    assert count == 1
    assert "DROP TABLE IF EXISTS raw_x.data_y" in log
    assert any('ON CONFLICT ("nomor_perkara") DO UPDATE SET' in query for query in log)


def test_loader_upsert_without_full_refresh_does_not_drop(monkeypatch):
    log = []
    _install_fake_db(monkeypatch, log)

    PostgresLoader(_config()).load([{"nomor_perkara": "A"}])

    assert not any(statement.startswith("DROP TABLE") for statement in log)


def test_run_passes_full_refresh_to_execute_run(monkeypatch):
    calls = []

    def fake_execute(usecase, pub, src, mode, limit, use_dlt, targets, full_refresh=False, out=None):
        calls.append(full_refresh)
        return 0

    monkeypatch.setattr(cli, "execute_run", fake_execute)
    monkeypatch.setattr(cli, "_resolve_run_targets", lambda *a, **k: [("publisher", "source")])
    monkeypatch.setattr(cli, "_apply_env", lambda p: None)

    result = CliRunner().invoke(
        cli.run, ["--usecase", "ketenagakerjaan", "--env", "dev", "--full-refresh"]
    )

    assert result.exit_code == 0, result.output
    assert calls == [True]


def test_run_thread_passes_full_refresh_to_workers(monkeypatch):
    seen = []

    def fake_execute(usecase, pub, src, mode, limit, use_dlt, targets, full_refresh=False, out=None):
        seen.append(full_refresh)
        return 0

    monkeypatch.setattr(cli, "execute_run", fake_execute)
    monkeypatch.setattr(cli, "_resolve_run_targets", lambda *a, **k: [("p", "a"), ("p", "b")])
    monkeypatch.setattr(cli, "_apply_env", lambda p: None)

    result = CliRunner().invoke(
        cli.run,
        ["--usecase", "ketenagakerjaan", "--publisher", "p", "--thread", "2", "--env", "dev", "--full-refresh"],
    )

    assert result.exit_code == 0, result.output
    assert seen == [True, True]


def test_run_defaults_to_no_full_refresh(monkeypatch):
    calls = []

    def fake_execute(usecase, pub, src, mode, limit, use_dlt, targets, full_refresh=False, out=None):
        calls.append(full_refresh)
        return 0

    monkeypatch.setattr(cli, "execute_run", fake_execute)
    monkeypatch.setattr(cli, "_resolve_run_targets", lambda *a, **k: [("publisher", "source")])
    monkeypatch.setattr(cli, "_apply_env", lambda p: None)

    result = CliRunner().invoke(cli.run, ["--usecase", "ketenagakerjaan", "--env", "dev"])

    assert result.exit_code == 0, result.output
    assert calls == [False]
