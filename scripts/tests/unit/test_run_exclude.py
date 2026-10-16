"""Tests for `run --exclude` source filtering."""

from click.testing import CliRunner

import ingestion.cli as cli
from ingestion.usecases import registry


def test_resolve_run_targets_excludes_source(monkeypatch):
    monkeypatch.setattr(registry, "list_sources", lambda uc, pub: ["a", "b", "c"])
    assert cli._resolve_run_targets("uc", "p", None, exclude="b") == [("p", "a"), ("p", "c")]


def test_resolve_run_targets_excludes_multiple_comma_separated(monkeypatch):
    monkeypatch.setattr(
        registry, "list_sources", lambda uc, pub: ["kasus_perselisihan", "data_mogok_kerja", "satu_data"]
    )
    pairs = cli._resolve_run_targets(
        "uc", "p", None, exclude="Kasus Perselisihan,data_mogok_kerja"
    )
    assert pairs == [("p", "satu_data")]


def test_resolve_run_targets_exclude_is_substring_tolerant(monkeypatch):
    monkeypatch.setattr(
        registry, "list_sources", lambda uc, pub: ["bps_inflasi_yoy", "bps_inflasi_mom", "umk_aceh"]
    )
    assert cli._resolve_run_targets("uc", "bps", None, exclude="bps_inflasi") == [("bps", "umk_aceh")]


def test_resolve_run_targets_without_exclude_unchanged(monkeypatch):
    monkeypatch.setattr(registry, "list_sources", lambda uc, pub: ["a", "b"])
    assert cli._resolve_run_targets("uc", "p", None) == [("p", "a"), ("p", "b")]


def test_run_passes_exclude_to_resolver(monkeypatch):
    seen = {}

    def fake_resolve(usecase, publisher, source, exclude=None):
        seen["exclude"] = exclude
        return [("p", "a")]

    monkeypatch.setattr(cli, "_resolve_run_targets", fake_resolve)
    monkeypatch.setattr(cli, "_apply_env", lambda profile: None)
    monkeypatch.setattr(cli, "execute_run", lambda *a, **k: 0)

    result = CliRunner().invoke(
        cli.run, ["--usecase", "uc", "--publisher", "p", "--exclude", "a,b"]
    )

    assert result.exit_code == 0, result.output
    assert seen["exclude"] == "a,b"
