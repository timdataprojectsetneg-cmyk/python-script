"""Pydantic schema mirroring the Data Dictionary for SIPRI Military Expenditure."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SipriBelanjaMiliterRecord(BaseModel):
    negara: str = Field(
        description="Nama negara mitra diplomatik atau negara tetangga kawasan (misal: Indonesia, Singapura, Australia, China)."
    )
    tahun: int = Field(
        description="Tahun anggaran pertahanan dan belanja militer (misal: 2024, 2023)."
    )
    belanja_militer_juta_usd: float = Field(
        description="Total pengeluaran militer dalam satuan Juta US Dollar (Current Prices)."
    )
    belanja_militer_pct_pdb: Optional[float] = Field(
        default=None,
        description="Porsi pengeluaran militer terhadap Produk Domestik Bruto / PDB (%)."
    )
    belanja_militer_pct_apbn: Optional[float] = Field(
        default=None,
        description="Porsi belanja militer terhadap total belanja pemerintah / APBN (%)."
    )
    peringkat_belanja_dunia: Optional[int] = Field(
        default=None,
        description="Estimasi peringkat besaran belanja militer global pada tahun anggaran terkait."
    )
    tren_modernisasi_alutsista: Optional[str] = Field(
        default=None,
        description="Fokus pengadaan alutsista strategis (Armada Laut, Rudal Jarak Jauh, Jet Tempur, dsb)."
    )
    kawasan: Optional[str] = Field(
        default="Internasional",
        description="Kawasan geografis negara bersangkutan (Asia Tenggara, Asia Timur, Oseania, dll)."
    )
    data_source: str = Field(
        default="Stockholm International Peace Research Institute (SIPRI)",
        description="Sumber resmi database belanja militer global SIPRI."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SipriBelanjaMiliterRecord
