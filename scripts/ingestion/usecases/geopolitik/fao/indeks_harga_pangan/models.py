"""Pydantic schema mirroring the Data Dictionary for FAO Food Price Index."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FaoIndeksHargaPanganRecord(BaseModel):
    date: str = Field(alias="Date", description="Bulan observasi (YYYY-MM).")
    food_price_index: Optional[float] = Field(
        default=None,
        alias="Food Price Index",
        description="FAO Food Price Index (FFPI) gabungan 5 kelompok komoditas (2014-2016=100).",
    )
    meat: Optional[float] = Field(default=None, alias="Meat", description="Sub-indeks harga daging.")
    dairy: Optional[float] = Field(default=None, alias="Dairy", description="Sub-indeks harga produk susu.")
    cereals: Optional[float] = Field(default=None, alias="Cereals", description="Sub-indeks harga serealia.")
    oils: Optional[float] = Field(default=None, alias="Oils", description="Sub-indeks harga minyak nabati.")
    sugar: Optional[float] = Field(default=None, alias="Sugar", description="Sub-indeks harga gula.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = FaoIndeksHargaPanganRecord
