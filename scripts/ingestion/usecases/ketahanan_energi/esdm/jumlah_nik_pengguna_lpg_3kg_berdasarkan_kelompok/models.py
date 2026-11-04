"""Pydantic schema — Tabel 18 Jumlah NIK Pengguna LPG 3kg Berdasarkan Kelompok (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Kelompok pengguna: Rumah Tangga, Usaha Mikro, Petani Sasaran, Nelayan Sasaran, Pengecer, atau TOTAL")
    nilai: float | None = Field(default=None, alias="nilai", description="Jumlah NIK pengguna LPG 3 kg per kelompok")
    satuan: str | None = Field(default=None, alias="satuan", description="Juta atau ribu, sesuai baris (tidak dikonversi)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
