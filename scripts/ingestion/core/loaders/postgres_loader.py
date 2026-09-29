"""DEV-only PostgreSQL loader backed by dlt.

This module is only used when ``--mode dev``. In production, Python emits NDJSON
and NiFi ``PutDatabaseRecord`` performs the load, so no DB credentials live here.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable
from uuid import uuid4

from ...config import get_raw
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


class PostgresLoader(BaseLoader):
    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        try:
            import dlt
        except ImportError as exc:
            raise ConfigError(
                "DEV PostgreSQL load requires the 'dlt' package (pip install dlt[postgres])"
            ) from exc

        table = self.config.get("table") or self.config.get("source")
        write_disposition = self.config.get("write_disposition") or "merge"
        primary_key = self.config.get("primary_key")
        dataset = get_raw("DEV__POSTGRES_DATASET", "ingestion_dev")

        pipeline = dlt.pipeline(
            pipeline_name=f"ingestion_{self.config.get('usecase')}",
            destination="postgres",
            dataset_name=dataset,
            credentials=_postgres_credentials(),
        )
        resource = dlt.resource(
            rows,
            name=table,
            write_disposition=write_disposition,
            primary_key=primary_key,
        )
        pipeline.run(resource)
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
        index = self.config.get("table") or self.config.get("source")
        actions = [
            {"_index": index, "_id": row.get("_id") or str(uuid4()), "_source": row}
            for row in rows
        ]
        helpers.bulk(client, actions)
        return len(rows)
