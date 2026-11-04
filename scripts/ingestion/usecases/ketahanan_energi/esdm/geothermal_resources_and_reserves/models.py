"""Pydantic schema — 6.5.1 Geothermal Resources and Reserves (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun posisi data (as of Desember 2025)")
    kategori: str | None = Field(default=None, alias="kategori", description="Kategori klasifikasi potensi panas bumi: Speculative, Hipotethical (kategori sumber daya/resources), Possible, Probable, Proven (kategori cadangan/reserves). Penulisan \"Hipotethical\" mengikuti dokumen sumber")
    nilai: int | None = Field(default=None, alias="nilai", description="Besaran potensi panas bumi (sumber daya atau cadangan) pada kategori dan provinsi terkait")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai, yaitu MW (megawatt)")

    label: str | None = Field(default=None, alias="Label", description="Deskripsi")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi lokasi potensi panas bumi sesuai tabel sumber (contoh: Aceh, West Java, Southeast Sulawesi)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
