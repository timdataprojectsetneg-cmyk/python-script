"""Pydantic schema mirroring the Data Dictionary for EIA Harga Brent Harian."""

from __future__ import annotations

import datetime as dt
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EiaHargaBrentHarianRecord(BaseModel):
    day: dt.date = Field(
        alias="Day",
        description="Tanggal perdagangan (hari kerja). Sumber berformat MM/DD/YYYY (AS); di-parse eksplisit ke YYYY-MM-DD.",
    )
    europe_brent_spot_price_fob_dollars_per_barrel: float = Field(
        alias="Europe Brent Spot Price FOB  Dollars per Barrel",
        description="Harga spot minyak mentah Brent (FOB Eropa) harian, USD/barel.",
    )
    series_id: str = Field(
        default="RBRTE",
        description="Kode seri EIA (RBRTE = Europe Brent Spot Price FOB, harian).",
    )
    source_vendor: str = Field(
        default="Thomson Reuters",
        description="Penyedia data asli EIA.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("day", mode="before")
    @classmethod
    def _parse_us_date(cls, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if "/" in text:
                return dt.datetime.strptime(text, "%m/%d/%Y").date()
            return text[:10]
        return value


# Registry looks up models.Record
Record = EiaHargaBrentHarianRecord
