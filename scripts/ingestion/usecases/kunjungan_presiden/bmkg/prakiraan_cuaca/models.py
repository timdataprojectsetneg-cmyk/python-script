"""Pydantic schema mirroring the Data Dictionary for BMKG Prakiraan Cuaca."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PrakiraanCuacaRecord(BaseModel):
    adm4: str = Field(description="Kode wilayah administrasi tingkat IV (kelurahan/desa).")
    provinsi: Optional[str] = Field(default=None, description="Nama provinsi.")
    kotkab: Optional[str] = Field(default=None, description="Nama kabupaten/kota.")
    kecamatan: Optional[str] = Field(default=None, description="Nama kecamatan.")
    desa: Optional[str] = Field(default=None, description="Nama desa/kelurahan.")
    lon: Optional[float] = Field(default=None, description="Longitude lokasi administrasi.")
    lat: Optional[float] = Field(default=None, description="Latitude lokasi administrasi.")
    timezone: Optional[str] = Field(default=None, description="Zona waktu lokasi.")
    local_datetime: Optional[str] = Field(default=None, description="Waktu prakiraan lokal (WIB/WITA/WIT).")
    utc_datetime: Optional[str] = Field(default=None, description="Waktu prakiraan UTC.")
    t: Optional[float] = Field(default=None, description="Suhu udara (derajat Celsius).")
    hu: Optional[float] = Field(default=None, description="Kelembapan udara (%).")
    weather_desc: Optional[str] = Field(default=None, description="Kondisi cuaca dalam Bahasa Indonesia.")
    weather_desc_en: Optional[str] = Field(default=None, description="Kondisi cuaca dalam Bahasa Inggris.")
    ws: Optional[float] = Field(default=None, description="Kecepatan angin (km/jam).")
    wd: Optional[str] = Field(default=None, description="Arah angin.")
    tcc: Optional[float] = Field(default=None, description="Tutupan awan (%).")
    vs_text: Optional[str] = Field(default=None, description="Jarak pandang (km).")
    analysis_date: Optional[str] = Field(default=None, description="Waktu analisis produksi data prakiraan.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = PrakiraanCuacaRecord
