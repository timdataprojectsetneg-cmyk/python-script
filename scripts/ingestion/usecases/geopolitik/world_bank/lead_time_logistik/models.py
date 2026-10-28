"""Pydantic schema mirroring dictionary_lead_time_logistik.md."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadTimeLogistikRecord(BaseModel):
    indicator_code: str = Field(description="Kode indikator World Bank.")
    indicator_name: Optional[str] = Field(default=None, description="Nama ukuran lead time.")
    year: int = Field(description="Tahun observasi yang memiliki nilai.")
    value: Optional[float] = Field(default=None, description="Median lead time menurut survei (hari).")
    unit: Optional[str] = Field(default=None, description="Satuan nilai.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


Record = LeadTimeLogistikRecord
