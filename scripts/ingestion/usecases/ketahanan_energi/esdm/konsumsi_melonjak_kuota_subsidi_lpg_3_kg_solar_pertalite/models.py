"""Pydantic schema — Artikel KONTAN - Konsumsi Melonjak, Kuota Subsidi LPG 3 kg, Solar & Pertalite Terancam Jebol pada 2026 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku laporan keuangan")
    komponen_biaya: str | None = Field(default=None, alias="Komponen Biaya", description="Pos biaya pada cost of sales PGN")
    jenis_biaya: str | None = Field(default=None, alias="Jenis Biaya", description="Raw material, service, labor, depreciation, maintenance, fuel, overhead")
    nilai: float | None = Field(default=None, alias="Nilai", description="Nilai komponen biaya sesuai laporan keuangan")
    tahun_pembanding: int | None = Field(default=None, alias="Tahun Pembanding", description="Tahun 2024 sebagai comparative figure")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

