"""DEV-only Elasticsearch loader supporting insert (replace) and update (upsert).

Used with ``--mode dev --env dev --target elastic``; in production Python emits
NDJSON and NiFi owns the sink. The connection is a single URI that may embed
credentials.

Configuration (``.env.dev``):

    ELASTIC__URI          = https://user:password@host:9200
    ELASTIC__API_KEY      = <secret>        # optional, instead of user:password
    ELASTIC__VERIFY_CERTS = true            # optional, default true
    ELASTIC__INDEX        = <default index> # optional; config es_index/table/source wins

Load method (``METHOD``): ``replace`` (default) deletes the index and bulk-inserts
every record; ``upsert`` bulk-updates documents by an id derived from
``UNIQUE_KEY`` with ``doc_as_upsert`` (insert when missing, update when present).
``upsert`` requires ``UNIQUE_KEY``.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable
from uuid import uuid4

from ...config import get_raw
from ...exceptions import ConfigError
from ..base.loader import BaseLoader
from .postgres_loader import _load_method, _unique_keys


def _elastic_options() -> Dict[str, Any]:
    """Client options from the ``ELASTIC__*`` env (URI may embed credentials)."""
    uri = get_raw("ELASTIC__URI") or get_raw("DEV__ELASTIC_URL") or "http://localhost:9200"
    options: Dict[str, Any] = {
        "hosts": [uri],
        "verify_certs": str(get_raw("ELASTIC__VERIFY_CERTS", "true")).lower() in ("1", "true", "yes"),
    }
    api_key = get_raw("ELASTIC__API_KEY") or get_raw("DEV__ELASTIC_API_KEY")
    if api_key:
        options["api_key"] = api_key
    return options


class ElasticLoader(BaseLoader):
    """DEV Elasticsearch loader: ``replace`` (insert) or ``upsert`` (update)."""

    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        try:
            from elasticsearch import Elasticsearch, helpers
        except ImportError as exc:
            raise ConfigError("DEV Elastic load requires the 'elasticsearch' package") from exc

        index = (
            self.config.get("es_index")
            or self.config.get("table")
            or self.config.get("source")
            or get_raw("ELASTIC__INDEX")
        )
        if not index:
            raise ConfigError("Missing ELASTIC__INDEX / es_index for the elastic load target")
        method = _load_method(self.config)
        keys = _unique_keys(self.config)
        if method == "upsert" and not keys:
            raise ConfigError("UNIQUE_KEY is required when METHOD=upsert")

        client = Elasticsearch(**_elastic_options())
        if method == "replace":
            client.indices.delete(index=index, ignore_unavailable=True)
            actions = [
                {"_op_type": "index", "_index": index, "_id": str(uuid4()), "_source": row}
                for row in rows
            ]
        else:
            actions = [
                {
                    "_op_type": "update",
                    "_index": index,
                    "_id": "|".join(str(row.get(key, "")) for key in keys),
                    "doc": row,
                    "doc_as_upsert": True,
                }
                for row in rows
            ]
        helpers.bulk(client, actions)
        return len(rows)
