"""Pydantic schema — BPS Inflasi YoY (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan dan tahun rilis (misal: Agustus 2026).")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY", description="Inflasi year-on-year dibanding bulan yang sama tahun sebelumnya.")
    inflasi_mtm: float | None = Field(default=None, alias="Inflasi_MtM", description="Inflasi month-to-month dibanding bulan sebelumnya.")
    komponen_pendorong: str | None = Field(default=None, alias="Komponen_Pendorong", description="Kelompok pengeluaran/komoditas utama pendorong inflasi bulan tersebut (dari narasi siaran pers).")

    model_config = {"populate_by_name": True, "extra": "ignore"}

