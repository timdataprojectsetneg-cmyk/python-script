"""Pydantic schema mirroring the Data Dictionary for IMF PortWatch Daily Chokepoints."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ChokepointsMaritimRecord(BaseModel):
    date: str = Field(description="Tanggal observasi harian (format YYYY-MM-DD).")
    year: Optional[int] = Field(default=None, description="Tahun observasi.")
    month: Optional[int] = Field(default=None, description="Bulan observasi.")
    day: Optional[int] = Field(default=None, description="Hari observasi.")
    portid: str = Field(description="ID unik chokepoint PortWatch (misal: chokepoint1, chokepoint5).")
    portname: str = Field(description="Nama chokepoint (misal: Malacca Strait, Suez Canal, Bab el-Mandeb Strait).")
    n_container: Optional[int] = Field(default=0, description="Jumlah lintasan kapal kontainer.")
    n_dry_bulk: Optional[int] = Field(default=0, description="Jumlah lintasan kapal dry bulk.")
    n_general_cargo: Optional[int] = Field(default=0, description="Jumlah lintasan kapal general cargo.")
    n_roro: Optional[int] = Field(default=0, description="Jumlah lintasan kapal ro-ro.")
    n_tanker: Optional[int] = Field(default=0, description="Jumlah lintasan kapal tanker minyak/gas.")
    n_cargo: Optional[int] = Field(default=0, description="Jumlah lintasan seluruh kapal kargo.")
    n_total: Optional[int] = Field(default=0, description="Total seluruh lintasan kapal pada titik chokepoint.")
    capacity_container: Optional[float] = Field(default=None, description="Kapasitas muatan kapal kontainer (TEU).")
    capacity_dry_bulk: Optional[float] = Field(default=None, description="Kapasitas muatan dry bulk (DWT).")
    capacity_general_cargo: Optional[float] = Field(default=None, description="Kapasitas muatan general cargo (DWT).")
    capacity_roro: Optional[float] = Field(default=None, description="Kapasitas kapal ro-ro.")
    capacity_tanker: Optional[float] = Field(default=None, description="Kapasitas muatan tanker (DWT).")
    capacity_cargo: Optional[float] = Field(default=None, description="Kapasitas muatan kargo total.")
    capacity: Optional[float] = Field(default=None, description="Akumulasi kapasitas total lintasan kapal.")
    object_id: Optional[int] = Field(default=None, alias="ObjectId", description="ID internal objek ArcGIS Server.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = ChokepointsMaritimRecord
