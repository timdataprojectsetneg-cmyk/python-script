# Data Dictionary: World Bank Commodity Markets - "Pink Sheet Data" Monthly prices September 2026 (minyak mentah dan gas global)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `World Bank Commodity Markets - "Pink Sheet Data" Monthly prices September 2026 (minyak mentah dan gas global)`
- Publisher: worldbank
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [WB - Pink Sheet](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=oi3i6v&nav=MTVfezk0MjYwRkUzLTg2NTItNEVGRS1CNDJDLTgyMTc0NDdGRURGMH0)
- Target module: `ingestion/usecases/ketahanan_energi/worldbank/pink_sheet_data_monthly_prices_september_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Text | bulan | Periode bulanan. |
| Crude Oil, Brent | `crude_oil_brent` | Decimal | US$/bbl | Harga rata-rata bulanan Brent. |
| Crude Oil, Dubai | `crude_oil_dubai` | Decimal | US$/bbl | Harga rata-rata bulanan Dubai Fateh. |
| Crude Oil, WTI | `crude_oil_wti` | Decimal | US$/bbl | Harga rata-rata bulanan WTI. |
| Natural Gas, Europe | `natural_gas_europe` | Decimal | US$/mmbtu | Harga gas alam Eropa berbasis TTF. |
| Natural Gas, US | `natural_gas_us` | Decimal | US$/mmbtu | Harga gas alam AS di Henry Hub. |
| Liquefied Natural Gas, Japan | `liquefied_natural_gas_japan` | Decimal | US$/mmbtu | Harga impor LNG Jepang. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PinkSheetDataMonthlyPricesSeptember2026Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode bulanan.")
    crude_oil_brent: float | None = Field(default=None, alias="Crude Oil, Brent", description="Harga rata-rata bulanan Brent.")
    crude_oil_dubai: float | None = Field(default=None, alias="Crude Oil, Dubai", description="Harga rata-rata bulanan Dubai Fateh.")
    crude_oil_wti: float | None = Field(default=None, alias="Crude Oil, WTI", description="Harga rata-rata bulanan WTI.")
    natural_gas_europe: float | None = Field(default=None, alias="Natural Gas, Europe", description="Harga gas alam Eropa berbasis TTF.")
    natural_gas_us: float | None = Field(default=None, alias="Natural Gas, US", description="Harga gas alam AS di Henry Hub.")
    liquefied_natural_gas_japan: float | None = Field(default=None, alias="Liquefied Natural Gas, Japan", description="Harga impor LNG Jepang.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
