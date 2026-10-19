"""Pydantic schema for World Bank Bilateral Macroeconomic Indicators."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WorldBankIndikatorMakroRecord(BaseModel):
    negara: str = Field(
        description="Nama negara mitra diplomatik atau negara pembanding (misal: 'Indonesia', 'Jepang', 'Tiongkok')."
    )
    kode_iso3: str = Field(
        description="Kode resmi 3 huruf ISO3 negara (misal: 'IDN', 'JPN', 'CHN', 'USA')."
    )
    kawasan: Optional[str] = Field(
        default=None,
        description="Kawasan geopolitik (misal: 'Asia Tenggara', 'Asia Timur', 'Amerika Utara', 'Eropa')."
    )
    tahun: int = Field(
        description="Tahun kalender observasi indikator makroekonomi."
    )
    populasi_juta_jiwa: Optional[float] = Field(
        default=None,
        description="Jumlah penduduk total negara dalam satuan juta jiwa."
    )
    pdb_nominal_miliar_usd: Optional[float] = Field(
        default=None,
        description="Produk Domestik Bruto (PDB) nominal negara dalam satuan miliar USD."
    )
    pdb_per_kapita_usd: Optional[float] = Field(
        default=None,
        description="Produk Domestik Bruto per kapita dalam satuan USD."
    )
    pertumbuhan_pdb_pct: Optional[float] = Field(
        default=None,
        description="Laju pertumbuhan ekonomi / PDB riil tahunan dalam persen (%)."
    )
    inflasi_pct: Optional[float] = Field(
        default=None,
        description="Tingkat inflasi tahunan (Consumer Price Index) dalam persen (%)."
    )
    nilai_ekspor_ri_ke_mitra_usd: Optional[float] = Field(
        default=None,
        description="Total nilai ekspor barang/jasa dari Indonesia ke negara mitra dalam USD."
    )
    nilai_impor_ri_dari_mitra_usd: Optional[float] = Field(
        default=None,
        description="Total nilai impor barang/jasa Indonesia dari negara mitra dalam USD."
    )
    neraca_perdagangan_ri_usd: Optional[float] = Field(
        default=None,
        description="Surplus atau defisit neraca perdagangan bilateral Indonesia dalam USD."
    )
    data_source: str = Field(
        default="World Bank Open Data (World Development Indicators)",
        description="Lembaga penerbit resmi data internasional."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = WorldBankIndikatorMakroRecord
