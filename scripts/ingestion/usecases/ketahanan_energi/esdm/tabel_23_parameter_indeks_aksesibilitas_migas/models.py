"""Pydantic schema — Tabel 23 Parameter Indeks Aksesibilitas Migas (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jenis: str | None = Field(default=None, alias="jenis", description="Kelompok: Infrastruktur, Fasilitas Pengolahan, Fasilitas Penyimpanan, atau Fasilitas Pengangkutan")
    kapasitas: str | None = Field(default=None, alias="kapasitas", description="Jenis kapasitas, mis. Jargas (APBN+Non-APBN) Kumulatif, Konkit Nelayan, Kilang Minyak, LPG, LNG, CNG, Gas Bumi melalui Pipa")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai kapasitas per tahun; null bila tidak tersedia")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan per baris, mis. SR, Paket, MBCD, Juta Ton/tahun, KL, Mton, m3, mmscfd")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
