# Data Dictionary: Indeks Harga Pangan FAO

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Indeks Harga Pangan FAO`
- Publisher: FAO
- Data access: `excel`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/fao/indeks_harga_pangan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Date | `date` | String | YYYY-MM | Bulan observasi. |
| Food Price Index | `food_price_index` | Decimal | Indeks (2014–2016=100) | FAO Food Price Index (FFPI) gabungan 5 kelompok komoditas. Angka utama untuk kartu harga pangan di tab Dampak. |
| Meat | `meat` | Decimal | Indeks (2014–2016=100) | Sub-indeks harga daging. Indeks harga (2014–2016 = 100), rata-rata bulanan tertimbang pangsa ekspor. |
| Dairy | `dairy` | Decimal | Indeks (2014–2016=100) | Sub-indeks harga produk susu. Indeks harga (2014–2016 = 100), rata-rata bulanan tertimbang pangsa ekspor. |
| Cereals | `cereals` | Decimal | Indeks (2014–2016=100) | Sub-indeks harga serealia (gandum, jagung, beras, dll.). Relevan untuk ketahanan pangan RI (impor gandum). |
| Oils | `oils` | Decimal | Indeks (2014–2016=100) | Sub-indeks harga minyak nabati (termasuk minyak sawit — komoditas ekspor utama RI). |
| Sugar | `sugar` | Decimal | Indeks (2014–2016=100) | Sub-indeks harga gula. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class IndeksHargaPanganFaoRecord(BaseModel):
    date: str | None = Field(default=None, alias="Date", description="Bulan observasi.")
    food_price_index: float | None = Field(default=None, alias="Food Price Index", description="FAO Food Price Index (FFPI) gabungan 5 kelompok komoditas. Angka utama untuk kartu harga pangan di tab Dampak.")
    meat: float | None = Field(default=None, alias="Meat", description="Sub-indeks harga daging. Indeks harga (2014–2016 = 100), rata-rata bulanan tertimbang pangsa ekspor.")
    dairy: float | None = Field(default=None, alias="Dairy", description="Sub-indeks harga produk susu. Indeks harga (2014–2016 = 100), rata-rata bulanan tertimbang pangsa ekspor.")
    cereals: float | None = Field(default=None, alias="Cereals", description="Sub-indeks harga serealia (gandum, jagung, beras, dll.). Relevan untuk ketahanan pangan RI (impor gandum).")
    oils: float | None = Field(default=None, alias="Oils", description="Sub-indeks harga minyak nabati (termasuk minyak sawit — komoditas ekspor utama RI).")
    sugar: float | None = Field(default=None, alias="Sugar", description="Sub-indeks harga gula.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
