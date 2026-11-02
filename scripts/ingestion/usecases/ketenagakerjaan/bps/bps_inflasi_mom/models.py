"""Pydantic schema — BPS Inflasi Bulanan (month-to-month) per city.

One row per city; one column per month plus ``tahunan`` (akumulasi tahun
kalender), and the derived ``tahun``.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi", description="Kab/kota titik pantau IHK BPS (INDONESIA = nasional).")
    januari: float | None = Field(default=None, alias="Januari", description="Inflasi m-to-m bulan Januari 2026; \"-\" = belum rilis.")
    februari: float | None = Field(default=None, alias="Februari", description="Inflasi m-to-m bulan Februari 2026; \"-\" = belum rilis.")
    maret: float | None = Field(default=None, alias="Maret", description="Inflasi m-to-m bulan Maret 2026; \"-\" = belum rilis.")
    april: float | None = Field(default=None, alias="April", description="Inflasi m-to-m bulan April 2026; \"-\" = belum rilis.")
    mei: float | None = Field(default=None, alias="Mei", description="Inflasi m-to-m bulan Mei 2026; \"-\" = belum rilis.")
    juni: float | None = Field(default=None, alias="Juni", description="Inflasi m-to-m bulan Juni 2026; \"-\" = belum rilis.")
    juli: float | None = Field(default=None, alias="Juli", description="Inflasi m-to-m bulan Juli 2026; \"-\" = belum rilis.")
    agustus: float | None = Field(default=None, alias="Agustus", description="Inflasi m-to-m bulan Agustus 2026; \"-\" = belum rilis.")
    september: float | None = Field(default=None, alias="September", description="Inflasi m-to-m bulan September 2026; \"-\" = belum rilis.")
    oktober: float | None = Field(default=None, alias="Oktober", description="Inflasi m-to-m bulan Oktober 2026; \"-\" = belum rilis.")
    november: float | None = Field(default=None, alias="November", description="Inflasi m-to-m bulan November 2026; \"-\" = belum rilis.")
    desember: float | None = Field(default=None, alias="Desember", description="Inflasi m-to-m bulan Desember 2026; \"-\" = belum rilis.")
    tahunan: float | None = Field(default=None, alias="Tahunan", description="Inflasi tahun kalender (terisi setelah Desember).")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
