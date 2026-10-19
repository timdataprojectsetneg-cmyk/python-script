"""Pydantic schema for UN Comtrade Komoditas Strategis."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UnComtradeRecord(BaseModel):
    periode_bulan: str = Field(
        description="Periode bulan transaksi perdagangan luar negeri (format YYYY-MM)."
    )
    kode_hs_2digit: str = Field(
        description="Klasifikasi 2 digit HS Code (contoh: 75, 10, 15, 27, 85)."
    )
    deskripsi_komoditas: str = Field(
        description="Nama kelompok produk strategis (Nikel Smelter, Gandum, CPO, Batubara, Semikonduktor)."
    )
    arus_perdagangan: str = Field(
        description="Arus barang: Ekspor atau Impor."
    )
    negara_mitra_utama: str = Field(
        description="Negara asal impor atau tujuan ekspor terbesar (Tiongkok, Australia, India, dll.)."
    )
    volume_ribu_ton: float = Field(
        default=0.0,
        description="Volume fisik barang dalam ribuan ton (Ribu Ton)."
    )
    nilai_fob_cif_juta_usd: float = Field(
        default=0.0,
        description="Nilai perdagangan dalam valuta USD (Juta USD)."
    )
    pertumbuhan_tahunan_pct: float = Field(
        default=0.0,
        description="Pertumbuhan nilai dibanding periode sama tahun sebelumnya (%)."
    )
    data_source: str = Field(
        default="Badan Pusat Statistik (BPS) & UN Comtrade",
        description="Lembaga penerbit resmi data statistik perdagangan."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UnComtradeRecord
