"""Pydantic schema mirroring the Data Dictionary for the Caldara-Iacoviello GPR index."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CaldaraIacovielloIndeksRisikoGeopolitikRecord(BaseModel):
    month: str = Field(alias="month", description="Bulan observasi (YYYY-MM).")
    gpr: Optional[float] = Field(default=None, alias="GPR", description="Indeks risiko geopolitik keseluruhan.")
    gprt: Optional[float] = Field(default=None, alias="GPRT", description="Komponen ancaman geopolitik.")
    gpra: Optional[float] = Field(default=None, alias="GPRA", description="Komponen aksi/peristiwa geopolitik.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = CaldaraIacovielloIndeksRisikoGeopolitikRecord
