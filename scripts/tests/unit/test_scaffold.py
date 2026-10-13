"""Tests for module scaffolding (eligible sources only, non-destructive)."""

from pathlib import Path

from ingestion.catalog.metadata_parser import publisher_slug, source_slug, to_pydantic_source
from ingestion.catalog.scaffold import (
    merge_models_source,
    remove_ineligible_sources,
    scaffold_usecase,
)

SOURCES = [
    {
        "source_name": "Kasus Perselisihan",
        "publisher": "Kemnaker",
        "data_access": "Download Excel",
        "eligible": True,
    }
]


def test_scaffold_creates_files(tmp_path):
    schemas = {"kasus_perselisihan": [{"label": "Jumlah_Pusat", "type": "Integer"}]}
    created, skipped = scaffold_usecase(str(tmp_path), "ketenagakerjaan", SOURCES, schemas)

    base = tmp_path / "ketenagakerjaan" / "kemnaker" / "kasus_perselisihan"
    assert (tmp_path / "ketenagakerjaan" / "kemnaker" / "__init__.py").exists()
    assert (base / "__init__.py").exists()
    assert (base / "models.py").exists()
    assert (base / "normalizer.py").exists()
    assert (base / "extractor.py").exists()

    models = (base / "models.py").read_text()
    assert "class Record(BaseModel):" in models
    assert "jumlah_pusat" in models

    extractor = (base / "extractor.py").read_text()
    assert "class Extractor(ExcelExtractor):" in extractor
    assert "from .....core.extractors.excel_extractor import ExcelExtractor" in extractor

    normalizer = (base / "normalizer.py").read_text()
    assert "from .....core.base.normalizer import BaseNormalizer" in normalizer

    assert len(created) == 5
    assert skipped == []


def test_scaffold_does_not_overwrite_preserves_custom_code(tmp_path):
    base = tmp_path / "ketenagakerjaan" / "kemnaker" / "kasus_perselisihan"
    base.mkdir(parents=True)
    (base / "models.py").write_text(
        '"""Custom."""\n\n'
        "from pydantic import BaseModel, Field\n\n\n"
        "class Record(BaseModel):\n"
        "    jumlah_pusat: int | None = Field(default=None, alias=\"Jumlah_Pusat\")\n\n"
        "    model_config = {\"populate_by_name\": True, \"extra\": \"ignore\"}\n\n"
        "    def keep_me(self) -> str:\n"
        "        return \"keep me\"\n"
    )

    created, skipped = scaffold_usecase(
        str(tmp_path),
        "ketenagakerjaan",
        SOURCES,
        {"kasus_perselisihan": [{"label": "Jumlah_Pusat", "type": "Integer"}]},
    )

    models = (base / "models.py").read_text()
    assert "keep me" in models
    assert str(base / "normalizer.py") in created


def test_scaffold_can_overwrite(tmp_path):
    base = tmp_path / "ketenagakerjaan" / "kemnaker" / "kasus_perselisihan"
    base.mkdir(parents=True)
    (base / "models.py").write_text("# custom\n")

    created, skipped = scaffold_usecase(
        str(tmp_path),
        "ketenagakerjaan",
        SOURCES,
        {"kasus_perselisihan": [{"label": "Jumlah_Pusat", "type": "Integer"}]},
        overwrite=True,
    )

    models = (base / "models.py").read_text()
    assert "# custom" not in models
    assert "class Record(BaseModel):" in models
    assert str(base / "models.py") in created
    assert skipped == []


def test_merge_updates_fields_keeps_methods_and_extra_classes():
    schema = [
        {"label": "Kabupaten_Kota", "name": "kabupaten_kota", "type": "Text"},
        {"label": "Tahun", "name": "tahun", "type": "Integer"},
    ]
    generated = '"""Doc."""\n\n' + to_pydantic_source("Record", schema)
    existing = (
        '"""Custom docstring."""\n\n'
        "from pydantic import BaseModel, Field\n\n\n"
        "class Extra(BaseModel):\n"
        "    foo: str | None = None\n\n\n"
        "class Record(BaseModel):\n"
        '    kabupaten_kota: str | None = Field(default=None, alias="Old")\n\n'
        "    @classmethod\n"
        "    def helper(cls) -> str:\n"
        "        return \"keep me\"\n"
    )

    merged = merge_models_source(existing, generated)

    assert "class Extra(BaseModel):" in merged
    assert "def helper" in merged
    assert 'alias="Kabupaten_Kota"' in merged
    assert "tahun" in merged


def test_merge_preserves_custom_field_aliases():
    schema = [{"label": "UMK", "name": "umk", "type": "Integer"}]
    generated = to_pydantic_source("Record", schema)
    existing = (
        "from pydantic import BaseModel, Field\n\n\n"
        "class Record(BaseModel):\n"
        '    umk: int | None = Field(default=None, validation_alias="upah")\n\n'
        '    model_config = {"populate_by_name": True, "extra": "ignore"}\n'
    )

    merged = merge_models_source(existing, generated)

    assert 'validation_alias="upah"' in merged


def test_merge_uses_record_alias_target():
    schema = [{"label": "Judul", "name": "judul", "type": "Text"}]
    generated = to_pydantic_source("Record", schema)
    existing = (
        "from pydantic import BaseModel, Field\n\n\n"
        "class SatuDataRecord(BaseModel):\n"
        "    judul: str | None = Field(default=None)\n\n\n"
        "Record = SatuDataRecord\n"
    )

    merged = merge_models_source(existing, generated)

    assert "class Record(BaseModel):" not in merged
    assert "Record = SatuDataRecord" in merged
    assert merged.count("class SatuDataRecord(BaseModel):") == 1


def test_remove_ineligible_sources_respects_scope(tmp_path):
    root = tmp_path / "usecases"
    kept = root / "ketenagakerjaan" / publisher_slug(SOURCES[0]) / source_slug(SOURCES[0])
    sibling = root / "ketenagakerjaan" / "kemnaker" / "stale_source"
    other_pub = root / "ketenagakerjaan" / "otherpub" / "stale_source"
    for path in (kept, sibling, other_pub):
        path.mkdir(parents=True)
        (path / "__init__.py").write_text("")

    removed = remove_ineligible_sources(
        str(root), "ketenagakerjaan", SOURCES, publishers={"kemnaker"}, sources={source_slug(SOURCES[0])}
    )

    assert kept.exists()
    assert sibling.exists()
    assert other_pub.exists()
    assert removed == []

    removed_all = remove_ineligible_sources(str(root), "ketenagakerjaan", SOURCES)

    assert kept.exists()
    assert not sibling.exists()
    assert not other_pub.exists()
    assert str(sibling) in removed_all
