"""Pydantic schema — Data Mogok Kerja (mirrors the Data Dictionary).

Source columns in the ``mogok`` sheet: Provinsi, Kasus, Tenaga Kerja yang
Terlibat (orang); ``tahun`` is derived from the 'Tahun <yyyy>' title row.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    kasus: int | None = Field(default=None, alias="Kasus", description="Jumlah kejadian mogok kerja tercatat.")
    tenaga_kerja_yang_terlibat: int | None = Field(
        default=None,
        alias="Tenaga Kerja yang Terlibat (orang)",
        description="Jumlah tenaga kerja yang terlibat dalam mogok kerja.",
    )
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun penarikan data.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
