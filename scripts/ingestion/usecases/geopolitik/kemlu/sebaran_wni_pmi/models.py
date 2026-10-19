"""Pydantic schema for Kemlu Sebaran WNI & PMI."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemluSebaranWniPmiRecord(BaseModel):
    negara: str = Field(
        description="Negara tempat tinggal atau penempatan WNI/PMI."
    )
    kawasan: str = Field(
        description="Kawasan geografis penempatan diplomatik (misal: 'Asia Tenggara', 'Timur Tengah', 'Amerika Utara')."
    )
    jumlah_wni_lapor_diri: int = Field(
        default=0,
        description="Total akumulasi WNI yang aktif melakukan lapor diri pada Portal Peduli WNI."
    )
    pekerja_migran_pmi: int = Field(
        default=0,
        description="Jumlah estimasi Pekerja Migran Indonesia (PMI) resmi terdaftar."
    )
    pelajar_mahasiswa: int = Field(
        default=0,
        description="Jumlah pelajar dan mahasiswa Indonesia di negara bersangkutan."
    )
    staf_profesional_ekspat: int = Field(
        default=0,
        description="Jumlah staf profesional, diaspora, atau ekspatriat Indonesia."
    )
    perwakilan_ri_pengampu: str = Field(
        description="Nama KBRI / KJRI / KRI yang membawahi wilayah hukum penempatan."
    )
    data_source: str = Field(
        default="Kementerian Luar Negeri RI & Kementerian Perlindungan Pekerja Migran Indonesia (KP2MI)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemluSebaranWniPmiRecord
