"""DEV-only Elasticsearch loader supporting insert (replace) and update (upsert).

Used with ``--mode dev --env dev``; in production Python emits NDJSON and NiFi
owns the sink. The connection is a single URI that may embed credentials.

Configuration (``.env.dev``):

    ELASTIC__URI          = https://user:password@host:9200
    ELASTIC__API_KEY      = <secret>        # optional, instead of user:password
    ELASTIC__VERIFY_CERTS = true            # optional, default true
    ELASTIC__INDEX        = <default index> # optional; config es_index/table/source wins

Load method (``METHOD``):

- ``replace`` (default) overwrites documents **by a stable id** without deleting
  the index. The id comes from ``UNIQUE_KEY`` when set, otherwise from a hash of
  the record content, so re-runs are idempotent (no duplicates) and no
  ``delete_index``/``manage`` privilege is required. Note: rows that disappear
  from the source are not purged (deleting the index is what needed the extra
  privilege).
- ``upsert`` bulk-updates documents by an id derived from ``UNIQUE_KEY`` with
  ``doc_as_upsert`` (insert when missing, update when present). ``upsert``
  requires ``UNIQUE_KEY``.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

from ...config import get_raw, get_uri
from ...exceptions import ConfigError
from ..base.loader import BaseLoader
from .postgres_loader import _load_method, _unique_keys


def _elastic_options() -> Dict[str, Any]:
    """Client options from the ``ELASTIC__*`` env (URI may embed credentials)."""
    uri = (
        get_raw("ELASTIC__URI")
        or get_uri("ELASTICSEARCH_URL")
        or get_raw("DEV__ELASTIC_URL")
        or "http://localhost:9200"
    )
    options: Dict[str, Any] = {
        "hosts": [uri],
        "verify_certs": str(get_raw("ELASTIC__VERIFY_CERTS", "true")).lower() in ("1", "true", "yes"),
    }
    api_key = get_raw("ELASTIC__API_KEY") or get_raw("DEV__ELASTIC_API_KEY")
    if api_key:
        options["api_key"] = api_key
    return options


def _doc_id(row: Dict[str, Any], keys: List[str]) -> str:
    """Stable document id: from UNIQUE_KEY, else a hash of the record content."""
    if keys:
        return "|".join(str(row.get(key, "")) for key in keys)
    payload = json.dumps(row, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _build_actions(
    rows: List[Dict[str, Any]], index: str, method: str, keys: List[str]
) -> List[Dict[str, Any]]:
    """Bulk actions for the given method, without ever deleting the index."""
    if method == "upsert":
        if not keys:
            raise ConfigError("UNIQUE_KEY is required when METHOD=upsert")
        return [
            {
                "_op_type": "update",
                "_index": index,
                "_id": _doc_id(row, keys),
                "doc": row,
                "doc_as_upsert": True,
            }
            for row in rows
        ]
    return [
        {"_op_type": "index", "_index": index, "_id": _doc_id(row, keys), "_source": row}
        for row in rows
    ]


class ElasticLoader(BaseLoader):
    """DEV Elasticsearch loader: ``replace`` (overwrite by id) or ``upsert``."""

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
        actions = _build_actions(rows, index, method, keys)

        client = Elasticsearch(**_elastic_options())
        helpers.bulk(client, actions)
        return len(rows)
