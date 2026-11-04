"""Pydantic schema — 6.1.1 Coal Resources and Reserves (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    province_code: int | None = Field(default=None, alias="Province Code", description="Kode provinsi sesuai kode Kementerian Dalam Negeri")
    province: str | None = Field(default=None, alias="Province", description="Nama provinsi; baris TOTAL untuk agregat nasional")
    exploration_target: str | None = Field(default=None, alias="Exploration Target", description="Target eksplorasi batubara pada provinsi bersangkutan")
    total_inventory: str | None = Field(default=None, alias="Total Inventory", description="Total inventori batubara pada provinsi bersangkutan")
    resources_inferred: str | None = Field(default=None, alias="Resources - Inferred", description="Sumber daya batubara kelas tereka (inferred)")
    resources_indicated: str | None = Field(default=None, alias="Resources - Indicated", description="Sumber daya batubara kelas terunjuk (indicated)")
    resources_measured: str | None = Field(default=None, alias="Resources - Measured", description="Sumber daya batubara kelas terukur (measured)")
    resources_total: str | None = Field(default=None, alias="Resources - Total", description="Total sumber daya batubara (inferred + indicated + measured)")
    reserves: str | None = Field(default=None, alias="Reserves", description="Cadangan batubara pada provinsi bersangkutan")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
