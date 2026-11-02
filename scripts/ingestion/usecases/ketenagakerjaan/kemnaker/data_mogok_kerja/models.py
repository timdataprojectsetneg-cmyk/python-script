"""Pydantic schema — Data Mogok Kerja (mirrors the Data Dictionary).

Source columns in the ``mogok`` sheet: Provinsi, Kasus, Tenaga Kerja yang
Terlibat (orang); ``tahun`` is derived from the 'Tahun <yyyy>' title row.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi mogok kerja (\"Jumlah\" = nasional).")
    tenaga_kerja_yang_terlibat: int | None = Field(
        default=None,
        alias="Tenaga Kerja yang Terlibat (orang)",
        description="Jumlah tenaga kerja yang terlibat dalam mogok kerja.",
    )

    periode: str | None = Field(default=None, alias="Periode", description="Periode data, kumulatif sejak Januari.")
    jumlah_kasus: int | None = Field(default=None, alias="Jumlah_Kasus", description="Jumlah kasus mogok kerja; \"-\" = tidak ada kasus.")
    tk_terlibat: int | None = Field(default=None, alias="TK_Terlibat", description="Jumlah tenaga kerja yang terlibat mogok.")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
