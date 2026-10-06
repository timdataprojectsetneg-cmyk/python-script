"""Pydantic schema — Upah Minimum Provinsi (UMP) (mirrors the Data Dictionary).

Columns in the ``data`` sheet: ``Provinsi`` and ``Upah Minimum (Rp)``.
"""

from pydantic import BaseModel, ConfigDict, Field


class UpahMinimumProvinsiRecord(BaseModel):
    provinsi: str = Field(alias="Provinsi", description="Nama provinsi.")
    nilai_ump: float = Field(alias="Upah Minimum (Rp)", description="Besaran UMP dalam Rupiah.")

    # Reject NaN/Inf so footer rows (e.g. 'Sumber: Kemnaker RI') are dropped.
    model_config = ConfigDict(populate_by_name=True, extra="ignore", allow_inf_nan=False)


Record = UpahMinimumProvinsiRecord
