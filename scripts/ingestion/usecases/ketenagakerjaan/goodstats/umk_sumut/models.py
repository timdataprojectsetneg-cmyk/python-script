"""Pydantic schema — UMK Sumatera Utara."""

from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UMKSumutRecord(BaseModel):
    kabupaten_kota: str = Field(
        validation_alias=AliasChoices("kabupaten_kota", "Kabupaten/Kota", "Wilayah", "wilayah")
    )
    umk_2026: int = Field(
        ge=0, validation_alias=AliasChoices("umk_2026", "UMK_2026", "Upah", "upah")
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up ``models.Record``.
Record = UMKSumutRecord
