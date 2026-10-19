"""Pydantic schema mirroring the Data Dictionary for SIRANAP Referral Hospitals."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SiranapRsRujukanRecord(BaseModel):
    kode_rs: str = Field(
        description="Kode registrasi resmi Rumah Sakit Kementerian Kesehatan (misal: 3171012, 3302012)."
    )
    nama_rumah_sakit: str = Field(
        description="Nama resmi rumah sakit rujukan terdekat dari lokasi kunker."
    )
    kelas_rs: str = Field(
        default="Kelas B (Rujukan Daerah)",
        description="Tipe kelas RS (Kelas A Rujukan Utama/Nasional, Kelas B, Kelas C, RS TNI/Polri)."
    )
    jarak_dari_lokasi_km: Optional[float] = Field(
        default=5.0,
        description="Estimasi jarak tempuh dari titik pusat kegiatan kunker (km)."
    )
    waktu_tempuh_menit: Optional[int] = Field(
        default=15,
        description="Estimasi waktu tempuh iring-iringan darurat medis kepresidenan (menit)."
    )
    ketersediaan_icu_vvip: int = Field(
        default=0,
        description="Jumlah tempat tidur ICU/ICCU/VVIP/VIP siap pakai tanpa antrian."
    )
    bed_occupancy_rate_pct: float = Field(
        default=75.0,
        description="Estimasi tingkat keterisian ranjang RS (Bed Occupancy Rate - BOR %)."
    )
    kesiapan_ambulans_vvip: str = Field(
        default="Siap Siaga 24 Jam",
        description="Status kesiapan mini-ICU ambulans kepresidenan dan tim advance medis."
    )
    alamat_rs: Optional[str] = Field(
        default=None,
        description="Alamat fisik fasyankes rumah sakit."
    )
    total_bed_kosong: int = Field(
        default=0,
        description="Total seluruh tempat tidur rawat inap yang kosong saat ini."
    )
    total_ruangan_terdata: int = Field(
        default=0,
        description="Jumlah unit ruangan/kamar rawat inap terdata pada SIRANAP."
    )
    provinsi: Optional[str] = Field(
        default=None,
        description="Provinsi fasyankes rumah sakit."
    )
    kabupaten_kota: Optional[str] = Field(
        default=None,
        description="Kabupaten / Kota fasyankes rumah sakit."
    )
    data_source: str = Field(
        default="Kementerian Kesehatan RI - SIRANAP",
        description="Sumber data resmi penyedia ketersediaan tempat tidur rawat inap."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SiranapRsRujukanRecord
