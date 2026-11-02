"""Pydantic schema — BPS Consumer Price Index (IHK) per province.

One row per province; one column per month, plus the derived ``tahun``.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (INDONESIA = nasional).")
    januari: float | None = Field(default=None, alias="Januari", description="IHK (2022=100) bulan Januari 2026; \"-\" = belum rilis.")
    februari: float | None = Field(default=None, alias="Februari", description="IHK (2022=100) bulan Februari 2026; \"-\" = belum rilis.")
    maret: float | None = Field(default=None, alias="Maret", description="IHK (2022=100) bulan Maret 2026; \"-\" = belum rilis.")
    april: float | None = Field(default=None, alias="April", description="IHK (2022=100) bulan April 2026; \"-\" = belum rilis.")
    mei: float | None = Field(default=None, alias="Mei", description="IHK (2022=100) bulan Mei 2026; \"-\" = belum rilis.")
    juni: float | None = Field(default=None, alias="Juni", description="IHK (2022=100) bulan Juni 2026; \"-\" = belum rilis.")
    juli: float | None = Field(default=None, alias="Juli", description="IHK (2022=100) bulan Juli 2026; \"-\" = belum rilis.")
    agustus: float | None = Field(default=None, alias="Agustus", description="IHK (2022=100) bulan Agustus 2026; \"-\" = belum rilis.")
    september: float | None = Field(default=None, alias="September", description="IHK (2022=100) bulan September 2026; \"-\" = belum rilis.")
    oktober: float | None = Field(default=None, alias="Oktober", description="IHK (2022=100) bulan Oktober 2026; \"-\" = belum rilis.")
    november: float | None = Field(default=None, alias="November", description="IHK (2022=100) bulan November 2026; \"-\" = belum rilis.")
    desember: float | None = Field(default=None, alias="Desember", description="IHK (2022=100) bulan Desember 2026; \"-\" = belum rilis.")

    tahunan: float | None = Field(default=None, alias="Tahunan", description="IHK tahunan (terisi setelah Desember).")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
