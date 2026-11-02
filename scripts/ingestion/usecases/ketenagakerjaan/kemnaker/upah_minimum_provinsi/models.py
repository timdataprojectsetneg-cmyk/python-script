"""Pydantic schema — Upah Minimum Provinsi (UMP) (mirrors the Data Dictionary).

Columns in the ``data`` sheet: ``Provinsi`` and ``Upah Minimum (Rp)``.
"""

from pydantic import BaseModel, ConfigDict, Field


class UpahMinimumProvinsiRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")

    # Reject NaN/Inf so footer rows (e.g. 'Sumber: Kemnaker RI') are dropped.
    upah_minimum: float | None = Field(default=None, alias="Upah_Minimum", description="Besaran UMP tahun 2026.")
    model_config = ConfigDict(populate_by_name=True, extra="ignore", allow_inf_nan=False)


Record = UpahMinimumProvinsiRecord
