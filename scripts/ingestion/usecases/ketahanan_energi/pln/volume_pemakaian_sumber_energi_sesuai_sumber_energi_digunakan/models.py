"""Pydantic schema — Table Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    sumber_energi: str | None = Field(default=None, alias="sumber_energi", description="Nama sumber atau jenis energi (Bahan Bakar Minyak, Batu Bara, Gas Alam, Biomassa, Bahan Bakar Nabati), atau \"Total\" untuk baris total")

    kategori: str | None = Field(default=None, alias="kategori", description="Kelompok sumber energi: \"Sumber Energi Tak Terbarukan\", \"Sumber Energi Terbarukan\", atau \"Total Energi Terpakai dari Sumber Energi Tak Terbarukan dan Terbarukan\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (sumber energi), \"subtotal\" (total per kategori), atau \"grand_total\" (total keseluruhan)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai energi terpakai untuk produksi listrik pada sumber energi dan tahun terkait")
    model_config = {"populate_by_name": True, "extra": "ignore"}
