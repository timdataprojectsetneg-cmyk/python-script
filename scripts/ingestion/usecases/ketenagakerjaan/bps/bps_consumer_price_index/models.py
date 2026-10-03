"""Pydantic schema — BPS Consumer Price Index (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (38 provinsi).")
    januari: float | None = Field(default=None, alias="Januari", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    februari: float | None = Field(default=None, alias="Februari", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    maret: float | None = Field(default=None, alias="Maret", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    april: float | None = Field(default=None, alias="April", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    mei: float | None = Field(default=None, alias="Mei", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    juni: float | None = Field(default=None, alias="Juni", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    juli: float | None = Field(default=None, alias="Juli", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    agustus: float | None = Field(default=None, alias="Agustus", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    september: float | None = Field(default=None, alias="September", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    oktober: float | None = Field(default=None, alias="Oktober", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    november: float | None = Field(default=None, alias="November", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    desember: float | None = Field(default=None, alias="Desember", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    tahun: str | None = Field(default=None, alias="Tahun", description="tahun rilis.")

    model_config = {"populate_by_name": True, "extra": "ignore"}

