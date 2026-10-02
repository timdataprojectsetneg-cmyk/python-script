"""DEV-only PostgreSQL loader backed by dlt.

This module is only used when ``--mode dev``. In production, Python emits NDJSON
and NiFi ``PutDatabaseRecord`` performs the load, so no DB credentials live here.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable
from uuid import uuid4
import importlib
import json
from datetime import datetime, date

from ...config import HTTP_METHODS, get_raw
from ...exceptions import ConfigError
from ..base.loader import BaseLoader


def _postgres_credentials() -> Dict[str, Any]:
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
            cur.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema))
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


def _column_type(values: list[Any]) -> str:
    """Choose a conservative PostgreSQL type from normalized Python values."""
    non_null = [value for value in values if value is not None]
    if non_null and all(isinstance(value, bool) for value in non_null):
        return "BOOLEAN"
    if non_null and all(isinstance(value, (dict, list)) for value in non_null):
        return "JSONB"
    if non_null and all(isinstance(value, int) and not isinstance(value, bool) for value in non_null):
        return "BIGINT"
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
    comments: Dict[str, str],
) -> None:
    """Create a missing table from the Pydantic fields and observed values."""
    observed = list(dict.fromkeys(column for row in rows for column in row))
    ordered = list(dict.fromkeys(columns + observed))
    definitions = []
    for column in ordered:
        definitions.append(sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(_column_type([row.get(column) for row in rows]))))
    if keys:
        definitions.append(sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(sql.Identifier(key) for key in keys)))
    cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({})").format(sql.Identifier(schema), sql.Identifier(table), sql.SQL(", ").join(definitions)))
    for column in ordered:
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


def _ensure_unique_index(cur: Any, sql: Any, schema: str, table: str, keys: list[str]) -> None:
    """Ensure a unique index on ``keys`` so ``ON CONFLICT`` can target it.

    Needed when the table already existed (e.g. created by a previous
    ``replace`` load) without a matching primary key/unique constraint.
    """
    if not keys:
        return
    index_name = "uq_" + "_".join([table] + keys)[:60]
    cur.execute(
        sql.SQL("CREATE UNIQUE INDEX IF NOT EXISTS {} ON {}.{} ({})").format(
            sql.Identifier(index_name),
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(key) for key in keys),
        )
    )


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

        timestamp_column = str(self.config.get("load_timestamp_column") or "loaded_at").strip()
        if timestamp_column:
            from datetime import datetime, timezone
            stamp = datetime.now(timezone.utc)
            rows = [{**row, timestamp_column: row.get(timestamp_column) or stamp} for row in rows]

        _ensure_schema(schema)
        creds = _postgres_credentials()
        columns = list(dict.fromkeys(key for row in rows for key in row))
        model_fields = _model_columns(self.config)
        comments = _model_comments(self.config)
        columns = list(dict.fromkeys(model_fields + columns))
        if timestamp_column and timestamp_column not in columns:
            columns.append(timestamp_column)
        if not columns:
            return 0
        conn = psycopg2.connect(host=creds["host"], port=creds["port"], dbname=creds["database"], user=creds["username"], password=creds["password"])
        try:
            with conn, conn.cursor() as cur:
                qualified = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table))
                _ensure_table(cur, sql, schema, table, columns, rows, keys, comments)
                if method == "upsert":
                    _ensure_unique_index(cur, sql, schema, table, keys)
                if method == "replace":
                    cur.execute(sql.SQL("TRUNCATE TABLE {}" ).format(qualified))
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
                    updates = [column for column in columns if column not in keys]
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
        pipeline = dlt.pipeline(pipeline_name=f"ingestion_{self.config.get('usecase')}", destination=postgres_destination(credentials=_postgres_credentials()), dataset_name=schema)
        pipeline.run(dlt.resource(rows, name=table, write_disposition="merge" if method == "upsert" else "replace", primary_key=keys or None))
        return len(rows)


class ElasticLoader(BaseLoader):
    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        try:
            from elasticsearch import Elasticsearch, helpers
        except ImportError as exc:
            raise ConfigError("DEV Elastic load requires the 'elasticsearch' package") from exc

        client = Elasticsearch(
            get_raw("DEV__ELASTIC_URL", "http://localhost:9200"),
            api_key=get_raw("DEV__ELASTIC_API_KEY") or None,
        )
        index = self.config.get("es_index") or self.config.get("table") or self.config.get("source")
        method = _load_method(self.config)
        keys = _unique_keys(self.config)
        if method == "upsert" and not keys:
            raise ConfigError("UNIQUE_KEY is required when METHOD=upsert")

        if method == "replace":
            client.indices.delete(index=index, ignore_unavailable=True)
            ids = [str(uuid4()) for _ in rows]
        else:
            ids = [
                str(row.get("_id") or "|".join(str(row.get(key, "")) for key in keys))
                for row in rows
            ]
        actions = [
            {"_index": index, "_id": doc_id, "_source": row}
            for doc_id, row in zip(ids, rows)
        ]
        helpers.bulk(client, actions)
        return len(rows)
