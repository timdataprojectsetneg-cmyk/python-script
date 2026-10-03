"""Pydantic schema — UMK Sumut (mirrors the Data Dictionary)."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/dictionary_<usecase>_<source>.md."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
