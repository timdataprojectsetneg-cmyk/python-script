"""Pydantic schema for BGN Satuan Pelayanan Pemenuhan Gizi (SPPG) MBG."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BgnSppgMbgRecord(BaseModel):
    id_sppg: str = Field(
        description="Identifier unik Satuan Pelayanan Pemenuhan Gizi (contoh: SPPG-3302-001)."
    )
    nama_sppg: str = Field(
        description="Nama unit dapur pelayanan gizi Makan Bergizi Gratis."
    )
    provinsi: str = Field(
        description="Provinsi wilayah operasional dapur."
    )
    kabupaten_kota: str = Field(
        description="Kabupaten atau kota lokasi dapur."
    )
    kecamatan: str = Field(
        description="Kecamatan lokasi dapur."
    )
    kapasitas_porsi_harian: int = Field(
        default=0,
        description="Kapasitas produksi makanan bergizi per hari (porsi/hari)."
    )
    jumlah_penerima_manfaat: int = Field(
        default=0,
        description="Jumlah sasaran siswa dan balita penerima manfaat terlayani (jiwa)."
    )
    status_operasional: str = Field(
        default="Aktif",
        description="Status operasional unit dapur (Aktif, Persiapan, Uji Coba)."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Koordinat lintang lokasi dapur."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Koordinat bujur lokasi dapur."
    )
    data_source: str = Field(
        default="Badan Gizi Nasional (BGN)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = BgnSppgMbgRecord
