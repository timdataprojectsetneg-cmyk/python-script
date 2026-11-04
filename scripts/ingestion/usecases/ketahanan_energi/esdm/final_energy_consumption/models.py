"""Pydantic schema — Final Energy Consumption (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    tahun: int | None = Field(default=None, alias="tahun", description="Tahun konsumsi energi final (grafik 2019–2025)")
    sektor: str | None = Field(default=None, alias="sektor", description="Industry, Household, Commercial, Transportation, Others, atau Total")
    konsumsi: str | None = Field(default=None, alias="konsumsi", description="Konsumsi energi final per sektor")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi terhadap total konsumsi energi final (diagram donat)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
