"""Pydantic schema — UMK Aceh (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    kabupaten_kota: str | None = Field(default=None, alias="Kabupaten Kota")
    umk: int | None = Field(default=None, alias="umk")
    tahun: int | None = Field(default=None, alias="tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}

