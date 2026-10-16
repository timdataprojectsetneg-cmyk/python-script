"""Pydantic schema — UMK Aceh (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    kabupaten_kota: str | None = Field(default=None, alias="Kabupaten Kota", description="Nama Kabupaten Kota")
    umk: int | None = Field(default=None, alias="umk", description="Jumlah UMK")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun Perhitungan")

    model_config = {"populate_by_name": True, "extra": "ignore"}

