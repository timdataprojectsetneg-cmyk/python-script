"""Pydantic schema — BPS Inflasi MoM (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi")
    januari_s_d_desember_12_kolom_terpisah_per_bulan: float | None = Field(default=None, alias="Januari s.d. Desember (12 kolom terpisah per bulan)")
    tahunan: float | None = Field(default=None, alias="Tahunan")

    model_config = {"populate_by_name": True, "extra": "ignore"}

