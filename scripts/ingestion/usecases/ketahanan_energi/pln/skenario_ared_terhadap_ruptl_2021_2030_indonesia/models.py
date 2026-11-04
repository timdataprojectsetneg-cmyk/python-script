"""Pydantic schema — PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    jenis: str | None = Field(default=None, alias="jenis", description="Jenis pembangkit (PLTU, PLTP, BESS, dll.), level tegangan transmisi atau gardu induk, atau jenis distribusi (JTM, JTR, Trafo Distribusi)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan: MW (Pembangkit), kms (Transmisi, JTM, JTR), MVA (Gardu Induk, Trafo Distribusi)")
    ruptl_sebelumnya: int | None = Field(default=None, alias="ruptl_sebelumnya", description="Nilai pada RUPTL 2021-2030. Null jika di sumber tertulis \"-\"")
    usulan_perubahan: int | None = Field(default=None, alias="usulan_perubahan", description="Nilai usulan perubahan pada RUPTL 2025-2034 Skenario ARED. Null jika \"-\"")
    selisih: int | None = Field(default=None, alias="selisih", description="Selisih usulan perubahan terhadap RUPTL sebelumnya. Negatif untuk nilai berkurung. Null jika \"-\"")

    no: int | None = Field(default=None, alias="no", description="Nomor urut baris")
    kategori: str | None = Field(default=None, alias="kategori", description="Kategori infrastruktur: Pembangkit, Transmisi, Gardu Induk, atau Distribusi")
    model_config = {"populate_by_name": True, "extra": "ignore"}
