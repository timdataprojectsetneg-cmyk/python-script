"""Pydantic schema for Kemenkes SATUSEHAT Cek Kesehatan Gratis (CKG)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemenkesSatusehatCkgRecord(BaseModel):
    id_fasyankes: str = Field(
        description="Kode registrasi fasyankes SATUSEHAT Kemenkes (contoh: P33020101)."
    )
    nama_puskesmas_klinik: str = Field(
        description="Nama fasilitas pelayanan kesehatan pelaksana skrining CKG."
    )
    provinsi: str = Field(
        description="Provinsi lokasi fasyankes."
    )
    kabupaten_kota: str = Field(
        description="Kabupaten atau kota lokasi fasyankes."
    )
    jumlah_skrining_balita: int = Field(
        default=0,
        description="Jumlah balita yang telah diskrining tumbuh kembang (jiwa)."
    )
    jumlah_skrining_dewasa: int = Field(
        default=0,
        description="Jumlah usia produktif yang diskrining penyakit tidak menular / PTM (jiwa)."
    )
    jumlah_skrining_lansia: int = Field(
        default=0,
        description="Jumlah warga lansia yang diskrining kesehatan geriatri (jiwa)."
    )
    kasus_terindikasi_stunting: int = Field(
        default=0,
        description="Jumlah balita yang terindikasi stunting atau wasting (kasus)."
    )
    kasus_dirujuk_ke_rs: int = Field(
        default=0,
        description="Jumlah pasien yang memerlukan rujukan ke rumah sakit lanjutan (kasus)."
    )
    data_source: str = Field(
        default="Kementerian Kesehatan RI (SATUSEHAT & Ditjen Kesmas)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemenkesSatusehatCkgRecord
