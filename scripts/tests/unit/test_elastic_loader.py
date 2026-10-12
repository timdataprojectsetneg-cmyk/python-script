"""Tests for the Elasticsearch loader (no index delete / no delete privilege)."""

import pytest

from ingestion.core.loaders.elastic_loader import _build_actions, _doc_id
from ingestion.exceptions import ConfigError


def test_replace_indexes_by_unique_key_without_delete():
    rows = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}]
    actions = _build_actions(rows, "idx", "replace", ["id"])
    assert all(action["_op_type"] == "index" for action in actions)
    assert [action["_id"] for action in actions] == ["1", "2"]
    assert all(action["_op_type"] != "delete" for action in actions)


def test_replace_without_key_uses_stable_content_hash():
    assert _doc_id({"a": 1, "b": "x"}, []) == _doc_id({"b": "x", "a": 1}, [])
    assert _doc_id({"a": 1, "b": "x"}, []) != _doc_id({"a": 1, "b": "y"}, [])


def test_upsert_requires_key_and_uses_update():
    with pytest.raises(ConfigError):
        _build_actions([{"a": 1}], "idx", "upsert", [])
    actions = _build_actions([{"a": 1}], "idx", "upsert", ["a"])
    assert actions[0]["_op_type"] == "update"
    assert actions[0]["doc_as_upsert"] is True
