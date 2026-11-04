"""DEV-only PostgreSQL loader backed by dlt.

This module is only used when ``--mode dev``. In production, Python emits NDJSON
and NiFi ``PutDatabaseRecord`` performs the load, so no DB credentials live here.
"""

from __future__ import annotations

from decimal import Decimal

from pathlib import Path
from typing import Any, Dict, Iterable
import importlib
import json
from datetime import date, datetime, timezone
from functools import lru_cache
import re

from ...config import HTTP_METHODS, get_raw, get_uri
from ...exceptions import ConfigError
from ..base.loader import BaseLoader


def _creds_from_uri(uri: str) -> Dict[str, Any]:
    """Parse a ``postgresql://user:pass@host:port/db`` URI into dlt creds."""
    from urllib.parse import unquote, urlparse

    parsed = urlparse(uri)
    return {
        "drivername": (parsed.scheme or "postgresql").split("+")[0],
        "database": (parsed.path or "").lstrip("/"),
        "username": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
    }


def _postgres_credentials() -> Dict[str, Any]:
    uri = get_uri("PG_URI")
    if uri:
        return _creds_from_uri(uri)
    host = get_raw("DEV__POSTGRES_HOST", "localhost")
    port = int(get_raw("DEV__POSTGRES_PORT", 5432))
    db = get_raw("DEV__POSTGRES_DB", "ingestion_dev")
    user = get_raw("DEV__POSTGRES_USER", "dev")
    password = get_raw("DEV__POSTGRES_PASSWORD", "")
    return {
        "drivername": "postgresql",
        "database": db,
        "username": user,
        "password": password,
        "host": host,
        "port": port,
    }


def _split_schema_table(value: Any, default_schema: str) -> tuple:
    """Split ``schema.table`` into ``(schema, table)``; table-only uses the default."""
    text = (value or "").strip()
    if not text:
        return default_schema, None
    if "." in text:
        schema, table = text.split(".", 1)
        return (schema.strip() or default_schema), (table.strip() or None)
    return default_schema, text


def _run_ddl(cur: Any, query: Any) -> None:
    """Run a DDL statement, ignoring duplicates created by concurrent loads.

    ``IF NOT EXISTS`` is not race-free: the CLI loads sources in threads, so two
    loads can pass the existence check together and one then fails on the catalog
    unique constraint (``pg_namespace_nspname_index`` for a schema, ``pg_class``
    for a table/index). The statement runs under a savepoint so a duplicate is
    treated as "already exists" and the surrounding transaction stays usable.
    """
    from psycopg2 import errors

    cur.execute("SAVEPOINT setneg_ddl")
    try:
        cur.execute(query)
    except (errors.UniqueViolation, errors.DuplicateSchema, errors.DuplicateTable):
        cur.execute("ROLLBACK TO SAVEPOINT setneg_ddl")
    else:
        cur.execute("RELEASE SAVEPOINT setneg_ddl")


def _ensure_schema(schema: str) -> None:
    """Create the target schema if it does not exist yet."""
    import psycopg2
    from psycopg2 import sql

    creds = _postgres_credentials()
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["username"],
        password=creds["password"],
    )
    try:
        with conn, conn.cursor() as cur:
            _run_ddl(
                cur,
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)),
            )
    finally:
        conn.close()


def _unique_keys(config: Dict[str, Any]) -> list[str]:
    """Parse ``UNIQUE_KEY`` into a list of columns.

    Accepts comma/semicolon-separated values and supports more than two keys.
    """
    value = config.get("unique_key")
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").replace(";", ",").split(",") if item.strip()]


def _dedupe_rows(rows: list[Dict[str, Any]], keys: list[str]) -> list[Dict[str, Any]]:
    """Collapse rows sharing a full unique key, keeping the last occurrence.

    ``INSERT ... ON CONFLICT DO UPDATE`` fails if the same constrained value is
    proposed twice in one statement. Rows with a missing key part are kept as-is
    (they cannot be deduplicated reliably).
    """
    if not keys:
        return rows
    index_by_key: Dict[tuple, int] = {}
    result: list[Dict[str, Any]] = []
    for row in rows:
        key = tuple(row.get(k) for k in keys)
        if any(value is None for value in key):
            result.append(row)
            continue
        if key in index_by_key:
            result[index_by_key[key]] = row
        else:
            index_by_key[key] = len(result)
            result.append(row)
    return result


