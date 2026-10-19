"""Pydantic schema for BPS Profil Sosioekonomi Wilayah."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BpsProfilSosioekonomiRecord(BaseModel):
    kode_wilayah_kemendagri: str = Field(
        description="Kode wilayah administrasi Kemendagri (contoh: 33.02, 32.04)."
    )
    provinsi: str = Field(
        description="Nama provinsi (contoh: Jawa Tengah, Jawa Barat, Jawa Timur)."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten/kota sasaran (contoh: Kabupaten Banyumas, Kabupaten Bandung)."
    )
    jumlah_penduduk_jiwa: int = Field(
        default=0,
        description="Jumlah penduduk total semesteran (jiwa)."
    )
    kepadatan_penduduk_km2: float = Field(
        default=0.0,
        description="Kepadatan penduduk per km persegi (jiwa/km2)."
    )
    persentase_penduduk_miskin: float = Field(
        default=0.0,
        description="Persentase penduduk miskin daerah (%)."
    )
    tingkat_pengangguran_terbuka_tpt: float = Field(
        default=0.0,
        description="Tingkat Pengangguran Terbuka daerah / TPT (%)."
    )
    indeks_pembangunan_manusia_ipm: float = Field(
        default=0.0,
        description="Indeks Pembangunan Manusia / IPM daerah (skor 0-100)."
    )
    pertumbuhan_ekonomi_pdrb_pct: float = Field(
        default=0.0,
        description="Laju pertumbuhan PDRB riil tahunan (%)."
    )
    pdrb_harga_berlaku_juta_rp: float = Field(
        default=0.0,
        description="Nominal PDRB Atas Dasar Harga Berlaku (Juta Rupiah)."
    )
    data_source: str = Field(
        default="Badan Pusat Statistik (BPS)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = BpsProfilSosioekonomiRecord
