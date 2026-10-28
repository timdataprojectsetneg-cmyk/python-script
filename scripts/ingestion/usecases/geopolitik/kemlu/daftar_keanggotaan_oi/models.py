"""Pydantic schema for Daftar Keanggotaan OI (Kemlu)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DaftarKeanggotaanOiRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    kelompok_instansi: Optional[str] = Field(
        default=None,
        alias="Kelompok Instansi",
        description="Judul bagian dokumen (instansi pengampu) tempat organisasi dicantumkan, mis. DEWAN PERWAKILAN RAKYAT (DPR).",
    )
    no_pada_kelompok: Optional[int] = Field(
        default=None,
        alias="No pada Kelompok",
        ge=1,
        description="Nomor urut sebagaimana tabel; berulang antarbagian dokumen.",
    )
    nama_organisasi_internasional: Optional[str] = Field(
        default=None,
        alias="Nama Organisasi Internasional",
        description="Nama organisasi/forum pada daftar resmi.",
    )
    status_dan_tahun: Optional[str] = Field(
        default=None,
        alias="Status dan Tahun",
        description="Status keanggotaan atau kontribusi dan tahun jika dicantumkan.",
    )
    dasar_hukum: Optional[str] = Field(
        default=None,
        alias="Dasar Hukum",
        description="Dasar hukum Indonesia sebagaimana dokumen.",
    )
    unit_terkait_di_kemlu: Optional[str] = Field(
        default=None,
        alias="Unit Terkait di Kemlu",
        description="Unit Kemlu yang dicantumkan sebagai pengampu.",
    )
    keterangan: Optional[str] = Field(
        default=None,
        alias="Keterangan",
        description="Catatan sumber, termasuk peran, forum turunan atau situs bila tersedia.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None,
        alias="Halaman PDF",
        ge=1,
        description="Halaman PDF tempat record mulai.",
    )


Record = DaftarKeanggotaanOiRecord
