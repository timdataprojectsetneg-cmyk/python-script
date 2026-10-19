"""Pydantic schema mirroring the Data Dictionary for OFAC Trade Sanctions."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OfacSanksiPerdaganganRecord(BaseModel):
    id_sanksi: str = Field(
        description="Identifier resmi regulasi sanksi perdagangan dan embargo (misal: OFAC-SDN-36, SNK-OFAC-2026-12)."
    )
    otoritas_penerbit: str = Field(
        default="US Department of the Treasury (OFAC)",
        description="Otoritas penerbit sanksi internasional (US OFAC, European Union, UN Security Council)."
    )
    negara_sasaran: str = Field(
        description="Negara sasaran sanksi, embargo ekonomi, atau pembatasan dagang."
    )
    sektor_terkena: str = Field(
        description="Sektor ekonomi sasaran (Perbankan & Keuangan, Energi & Minyak, Logistik Maritim, Teknologi)."
    )
    tanggal_efektif: str = Field(
        description="Waktu mulai berlakunya pembatasan dalam format ISO YYYY-MM-DD."
    )
    komoditas_terdampak_indonesia: str = Field(
        description="Komoditas atau produk ekspor-impor Indonesia yang rawan terimbas sanksi."
    )
    potensi_dampak_ke_pelaku_usaha: str = Field(
        description="Analisis risiko sanksi sekunder bagi eksportir, importir, dan perbankan devisa nasional."
    )
    nama_entitas: str = Field(
        description="Nama resmi badan usaha, institusi, kapal, atau individu yang masuk dalam daftar sanksi SDN."
    )
    tipe_entitas: Optional[str] = Field(
        default="Entity / Corporate",
        description="Klasifikasi subjek sanksi: Individual, Entity/Corporate, Vessel, Aircraft."
    )
    program_sanksi: Optional[str] = Field(
        default=None,
        description="Kode program sanksi resmi OFAC (misal: RUSSIA-EO14024, CUBA, IRAN, SDGT)."
    )
    catatan_sanksi: Optional[str] = Field(
        default=None,
        description="Keterangan tambahan identifikasi entitas (alias, IMO number, alamat)."
    )
    data_source: str = Field(
        default="US Department of the Treasury (OFAC)",
        description="Sumber resmi daftar sanksi SDN OFAC."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = OfacSanksiPerdaganganRecord
