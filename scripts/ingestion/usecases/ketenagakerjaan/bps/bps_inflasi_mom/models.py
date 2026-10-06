"""Pydantic schema — BPS Inflasi Bulanan (month-to-month) per city.

One row per city; one column per month plus ``tahunan`` (akumulasi tahun
kalender), and the derived ``tahun``.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    kota_inflasi: str | None = Field(default=None, description="Nama kota sampel IHK BPS.")
    januari: float | None = Field(default=None, description="Inflasi bulanan Januari (%).")
    februari: float | None = Field(default=None, description="Inflasi bulanan Februari (%).")
    maret: float | None = Field(default=None, description="Inflasi bulanan Maret (%).")
    april: float | None = Field(default=None, description="Inflasi bulanan April (%).")
    mei: float | None = Field(default=None, description="Inflasi bulanan Mei (%).")
    juni: float | None = Field(default=None, description="Inflasi bulanan Juni (%).")
    juli: float | None = Field(default=None, description="Inflasi bulanan Juli (%).")
    agustus: float | None = Field(default=None, description="Inflasi bulanan Agustus (%).")
    september: float | None = Field(default=None, description="Inflasi bulanan September (%).")
    oktober: float | None = Field(default=None, description="Inflasi bulanan Oktober (%).")
    november: float | None = Field(default=None, description="Inflasi bulanan November (%).")
    desember: float | None = Field(default=None, description="Inflasi bulanan Desember (%).")
    tahunan: float | None = Field(default=None, description="Akumulasi inflasi tahun kalender (%) - bukan y-o-y.")
    tahun: int | None = Field(default=None, description="Tahun data.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
