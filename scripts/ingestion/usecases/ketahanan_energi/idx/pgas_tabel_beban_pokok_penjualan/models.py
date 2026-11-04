"""Pydantic schema — PGAS_Tabel Beban Pokok Penjualan (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    uraian: str | None = Field(default=None, alias="uraian", description="Nama pos beban pokok penjualan (bahasa Indonesia). Ejaan mengikuti sumber, misalnya \"Biaya pabrikasi lainya\" dan \"Realti dan properti\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (pos biasa), \"subtotal\" (Bahan baku yang digunakan, Jumlah biaya produksi, Harga pokok produksi), atau \"total\" (Beban pokok penjualan dan pendapatan)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun laporan: 2025 (31 Desember 2025) atau 2024 (31 Desember 2024)")
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai pos pada tahun terkait. Null jika sel di sumber kosong")

    model_config = {"populate_by_name": True, "extra": "ignore"}

