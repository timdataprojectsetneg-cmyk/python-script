"""Tests for the ``docs --list`` inventory (no credentials/env required)."""

from click.testing import CliRunner

from ingestion.cli import cli


def test_docs_list_bare_needs_no_env():
    # `--list` without a value means "all" and must not touch SharePoint/Sheets.
    result = CliRunner().invoke(cli, ["docs", "--list"])
    assert result.exit_code == 0, result.output
    assert "usecases=" in result.output  # summary view


def test_docs_list_filtered_by_usecase():
    result = CliRunner().invoke(
        cli, ["docs", "--list", "sources", "--usecase", "ketenagakerjaan"]
    )
    assert result.exit_code == 0, result.output
    assert "ketenagakerjaan/" in result.output
