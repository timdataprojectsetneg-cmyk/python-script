"""Pydantic schema for ESDM Indonesian Crude Price (ICP) and benchmark crude prices."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EsdmHargaIcpRecord(BaseModel):
    periode_data: str = Field(
        description="Periode bulan dan tahun penetapan (misal: '2026-09' atau 'September 2026')."
    )
    tahun: int = Field(
        description="Tahun kalender penetapan ICP (misal: 2026)."
    )
    bulan: str = Field(
        description="Nama bulan kalender penetapan (misal: 'Januari', 'Februari', dst)."
    )
    icp_usd: float = Field(
        description="Harga rata-rata Minyak Mentah Indonesia (Indonesian Crude Price / ICP) resmi dalam USD per barel."
    )
    icp_perubahan_usd: Optional[float] = Field(
        default=None,
        description="Perubahan kenaikan atau penurunan ICP dibandingkan bulan sebelumnya dalam USD per barel."
    )
    brent_ice_usd: Optional[float] = Field(
        default=None,
        description="Harga acuan minyak mentah Brent (ICE) rata-rata bulanan dalam USD per barel."
    )
    wti_nymex_usd: Optional[float] = Field(
        default=None,
        description="Harga acuan minyak mentah West Texas Intermediate / WTI (Nymex) rata-rata bulanan dalam USD per barel."
    )
    dated_brent_usd: Optional[float] = Field(
        default=None,
        description="Harga acuan Dated Brent rata-rata bulanan dalam USD per barel."
    )
    basket_opec_usd: Optional[float] = Field(
        default=None,
        description="Harga acuan Basket OPEC rata-rata bulanan dalam USD per barel."
    )
    nomor_kepmen: Optional[str] = Field(
        default=None,
        description="Nomor Keputusan Menteri ESDM RI tentang penetapan ICP bulan berkenaan."
    )
    faktor_geopolitik_pasar: Optional[str] = Field(
        default=None,
        description="Ringkasan faktor geopolitik, rantai pasok energi global, dan dinamika pasar yang memengaruhi ICP."
    )
    sumber_dokumen_url: Optional[str] = Field(
        default=None,
        description="Tautan resmi dokumen Kepmen atau publikasi berita siaran pers Kementerian ESDM RI."
    )
    data_source: str = Field(
        default="Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = EsdmHargaIcpRecord
