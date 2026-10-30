"""Pydantic schema — DATA LEMBAGA PENYALUR BBM MELALUI STASIUN PENGISIAN - (KBLI 47301) (mirrors the Data Dictionary)."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