def _load_method(config: Dict[str, Any]) -> str:
    """Resolve the load method: ``replace`` (default) or ``upsert``.

    ``METHOD`` may still carry a legacy HTTP verb for API sources; those are
    ignored here and fall back to the default ``replace``.
    """
    method = str(config.get("method") or "").strip().lower()
    if not method:
        legacy = str(config.get("write_disposition") or "").strip().lower()
        method = {"merge": "upsert", "truncate_insert": "replace"}.get(legacy, "replace")
    if method.upper() in HTTP_METHODS:
        method = "replace"
    if method not in ("replace", "upsert"):
        raise ConfigError("METHOD must be 'replace' or 'upsert'")
    return method


def read_watermark(config: Dict[str, Any]) -> str | None:
    """Return ``max(TIMESTAMP_KEY)`` of the target table for incremental upsert.

    ``None`` means "no filter": not an upsert, no ``TIMESTAMP_KEY``, a full refresh,
    or a target table that does not exist yet or has no rows.
    """
    column = str(config.get("timestamp_key") or "").strip()
    if not column or _load_method(config) != "upsert" or config.get("full_refresh"):
        return None

    import psycopg2
    from psycopg2 import sql

    default_schema = get_raw("DEV__POSTGRES_DATASET", "ingestion_dev")
    schema, table = _split_schema_table(
        config.get("postgre_table") or config.get("table"),
        config.get("postgre_schema") or default_schema,
    )
    table = table or config.get("source")
    creds = _postgres_credentials()
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["username"],
        password=creds["password"],
    )
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (f"{schema}.{table}",))
            if cur.fetchone()[0] is None:
                return None
            cur.execute(
                sql.SQL("SELECT max({}) FROM {}.{}").format(
                    sql.Identifier(column), sql.Identifier(schema), sql.Identifier(table)
                )
            )
            value = cur.fetchone()[0]
    finally:
        conn.close()
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


_METADATA_TYPES = {
    "_source": "TEXT",
    "_source_url": "TEXT",
    "_published_date": "DATE",
    "_created_at": "TIMESTAMP WITH TIME ZONE",
    "_modified_at": "TIMESTAMP WITH TIME ZONE",
}
_METADATA_DEFAULTS = {
    "_created_at": "DEFAULT CURRENT_TIMESTAMP",
    "_modified_at": "DEFAULT CURRENT_TIMESTAMP",
}
_METADATA_COLUMNS = tuple(_METADATA_TYPES)


