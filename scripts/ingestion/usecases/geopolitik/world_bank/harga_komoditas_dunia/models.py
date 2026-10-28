"""Pydantic schema mirroring dictionary_harga_komoditas_dunia.md."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HargaKomoditasDuniaRecord(BaseModel):
    periode: str = Field(
        alias="Periode",
        pattern=r"^\d{4}-\d{2}$",
        description="Bulan pada Monthly Prices; format YYYY M MM dinormalisasi menjadi YYYY-MM.",
    )
    komoditas: str = Field(alias="Komoditas", description="Nama kolom komoditas asli.")
    harga: Optional[float] = Field(
        default=None, alias="Harga", description="Harga bulanan nominal. Missing value tetap kosong."
    )
    satuan: Optional[str] = Field(
        default=None,
        alias="Satuan",
        description="Unit persis dari baris satuan sumber. $ = USD; mt = metric ton; bbl = barrel; mmbtu = million BTU.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


Record = HargaKomoditasDuniaRecord
