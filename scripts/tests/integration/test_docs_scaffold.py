"""Integration tests: docs --scaffold / --delete work offline from local docs."""

from pathlib import Path

from click.testing import CliRunner

from ingestion.cli import cli
from ingestion.catalog.markdown_docs import (
    dictionary_filename,
    render_dictionary_markdown,
    render_usecase_markdown,
    write_markdown,
)
from ingestion.catalog.metadata_parser import parse_catalog_row

ROWS = [
    {
        "Source Name": "Kasus Perselisihan",
        "Publisher": "Kemnaker",
        "Data Access": "Download Excel",
        "Eligible": True,
        "Source Link": "https://example.org/a",
    },
    {
        "Source Name": "Sumber Manual",
        "Publisher": "Kemnaker",
        "Data Access": "Manual",
        "Eligible": False,
        "Source Link": "https://example.org/b",
    },
]

SCHEMA = [
    {
        "label": "Nomor_Perkara",
        "name": "nomor_perkara",
        "type": "String",
        "satuan": None,
        "deskripsi": "Nomor putusan",
    }
]


def _write_docs(tmp_path, sources=None):
    rows = sources or ROWS
    parsed = [parse_catalog_row(row) for row in rows]
    docs_dir = tmp_path / "docs" / "ketenagakerjaan"
    write_markdown(render_usecase_markdown("ketenagakerjaan", parsed, "catalog.xlsx"), str(docs_dir), "usecase.md")
    for row, source in zip(rows, parsed):
        write_markdown(
            render_dictionary_markdown("ketenagakerjaan", row["Source Name"], SCHEMA, source, "x/models.py"),
            str(docs_dir),
            dictionary_filename(row["Source Name"]),
        )
    return docs_dir


def _run(monkeypatch, tmp_path, args):
    monkeypatch.chdir(tmp_path)
    return CliRunner().invoke(cli, ["docs", *args])


def test_scaffold_from_local_docs_without_catalog_access(monkeypatch, tmp_path):
    _write_docs(tmp_path)

    result = _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])

    assert result.exit_code == 0, result.output
    source_dir = tmp_path / "ingestion" / "usecases" / "ketenagakerjaan" / "kemnaker" / "kasus_perselisihan"
    assert (source_dir / "models.py").is_file()
    assert (source_dir / "extractor.py").is_file()
    assert "nomor_perkara" in (source_dir / "models.py").read_text()
    # Ineligible sources are not scaffolded.
    assert not (tmp_path / "ingestion" / "usecases" / "ketenagakerjaan" / "kemnaker" / "sumber_manual").exists()


def test_scaffold_requires_local_docs(monkeypatch, tmp_path):
    result = _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])

    assert result.exit_code == 2, result.output
    assert "Local docs not found" in result.output


def test_scaffold_overwrite_replaces_existing_file(monkeypatch, tmp_path):
    _write_docs(tmp_path)
    source_dir = tmp_path / "ingestion" / "usecases" / "ketenagakerjaan" / "kemnaker" / "kasus_perselisihan"
    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])
    (source_dir / "normalizer.py").write_text("custom", encoding="utf-8")

    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])
    assert (source_dir / "normalizer.py").read_text() == "custom"

    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold-overwrite"])
    assert "BaseNormalizer" in (source_dir / "normalizer.py").read_text()


def test_scaffold_scoped_to_publisher(monkeypatch, tmp_path):
    _write_docs(tmp_path)

    result = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--publisher", "Kemnaker", "--scaffold"],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "ingestion" / "usecases" / "ketenagakerjaan" / "kemnaker").is_dir()

    missing = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--publisher", "Tidak Ada", "--scaffold"],
    )
    assert missing.exit_code == 2, missing.output


def test_delete_removes_docs_and_module_folders(monkeypatch, tmp_path):
    _write_docs(tmp_path)
    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])

    result = _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--delete"])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / "docs" / "ketenagakerjaan").exists()
    assert not (tmp_path / "ingestion" / "usecases" / "ketenagakerjaan").exists()


def test_delete_scoped_to_source(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    docs_dir = _write_docs(
        tmp_path,
        [
            ROWS[0],
            {
                "Source Name": "Direktori Putusan PHI",
                "Publisher": "Mahkamah Agung RI",
                "Data Access": "Web Scraping",
                "Eligible": True,
                "Source Link": "https://example.org/c",
            },
        ],
    )
    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])
    root = tmp_path / "ingestion" / "usecases" / "ketenagakerjaan"
    (docs_dir / "usecase.env").write_text("KETENAGAKERJAAN__X=1\n", encoding="utf-8")

    result = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--source", "direktori_putusan_phi", "--delete"],
    )

    assert result.exit_code == 0, result.output
    assert not (docs_dir / "dictionary_direktori_putusan_phi.md").exists()
    assert not (root / "mahkamah_agung_ri").exists()
    # The rest of the use case stays: other source, usecase.md and usecase.env.
    assert (docs_dir / "dictionary_kasus_perselisihan.md").is_file()
    assert (docs_dir / "usecase.md").is_file()
    assert (docs_dir / "usecase.env").is_file()
    assert (root / "kemnaker" / "kasus_perselisihan" / "models.py").is_file()


def test_delete_scoped_to_publisher(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    docs_dir = _write_docs(tmp_path)
    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])
    root = tmp_path / "ingestion" / "usecases" / "ketenagakerjaan"

    result = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--publisher", "Kemnaker", "--delete"],
    )

    assert result.exit_code == 0, result.output
    assert not (root / "kemnaker").exists()
    assert (docs_dir / "usecase.md").is_file()


def test_delete_scoped_source_keeps_publisher_with_other_sources(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _write_docs(tmp_path)
    _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--scaffold"])
    root = tmp_path / "ingestion" / "usecases" / "ketenagakerjaan" / "kemnaker"
    (root / "sumber_lain").mkdir(parents=True)

    result = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--source", "Kasus Perselisihan", "--delete"],
    )

    assert result.exit_code == 0, result.output
    assert not (root / "kasus_perselisihan").exists()
    assert (root / "sumber_lain").is_dir()


def test_delete_scoped_source_not_in_docs(monkeypatch, tmp_path):
    _write_docs(tmp_path)

    result = _run(
        monkeypatch,
        tmp_path,
        ["--usecase", "ketenagakerjaan", "--source", "tidak_ada", "--delete"],
    )

    assert result.exit_code == 2, result.output
    assert "not found" in result.output


def test_delete_reports_missing_paths(monkeypatch, tmp_path):
    result = _run(monkeypatch, tmp_path, ["--usecase", "ketenagakerjaan", "--delete"])

    assert result.exit_code == 0, result.output
    assert str(Path("docs") / "ketenagakerjaan") in result.output
