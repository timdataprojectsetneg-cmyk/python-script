"""Tests for the --env profile loading."""

import pytest

from ingestion import config
from ingestion.cli import _apply_env
from ingestion.exceptions import ConfigError


@pytest.fixture(autouse=True)
def _reset_profile():
    config.set_env_profile(None)
    yield
    config.set_env_profile(None)


def test_profile_adds_env_file():
    config.set_env_profile("dev")
    files = [path for path, _ in config._env_files()]
    assert any(path.endswith(".env.dev") for path in files)
    profile_pairs = {path: override for path, override in config._env_files() if path.endswith(".env.dev")}
    assert all(override is True for override in profile_pairs.values())


def test_base_env_still_loaded_without_profile():
    files = [path for path, _ in config._env_files()]
    assert any(path.endswith(".env") and not path.endswith(".env.dev") for path in files)


def test_missing_profile_raises():
    with pytest.raises(ConfigError):
        _apply_env("definitely_missing_profile")


def test_apply_env_none_keeps_state(monkeypatch):
    monkeypatch.setattr(config, "env_profile_file", lambda profile: "/tmp/fake.env.dev")
    config.set_env_profile("dev")
    # Subcommand without --env must not reset the group-level profile.
    _apply_env(None)
    assert config.get_env_profile() == "dev"
