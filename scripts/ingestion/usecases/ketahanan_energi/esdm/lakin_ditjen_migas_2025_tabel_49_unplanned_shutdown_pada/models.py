"""Pydantic schema — LAKIN Ditjen Migas 2025_Tabel 49 Unplanned Shutdown pada Kegiatan Usaha Hulu Migas (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jumlah_unplanned_shutdown: int | None = Field(default=None, alias="jumlah_unplanned_shutdown", description="Jumlah unplanned shutdown kegiatan usaha hulu migas per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}

