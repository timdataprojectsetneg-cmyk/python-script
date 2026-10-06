"""Pydantic schema — BPS Consumer Price Index (IHK) per province.

One row per province; one column per month, plus the derived ``tahun``.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, description="Nama provinsi.")
    januari: float | None = Field(default=None, description="IHK Januari (tahun dasar 2022).")
    februari: float | None = Field(default=None, description="IHK Februari.")
    maret: float | None = Field(default=None, description="IHK Maret.")
    april: float | None = Field(default=None, description="IHK April.")
    mei: float | None = Field(default=None, description="IHK Mei.")
    juni: float | None = Field(default=None, description="IHK Juni.")
    juli: float | None = Field(default=None, description="IHK Juli.")
    agustus: float | None = Field(default=None, description="IHK Agustus.")
    september: float | None = Field(default=None, description="IHK September.")
    oktober: float | None = Field(default=None, description="IHK Oktober.")
    november: float | None = Field(default=None, description="IHK November.")
    desember: float | None = Field(default=None, description="IHK Desember.")
    tahun: int | None = Field(default=None, description="Tahun data.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
