"""Pydantic schema — Tabel 16 Realisasi Cadangan Operasional BBM dari Tahun ke Tahun (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jenis_cadangan: str | None = Field(default=None, alias="jenis_cadangan", description="Jenis cadangan operasional: BBM atau LPG")
    nilai: str | None = Field(default=None, alias="nilai", description="Cadangan operasional per jenis dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="hari")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