def _parse_published_date(value: Any) -> date | None:
    """Parse ``YYYY`` / ``YYYY-MM`` / ``YYYY-MM-DD``; other strings become NULL."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    match = re.fullmatch(r"(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", text)
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    try:
        return date(year, month, day)
    except ValueError:
        return None


_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"


@lru_cache(maxsize=32)
def _read_docs_sources(docs_dir: str, _mtime: float) -> list[Dict[str, Any]]:
    """Parse one usecase.md; the mtime argument invalidates the cache."""
    from ...catalog.docs_reader import read_usecase_sources

    return read_usecase_sources(Path(docs_dir))


def _clean_url(value: Any) -> str | None:
    text = str(value or "").strip()
    return None if text in ("", "-", "–", "—") else text


def _docs_metadata(
    config: Dict[str, Any], docs_root: Path | None = None
) -> tuple[Any, Any, Any]:
    """Read publisher, last update and source URL from ``docs/<usecase>/usecase.md``.

    The generated docs are the local copy of the catalog, so the loader can use
    those columns without duplicating them in every env file.
    """
    from ...catalog.metadata_parser import derive_module_name, publisher_slug, source_slug

    usecase = str(config.get("usecase") or "").strip()
    publisher = str(config.get("publisher") or "").strip()
    source = str(config.get("source") or "").strip()
    if not (usecase and publisher and source):
        return None, None, None

    docs_dir = Path(docs_root or _DOCS_ROOT) / derive_module_name(usecase)
    try:
        mtime = (docs_dir / "usecase.md").stat().st_mtime
        sources = _read_docs_sources(str(docs_dir), mtime)
    except Exception:  # noqa: BLE001 - docs are optional for the loader
        return None, None, None

    for item in sources:
        if (
            publisher_slug(item) == publisher.lower()
            and source_slug(item) == source.lower()
        ):
            return (
                item.get("publisher"),
                item.get("last_update"),
                _clean_url(item.get("source_link") or item.get("resource_url")),
            )
    return None, None, None


def _metadata_values(
    config: Dict[str, Any], docs_root: Path | None = None
) -> Dict[str, Any]:
    docs_publisher, docs_last_update, docs_source_url = _docs_metadata(config, docs_root)
    source = str(
        config.get("publisher_name") or docs_publisher or config.get("publisher") or ""
    ).strip() or None
    source_url = str(
        config.get("source_url")
        or docs_source_url
        or config.get("source_link")
        or config.get("url")
        or ""
    ).strip() or None
    last_update = config.get("last_update")
    if last_update in (None, ""):
        last_update = docs_last_update
    return {
        "_source": source,
        "_source_url": source_url,
        "_published_date": _parse_published_date(last_update),
    }


def _apply_metadata(
    rows: list[Dict[str, Any]],
    config: Dict[str, Any],
    *,
    reset_created_at: bool = False,
    docs_root: Path | None = None,
) -> list[Dict[str, Any]]:
    """Attach loader lineage columns.

    ``_created_at`` is preserved on upserts; ``reset_created_at`` is set for a
    ``--full-refresh`` load so the recreated table gets a new creation time.
    """
    values = _metadata_values(config, docs_root)
    now = datetime.now(timezone.utc)
    for row in rows:
        row.update(values)
        if reset_created_at:
            row["_created_at"] = now
        else:
            row.setdefault("_created_at", now)
        row["_modified_at"] = now
    return rows


def _column_type(values: list[Any]) -> str:
    """Choose a conservative PostgreSQL type from normalized Python values."""
    non_null = [value for value in values if value is not None]
    if non_null and all(isinstance(value, bool) for value in non_null):
        return "BOOLEAN"
    if non_null and all(isinstance(value, (dict, list)) for value in non_null):
        return "JSONB"
    if non_null and all(isinstance(value, int) and not isinstance(value, bool) for value in non_null):
        return "BIGINT"
    if any(isinstance(value, Decimal) for value in non_null) and all(
        isinstance(value, (Decimal, int)) and not isinstance(value, bool) for value in non_null
    ):
        return "NUMERIC"
    if non_null and all(isinstance(value, float) for value in non_null):
        return "DOUBLE PRECISION"
    if non_null and all(isinstance(value, datetime) for value in non_null):
        return "TIMESTAMPTZ"
    if non_null and all(isinstance(value, date) for value in non_null):
        return "DATE"
    return "TEXT"


def _model_record(config: Dict[str, Any]) -> Any:
    """Import and return the use-case Pydantic ``Record`` model, or None."""
    module_name = ".".join(("ingestion", "usecases", config.get("usecase", ""), config.get("publisher", ""), config.get("source", ""), "models"))
    try:
        model = importlib.import_module(module_name)
        return getattr(model, "Record", None)
    except (ImportError, AttributeError, ValueError):
        return None


def _model_columns(config: Dict[str, Any]) -> list[str]:
    """Return fields from the use-case Pydantic Record model when available."""
    record = _model_record(config)
    return list(getattr(record, "model_fields", {}) or {})


def _model_comments(config: Dict[str, Any]) -> Dict[str, str]:
    """Column comments from the Record model's ``Field(description=...)`` values."""
    record = _model_record(config)
    comments: Dict[str, str] = {}
    for name, info in (getattr(record, "model_fields", {}) or {}).items():
        description = getattr(info, "description", None)
        if description:
            comments[name] = str(description)
    return comments


def _json_dumps(value: Any) -> str:
    """JSON-encode a JSONB value, stringifying date/datetime objects (ISO)."""
    return json.dumps(value, ensure_ascii=False, default=str)


def _ensure_table(
    cur: Any,
    sql: Any,
    schema: str,
    table: str,
    columns: list[str],
    rows: list[Dict[str, Any]],
    keys: list[str],
) -> None:
    """Create a missing table from the Pydantic fields and observed values."""
    observed = list(dict.fromkeys(column for row in rows for column in row))
    ordered = list(dict.fromkeys(columns + observed))
    definitions = []
    for column in ordered:
        column_type = _METADATA_TYPES.get(column) or _column_type([row.get(column) for row in rows])
        default = _METADATA_DEFAULTS.get(column, "")
        definitions.append(
            sql.SQL("{} {}{}").format(
                sql.Identifier(column),
                sql.SQL(column_type),
                sql.SQL(f" {default}" if default else ""),
            )
        )
    if keys:
        definitions.append(sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(sql.Identifier(key) for key in keys)))
    _run_ddl(
        cur,
        sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({})").format(sql.Identifier(schema), sql.Identifier(table), sql.SQL(", ").join(definitions)),
    )


