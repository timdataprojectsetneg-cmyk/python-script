"""Pydantic schema — 6.5.2 Geothermal Power Plant Capacity 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Tidak terisi pada sumber (selalu `null`)")
    jenis_pembangkit: str | None = Field(default=None, alias="jenis_pembangkit", description="Nama PLTP (mis. PLTP Sibayak, PLTP Salak), atau `Total` untuk jumlah keseluruhan")
    nilai: str | None = Field(default=None, alias="nilai", description="Kapasitas terpasang PLTP")
    satuan: str | None = Field(default=None, alias="satuan", description="MW")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Provinsi lokasi PLTP (`null` untuk baris Total)")
    kode_provinsi: int | None = Field(default=None, alias="kode_provinsi", description="Kode provinsi (`null` untuk baris Total)")
    ipb_owner: str | None = Field(default=None, alias="ipb_owner", description="Pemilik IPB (Izin Panas Bumi) atau pengembang PLTP (`null` untuk baris Total)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

