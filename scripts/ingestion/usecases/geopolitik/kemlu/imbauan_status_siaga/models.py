"""Pydantic schema for Kemlu Imbauan dan Status Siaga."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImbauanStatusSiagaRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tanggal_acuan: Optional[date] = Field(
        default=None,
        alias="Tanggal Acuan",
        description="Tanggal imbauan/keputusan; tanggal estimasi WNI dapat berbeda dan dijelaskan.",
    )
    negara: Optional[str] = Field(
        default=None,
        alias="Negara",
        description="Negara terkait.",
    )
    wilayah: Optional[str] = Field(
        default=None,
        alias="Wilayah",
        description="Wilayah berlakunya imbauan sesuai sumber; negara jika tidak disebut.",
    )
    status_jenis_imbauan: Optional[str] = Field(
        default=None,
        alias="Status/Jenis Imbauan",
        description="Status Siaga Kemlu jika eksplisit; lainnya dicatat sebagai imbauan tanpa mengarang level.",
    )
    tindakan_yang_diumumkan: Optional[str] = Field(
        default=None,
        alias="Tindakan yang Diumumkan",
        description="Ringkasan langkah pelindungan, bukan hasil implementasi.",
    )
    perwakilan_penerbit: Optional[str] = Field(
        default=None,
        alias="Perwakilan/Penerbit",
        description="Instansi yang menerbitkan atau menjalankan langkah.",
    )
    jumlah_wni_disebut_sumber: Optional[int] = Field(
        default=None,
        alias="Jumlah WNI Disebut Sumber",
        ge=0,
        description="Jumlah agregat saat konteks sumber; kosong bukan nol.",
    )
    url_bukti: Optional[str] = Field(
        default=None,
        alias="URL Bukti",
        description="Sumber per record.",
    )


Record = ImbauanStatusSiagaRecord
