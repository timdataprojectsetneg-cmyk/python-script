"""Pydantic schema mirroring the Data Dictionary for BMKG Gempa Dirasakan."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BmkgGempaDirasakanRecord(BaseModel):
    tanggal: Optional[str] = Field(default=None, alias="Tanggal", description="Tanggal kejadian WIB (mis. 25 Okt 2026).")
    jam: Optional[str] = Field(default=None, alias="Jam", description="Jam kejadian WIB (HH:MM:SS WIB).")
    datetime: dt.datetime = Field(alias="DateTime", description="Waktu kejadian UTC (ISO 8601).")
    point_coordinates: str = Field(alias="point/coordinates", description='Koordinat episenter "lintang,bujur" desimal.')
    lintang: Optional[str] = Field(default=None, alias="Lintang", description="Lintang teks (mis. 0.73 LS).")
    bujur: Optional[str] = Field(default=None, alias="Bujur", description="Bujur teks (mis. 131.39 BT).")
    magnitude: Optional[float] = Field(default=None, alias="Magnitude", description="Kekuatan gempa (M).")
    kedalaman: Optional[str] = Field(default=None, alias="Kedalaman", description="Kedalaman hiposenter (teks, mis. 13 km).")
    wilayah: Optional[str] = Field(default=None, alias="Wilayah", description="Lokasi relatif episenter.")
    dirasakan: Optional[str] = Field(default=None, alias="Dirasakan", description="Intensitas MMI per daerah.")
    latitude: Optional[float] = Field(default=None, description="Turunan: lintang desimal (negatif = LS).")
    longitude: Optional[float] = Field(default=None, description="Turunan: bujur desimal (negatif = BB).")
    kedalaman_km: Optional[float] = Field(default=None, description="Turunan: kedalaman dalam km (angka).")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = BmkgGempaDirasakanRecord
