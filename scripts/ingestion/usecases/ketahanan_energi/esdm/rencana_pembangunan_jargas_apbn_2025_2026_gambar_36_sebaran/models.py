"""Pydantic schema — Gambar 33- Rencana Pembangunan Jargas APBN 2025-2026 , Gambar 36 Sebaran Kilang Minyak Bumi (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    gambar: str | None = Field(default=None, alias="gambar", description="Sumber gambar: Gambar 33 (Rencana Pembangunan Jargas APBN 2025-2026) atau Gambar 36 (Sebaran Kilang Minyak Bumi)")
    periode: str | None = Field(default=None, alias="periode", description="Periode rencana: 2025-2026 (Gambar 33) atau 2025 (Gambar 36)")
    nama_wilayah: str | None = Field(default=None, alias="nama_wilayah", description="Kab/Kota penerima jargas (Gambar 33) atau nama kilang (Gambar 36)")
    nilai: str | None = Field(default=None, alias="nilai", description="Target pembangunan jargas dalam SR (Gambar 33) atau kapasitas kilang dalam MBSD (Gambar 36)")
    satuan: str | None = Field(default=None, alias="satuan", description="SR (Gambar 33) atau MBSD (Gambar 36)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

