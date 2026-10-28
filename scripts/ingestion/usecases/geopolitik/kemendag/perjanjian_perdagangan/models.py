"""Pydantic schema mirroring the Data Dictionary for Perjanjian Perdagangan."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PerjanjianPerdaganganRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    nama_perjanjian: Optional[str] = Field(
        default=None, alias="Nama Perjanjian", description="Nama perjanjian pada daftar resmi Kemendag."
    )
    status_menurut_sumber: Optional[str] = Field(
        default=None, alias="Status menurut Sumber", description="Status pada periode referensi daftar."
    )
    tautan_detail: Optional[str] = Field(
        default=None, alias="Tautan Detail", description="Tautan detail perjanjian yang disediakan halaman sumber."
    )


Record = PerjanjianPerdaganganRecord
