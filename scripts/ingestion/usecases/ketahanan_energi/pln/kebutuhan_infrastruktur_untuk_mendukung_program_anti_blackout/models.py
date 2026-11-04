"""Pydantic schema — Tabel 5.52 Daftar Kebutuhan Infrastruktur untuk mendukung Program Anti Blackout (mirrors the Data Dictionary)."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
