"""Pydantic schema — Tabel 48 Unplanned Shutdown (>2 hari) pada Kegiatan Usaha Hulu Migas  Tahun 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
