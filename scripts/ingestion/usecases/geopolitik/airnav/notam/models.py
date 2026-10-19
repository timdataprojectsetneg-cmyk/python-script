"""Pydantic schema for AirNav NOTAM & Kesiapan Evakuasi WNI."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AirNavNotamRecord(BaseModel):
    id_wilayah: str = Field(
        description="Identifier rencana kontinjensi wilayah (misal: 'EVAC-2026-ME-01')."
    )
    negara: str = Field(
        description="Negara lokasi kontinjensi krisis atau zona konflik."
    )
    kawasan: str = Field(
        description="Kawasan geopolitik internasional."
    )
    status_siaga_evakuasi: str = Field(
        default="Siaga I",
        description="Tingkat siaga kedaruratan (Siaga I, Siaga II, Siaga III)."
    )
    estimasi_wni_terdampak: int = Field(
        default=0,
        description="Jumlah estimasi WNI terdata di zona bahaya."
    )
    jalur_evakuasi_utama: Optional[str] = Field(
        default=None,
        description="Rute dan moda evakuasi (Jalur Udara, Koridor Darat, Konvoi Laut)."
    )
    titik_kumpul_safe_haven: Optional[str] = Field(
        default=None,
        description="Lokasi aman penampungan WNI sebelum evakuasi (KBRI, Safe Haven)."
    )
    status_ruang_udara_notam: str = Field(
        default="Restricted",
        description="Status NOTAM penerbangan (Open, Restricted, Closed)."
    )
    kesiapan_bandara_pelabuhan: Optional[str] = Field(
        default=None,
        description="Kondisi operasional fasilitas bandara/pelabuhan keberangkatan."
    )
    koordinasi_satgas_tni_kemlu: Optional[str] = Field(
        default=None,
        description="Kesiapan koordinasi Satgas Gabungan TNI & Kemlu RI."
    )
    data_source: str = Field(
        default="AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = AirNavNotamRecord
