"""Pydantic schema — Kemnaker Perusahaan Melapor PP Table 1 (mirrors the Data Dictionary)."""
from pydantic import Field

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    mikro: int | None = Field(default=None, alias="Mikro", description="Perusahaan yang melaporkan PP skala Mikro (1–4 TK).")
    kecil: int | None = Field(default=None, alias="Kecil", description="Perusahaan yang melaporkan PP skala Kecil (5–19 TK).")
    menengah: int | None = Field(default=None, alias="Menengah", description="Perusahaan yang melaporkan PP skala Menengah (20–99 TK).")
    besar: int | None = Field(default=None, alias="Besar", description="Perusahaan yang melaporkan PP skala Besar (≥100 TK).")
    tidak_teridentifikasi: int | None = Field(default=None, alias="Tidak_Teridentifikasi", description="Perusahaan yang melaporkan PP yang belum melaporkan informasi tenaga kerja.")
    tahun: str | None = Field(default=None, alias="tahun", description="Tahun Pelaporan")
    bulan: str | None = Field(default=None, alias="bulan", description="Bulan Pelaporan")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh skala.")
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