def _apply_comments(
    cur: Any,
    sql: Any,
    schema: str,
    table: str,
    columns: list[str],
    comments: Dict[str, str],
    table_comment: str = "",
) -> None:
    """Refresh metadata comments from the dictionary (column + table)."""
    for column in columns:
        comment = comments.get(column)
        if comment:
            cur.execute(
                sql.SQL("COMMENT ON COLUMN {}.{}.{} IS {}").format(
                    sql.Identifier(schema),
                    sql.Identifier(table),
                    sql.Identifier(column),
                    sql.Literal(comment),
                )
            )
    if table_comment:
        cur.execute(
            sql.SQL("COMMENT ON TABLE {}.{} IS {}").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Literal(table_comment),
            )
        )


def _has_unique_key(cur: Any, schema: str, table: str, keys: list[str]) -> bool:
    """Return whether a table has a unique index or constraint on ``keys``."""
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM pg_index AS idx
            JOIN pg_class AS rel ON rel.oid = idx.indrelid
            JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace
            WHERE ns.nspname = %s
              AND rel.relname = %s
              AND idx.indisunique
              AND (
                  SELECT array_agg(att.attname ORDER BY key.ordinality)
                  FROM unnest(idx.indkey) WITH ORDINALITY AS key(attnum, ordinality)
                  JOIN pg_attribute AS att
                    ON att.attrelid = idx.indrelid
                   AND att.attnum = key.attnum
              ) = %s
        )
        """,
        (schema, table, keys),
    )
    return bool(cur.fetchone()[0])


def _ensure_unique_index(cur: Any, sql: Any, schema: str, table: str, keys: list[str]) -> None:
    """Ensure ``keys`` are backed by a unique index or constraint."""
    if not keys or _has_unique_key(cur, schema, table, keys):
        return
    index_name = "uq_" + "_".join([table] + keys)[:60]
    _run_ddl(
        cur,
        sql.SQL("CREATE UNIQUE INDEX IF NOT EXISTS {} ON {}.{} ({})").format(
            sql.Identifier(index_name),
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(key) for key in keys),
        ),
    )


def _ensure_timestamp_index(cur: Any, sql: Any, schema: str, table: str, column: str) -> None:
    """Index ``TIMESTAMP_KEY`` so the incremental ``max(...)`` watermark stays cheap."""
    if not column:
        return
    index_name = "ix_" + "_".join([table, column])[:60]
    _run_ddl(
        cur,
        sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} ({})").format(
            sql.Identifier(index_name),
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.Identifier(column),
        ),
    )


def _ensure_metadata_columns(cur: Any, sql: Any, schema: str, table: str) -> None:
    """Add lineage columns to a table created by an older loader version."""
    for column in _METADATA_COLUMNS:
        default = _METADATA_DEFAULTS.get(column, "")
        cur.execute(
            sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS {} {}{}").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Identifier(column),
                sql.SQL(_METADATA_TYPES[column]),
                sql.SQL(f" {default}" if default else ""),
            )
        )


def _prepare_table(
    cur: Any,
    sql: Any,
    schema: str,
    table: str,
    columns: list[str],
    rows: list[Dict[str, Any]],
    keys: list[str],
    method: str,
    comments: Dict[str, str],
    table_comment: str,
    full_refresh: bool = False,
    timestamp_key: str = "",
) -> Any:
    """Create/refresh the target table and its comments for the current load.

    ``replace`` drops the table first so column types and comments are rebuilt
    from the current model/extractor result; ``upsert`` keeps the existing table
    but refreshes comments and ensures the unique index — unless ``full_refresh``
    forces the drop anyway. ``TIMESTAMP_KEY`` is indexed whenever it is set.
    """
    qualified = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table))
    if method == "replace" or full_refresh:
        cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(qualified))
    _ensure_table(cur, sql, schema, table, columns, rows, keys)
    _ensure_metadata_columns(cur, sql, schema, table)
    _apply_comments(cur, sql, schema, table, columns, comments, table_comment)
    if method == "upsert":
        _ensure_unique_index(cur, sql, schema, table, keys)
    _ensure_timestamp_index(cur, sql, schema, table, timestamp_key)
    return qualified


class PostgresLoader(BaseLoader):
    """DEV PostgreSQL loader using psycopg2 and a fixed existing schema."""

    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        try:
            import psycopg2
            from psycopg2 import sql
            from psycopg2.extras import Json, execute_values
        except ImportError as exc:
            raise ConfigError("DEV PostgreSQL load requires the 'psycopg2-binary' package") from exc

        default_schema = get_raw("DEV__POSTGRES_DATASET", "ingestion_dev")
        schema, table = _split_schema_table(
            self.config.get("postgre_table") or self.config.get("table"),
            self.config.get("postgre_schema") or default_schema,
        )
        table = table or self.config.get("source")
        method = _load_method(self.config)
        keys = _unique_keys(self.config)
        if method == "upsert" and not keys:
            raise ConfigError("UNIQUE_KEY is required when METHOD=upsert")
        if method == "upsert":
            # Each constrained value may appear only once per INSERT ... ON CONFLICT
            # statement, so collapse duplicate keys within the batch (keep the last).
            rows = _dedupe_rows(rows, keys)

        full_refresh = bool(self.config.get("full_refresh"))
        rows = _apply_metadata(
            rows, self.config, reset_created_at=full_refresh
        )

        _ensure_schema(schema)
        creds = _postgres_credentials()
        columns = list(dict.fromkeys(key for row in rows for key in row))
        model_fields = _model_columns(self.config)
        comments = _model_comments(self.config)
        columns = list(dict.fromkeys(model_fields + columns))
        for column in _METADATA_COLUMNS:
            if column not in columns:
                columns.append(column)
        if not columns:
            return 0
        table_comment = str(_metadata_values(self.config).get("_source_url") or "").strip()
        conn = psycopg2.connect(host=creds["host"], port=creds["port"], dbname=creds["database"], user=creds["username"], password=creds["password"])
        try:
            with conn, conn.cursor() as cur:
                qualified = _prepare_table(
                    cur,
                    sql,
                    schema,
                    table,
                    columns,
                    rows,
                    keys,
                    method,
                    comments,
                    table_comment,
                    full_refresh,
                    str(self.config.get("timestamp_key") or "").strip(),
                )
                column_sql = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
                values = [
                    [
                        Json(row.get(column), dumps=_json_dumps)
                        if isinstance(row.get(column), (dict, list))
                        else row.get(column)
                        for column in columns
                    ]
                    for row in rows
                ]
                query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(qualified, column_sql)
                if method == "upsert":
                    updates = [
                        column
                        for column in columns
                        if column not in keys
                        and (column != "_created_at" or full_refresh)
                    ]
                    if updates:
                        query += sql.SQL(" ON CONFLICT ({}) DO UPDATE SET {}" ).format(
                            sql.SQL(", ").join(sql.Identifier(key) for key in keys),
                            sql.SQL(", ").join(sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column)) for column in updates),
                        )
                    else:
                        query += sql.SQL(" ON CONFLICT ({}) DO NOTHING").format(sql.SQL(", ").join(sql.Identifier(key) for key in keys))
                execute_values(cur, query.as_string(conn), values)
        finally:
            conn.close()
        return len(rows)


class DltPostgresLoader(BaseLoader):
    """Optional legacy DEV loader selected with ``--use-dlt``."""

    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        try:
            import dlt
            from dlt.destinations import postgres as postgres_destination
        except ImportError as exc:
            raise ConfigError("DEV dlt load requires the 'dlt[postgres]' package") from exc
        default_schema = get_raw("DEV__POSTGRES_DATASET", "ingestion_dev")
        schema, table = _split_schema_table(self.config.get("postgre_table"), self.config.get("postgre_schema") or default_schema)
        table = table or self.config.get("source")
        method = _load_method(self.config)
        keys = _unique_keys(self.config)
        if method == "upsert" and not keys:
            raise ConfigError("UNIQUE_KEY is required when METHOD=upsert")
        full_refresh = bool(self.config.get("full_refresh"))
        rows = _apply_metadata(
            rows, self.config, reset_created_at=full_refresh
        )
        # A recreated table is empty, so "replace" loads the same as a merge.
        disposition = (
            "replace"
            if full_refresh or method != "upsert"
            else "merge"
        )
        pipeline = dlt.pipeline(pipeline_name=f"ingestion_{self.config.get('usecase')}", destination=postgres_destination(credentials=_postgres_credentials()), dataset_name=schema)
        pipeline.run(dlt.resource(rows, name=table, write_disposition=disposition, primary_key=keys or None))
        return len(rows)
