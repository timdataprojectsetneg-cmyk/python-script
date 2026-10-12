"""Generic extractor that reads rows from PostgreSQL.

Use as a source when the input already lives in a database reachable via
``PG_URI`` (e.g. an ETL that reads a table and writes it to MinIO/another sink).
The connection is opened lazily — only when ``extract()`` runs (no startup
validation).

Config (``{USECASE}__{PUBLISHER}__{SOURCE}__*``):

    SQL    = SELECT provinsi, tahun, nilai FROM source_table   (or QUERY)
    TABLE  = source_table                                       (alternative: SELECT *)

Subclass it per source to pre/post-process rows.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator

from ...exceptions import ConfigError
from ..base.extractor import BaseExtractor


class PostgresExtractor(BaseExtractor):
    """Yield rows from a SQL query (or a whole table) on the ``PG_URI`` database."""

    def _credentials(self) -> Dict[str, Any]:
        from ...config import get_uri

        if not get_uri("PG_URI"):
            raise ConfigError("PostgresExtractor requires PG_URI")
        from ..loaders.postgres_loader import _postgres_credentials

        return _postgres_credentials()

    def _query(self) -> str:
        sql = self.config.get("sql") or self.config.get("query")
        if sql:
            return str(sql)
        table = self.config.get("postgre_table") or self.config.get("table")
        if table:
            return f"SELECT * FROM {table}"
        raise ConfigError("PostgresExtractor requires SQL/QUERY or TABLE")

    def extract(self) -> Iterator[Dict[str, Any]]:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError as exc:  # pragma: no cover - dependency dependent
            raise ConfigError("Postgres source requires the 'psycopg2-binary' package") from exc

        creds = self._credentials()
        conn = psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            dbname=creds["database"],
            user=creds["username"],
            password=creds["password"],
        )
        try:
            with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(self._query())
                for row in cur:
                    yield dict(row)
        finally:
            conn.close()
