"""Pydantic schema for KKP Kampung Nelayan Merah Putih (KNMP)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KkpKampungNelayanRecord(BaseModel):
    id_knmp: str = Field(
        description="Identifier unik sentra Kampung Nelayan Merah Putih (misal: 'KNMP-3301-01')."
    )
    nama_desa_nelayan: str = Field(
        description="Nama sentra perikanan, pelabuhan, atau kampung nelayan binaan."
    )
    provinsi: str = Field(
        description="Provinsi lokasi pesisir."
    )
    kabupaten_kota: str = Field(
        description="Kabupaten atau kota pesisir."
    )
    jumlah_nelayan: Optional[int] = Field(
        default=None,
        description="Jumlah nelayan binaan aktif terdata di sentra perikanan."
    )
    kapasitas_cold_storage_ton: Optional[float] = Field(
        default=None,
        description="Kapasitas fasilitas cold storage atau ruang pendingin ikan dalam satuan ton."
    )
    produksi_es_ton_hari: Optional[float] = Field(
        default=None,
        description="Kapasitas produksi pabrik es penunjang mutu hasil tangkapan dalam ton/hari."
    )
    status_operasional: str = Field(
        default="Beroperasi",
        description="Status operasional fasilitas sentra (misal: 'Beroperasi', 'Pengembangan', 'Persiapan')."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Koordinat lintang lokasi geografis."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Koordinat bujur lokasi geografis."
    )
    data_source: str = Field(
        default="Kementerian Kelautan dan Perikanan (KKP) Republik Indonesia",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KkpKampungNelayanRecord
