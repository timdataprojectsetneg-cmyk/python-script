"""Pydantic schema mirroring Data Dictionary — Kasus Perselisihan."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class JenisPerselisihan(str, Enum):
    HAK = "Perselisihan Hak"
    KEPENTINGAN = "Perselisihan Kepentingan"
    PHK = "PHK"
    SERIKAT_PEKERJA = "Serikat Pekerja"


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode")
    jenis_perselisihan: JenisPerselisihan = Field(alias="Jenis_Perselisihan")
    jumlah_pusat: int = Field(default=0, alias="Jumlah_Pusat", ge=0)
    jumlah_daerah: int = Field(default=0, alias="Jumlah_Daerah", ge=0)
    bipartit: int = Field(default=0, alias="Bipartit", ge=0)
    mediasi_pb: int = Field(default=0, alias="Mediasi_PB", ge=0)
    mediasi_anjuran: int = Field(default=0, alias="Mediasi_Anjuran", ge=0)
    konsiliasi: int = Field(default=0, alias="Konsiliasi", ge=0)
    arbitrasi: int = Field(default=0, alias="Arbitrasi", ge=0)
    hakim_hi: int = Field(default=0, alias="Hakim_HI", ge=0)
    sisa_kasus: int = Field(default=0, alias="Sisa_Kasus", ge=0)

    model_config = {"populate_by_name": True, "extra": "ignore"}
