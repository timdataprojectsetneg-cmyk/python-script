"""Tests for module scaffolding (eligible sources only, non-destructive)."""

from pathlib import Path

from ingestion.sharepoint.scaffold import scaffold_usecase

SOURCES = [
    {
        "source_name": "Kasus Perselisihan",
        "data_access": "Download Excel",
        "eligible": True,
    }
]


def test_scaffold_creates_files(tmp_path):
    schemas = {"kasus_perselisihan": [{"label": "Jumlah_Pusat", "type": "Integer"}]}
    created, skipped = scaffold_usecase(str(tmp_path), "ketenagakerjaan", SOURCES, schemas)

    base = tmp_path / "ketenagakerjaan" / "kasus_perselisihan"
    assert (base / "__init__.py").exists()
    assert (base / "models.py").exists()
    assert (base / "normalizer.py").exists()
    assert (base / "excel" / "__init__.py").exists()
    assert (base / "excel" / "extractor.py").exists()

    models = (base / "models.py").read_text()
    assert "class Record(BaseModel):" in models
    assert "jumlah_pusat" in models

    extractor = (base / "excel" / "extractor.py").read_text()
    assert "class Extractor(ExcelExtractor):" in extractor
    assert "from .....core.extractors.excel_extractor import ExcelExtractor" in extractor

    normalizer = (base / "normalizer.py").read_text()
    assert "from ....core.base.normalizer import BaseNormalizer" in normalizer

    assert len(created) == 5
    assert skipped == []


def test_scaffold_does_not_overwrite(tmp_path):
    base = tmp_path / "ketenagakerjaan" / "kasus_perselisihan"
    base.mkdir(parents=True)
    (base / "models.py").write_text("# custom\n")

    created, skipped = scaffold_usecase(str(tmp_path), "ketenagakerjaan", SOURCES, {})

    assert (base / "models.py").read_text() == "# custom\n"
    assert str(base / "models.py") in skipped
    assert str(base / "normalizer.py") in created


def test_scaffold_can_overwrite(tmp_path):
    base = tmp_path / "ketenagakerjaan" / "kasus_perselisihan"
    base.mkdir(parents=True)
    (base / "models.py").write_text("# custom\n")

    created, skipped = scaffold_usecase(
        str(tmp_path), "ketenagakerjaan", SOURCES, {}, overwrite=True
    )

    assert "# custom" not in (base / "models.py").read_text()
    assert str(base / "models.py") in created
    assert skipped == []
