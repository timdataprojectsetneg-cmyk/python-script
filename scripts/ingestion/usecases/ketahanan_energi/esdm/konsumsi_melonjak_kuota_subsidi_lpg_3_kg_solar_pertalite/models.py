"""Pydantic schema — Artikel KONTAN - Konsumsi Melonjak, Kuota Subsidi LPG 3 kg, Solar & Pertalite Terancam Jebol pada 2026 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode realisasi kumulatif yang disebut dalam RDP 26 Agustus 2026.")

    jenis_energi: str | None = Field(default=None, alias="Jenis Energi", description="Jenis energi bersubsidi atau penugasan.")
    kuota: float | None = Field(default=None, alias="Kuota", description="Kuota 2026 yang dirujuk dalam bahan rapat atau APBN, bila tersedia.")
    realisasi_s_d_juli: float | None = Field(default=None, alias="Realisasi s.d. Juli", description="Volume kumulatif sampai Juli 2026.")
    prognosa_2026: float | None = Field(default=None, alias="Prognosa 2026", description="Proyeksi volume sampai akhir 2026 menurut paparan rapat.")
    keterangan_terhadap_kuota: str | None = Field(default=None, alias="Keterangan terhadap Kuota", description="Rasio atau selisih prognosa terhadap kuota bila angka kuota tersedia.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
