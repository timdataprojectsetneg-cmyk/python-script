"""Pydantic schema — 6.4.3 Import of Electricity (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel T6.4.3 Import Electricity.")
    country_of_origin: str | None = Field(default=None, alias="Country of Origin", description="Negara asal impor listrik.")
    hydro_pp_gwh: str | None = Field(default=None, alias="Hydro PP (GWh)", description="Jumlah energi pembangkit listrik tenaga air.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
