"""Tests for source concurrency (--thread) and normalization skip."""

import time

import pytest
from click.testing import CliRunner

import ingestion.cli as cli
import ingestion.config as config
from ingestion.core.normalizers.generic_normalizer import PassthroughNormalizer
from ingestion.usecases import registry


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    config.set_env_profile(None)
    for key in ("PG_URI", "ELASTICSEARCH_URL", "MINIO_URI"):
        monkeypatch.delenv(key, raising=False)
    yield


def _install(monkeypatch, pairs, sink):
    def fake_execute(usecase, pub, src, mode, limit, use_dlt, targets, full_refresh=False, out=None):
        time.sleep(0.01)
        sink.append((pub, src))
        if out is not None:
            out.write('{"src":"%s"}\n' % src)
        return 0

    monkeypatch.setattr(cli, "execute_run", fake_execute)
    monkeypatch.setattr(cli, "_resolve_run_targets", lambda *a, **k: pairs)
    monkeypatch.setattr(cli, "_apply_env", lambda p: None)


def test_thread_runs_all_sources_in_order(monkeypatch):
    sink = []
    _install(monkeypatch, [("p", "a"), ("p", "b"), ("p", "c")], sink)

    result = CliRunner().invoke(
        cli.run, ["--usecase", "ketenagakerjaan", "--publisher", "p", "--thread", "3"]
    )

    assert result.exit_code == 0, result.output
    assert sorted(sink) == [("p", "a"), ("p", "b"), ("p", "c")]
    # Output is buffered per source and emitted in selection order.
    assert result.output.index('"a"') < result.output.index('"b"') < result.output.index('"c"')


def test_sequential_when_no_workers(monkeypatch):
    sink = []
    _install(monkeypatch, [("p", "a"), ("p", "b")], sink)
    result = CliRunner().invoke(cli.run, ["--usecase", "ketenagakerjaan", "--publisher", "p"])
    assert result.exit_code == 0
    assert sorted(sink) == [("p", "a"), ("p", "b")]


def test_resolve_normalizer_passthrough_when_no_model(monkeypatch, caplog):
    monkeypatch.setattr(registry, "_import", lambda path: None)

    with caplog.at_level("WARNING", logger="ingestion"):
        normalizer = registry.resolve_normalizer(
            "ketenagakerjaan", "kemnaker", "kasus_perselisihan", {}
        )

    assert isinstance(normalizer, PassthroughNormalizer)
    assert any("skipping normalization" in message for message in caplog.messages)
    # Records are passed through unchanged (no cleaning/validation).
    assert list(normalizer.normalize(iter([{"a": " x  y "}]))) == [{"a": " x  y "}]
