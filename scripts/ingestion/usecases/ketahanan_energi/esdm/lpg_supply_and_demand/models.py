"""Pydantic schema — 6.2.9 LPG Supply and Demand (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data")
    production_gas_refinery_ton: str | None = Field(default=None, alias="Production Gas Refinery (Ton)", description="Produksi LPG dari kilang gas")
    production_oil_refinery_ton: str | None = Field(default=None, alias="Production Oil Refinery (Ton)", description="Produksi LPG dari kilang minyak")
    production_total_ton: str | None = Field(default=None, alias="Production Total (Ton)", description="Total produksi LPG dalam negeri")
    export_ton: str | None = Field(default=None, alias="Export (Ton)", description="Jumlah LPG yang diekspor")
    import_ton: str | None = Field(default=None, alias="Import (Ton)", description="Jumlah LPG yang diimpor")
    sales_ton: str | None = Field(default=None, alias="Sales (Ton)", description="Penjualan LPG (termasuk refrigerant)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
