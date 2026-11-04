"""Pydantic schema — Penyalur BBM 47302 Agen Industri PT Pertamina Patra Niaga (mirrors the Data Dictionary)."""

from datetime import date
from pydantic import BaseModel, Field


class Record(BaseModel):

    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama agen BBM industri.")
    alamat: str | None = Field(default=None, alias="Alamat", description="Alamat agen/penyalur.")
    wilayah_penyaluran: str | None = Field(default=None, alias="Wilayah Penyaluran", description="Wilayah yang menjadi cakupan penyaluran.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
