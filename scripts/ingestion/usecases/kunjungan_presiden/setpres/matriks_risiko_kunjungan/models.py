"""Pydantic schema for Setpres Matriks Risiko Kunjungan."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SetpresMatriksRisikoKunjunganRecord(BaseModel):
    id_risiko: str = Field(
        description="Nomor register analisis risiko kunker (misal: 'RSK-2026-01')."
    )
    kategori_risiko: str = Field(
        description="Kategori risiko (Protokoler, Medis, Cuaca, Kerawanan Massa, Aksesibilitas)."
    )
    deskripsi_ancaman: str = Field(
        description="Potensi kendala atau gangguan yang teridentifikasi di lokasi kunjungan."
    )
    tingkat_probabilitas: str = Field(
        default="Sedang",
        description="Tingkat peluang terjadinya kendala (Tinggi, Sedang, Rendah)."
    )
    tingkat_dampak: str = Field(
        default="Signifikan",
        description="Dampak terhadap kelancaran acara kepresidenan (Kritis, Signifikan, Minor)."
    )
    rencana_mitigasi: Optional[str] = Field(
        default=None,
        description="Langkah antisipasi dan skenario cadangan (Plan B)."
    )
    penanggung_jawab_pic: Optional[str] = Field(
        default="Paspampres & Protokol Setpres",
        description="Satgas pengampu pelaksanaan mitigasi (Paspampres, Protokol Setpres, Dinkes, Kodim)."
    )
    data_source: str = Field(
        default="Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SetpresMatriksRisikoKunjunganRecord
