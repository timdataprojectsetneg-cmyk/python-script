# Data Dictionary: Tabel 17 Kuota dan Realisasi LPG Tabung 3 kg

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel 17 Kuota dan Realisasi LPG Tabung 3 kg`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [LKJ - Kuota dan Realisasi LPG3](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=fFhh1E&nav=MTVfezBGMTlBNUIyLUQ5MjAtNEVGOC05QjlDLTAzNjQ5QzM4MzYxMX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/kuota_dan_realisasi_lpg_tabung_3_kg/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| komponen | `komponen` | String | - | Kuota LPG Tabung 3 kg, Realisasi LPG Tabung 3 kg, atau Persentase Realisasi |
| nilai | `nilai` | Float | Juta MT atau % | Kuota dan realisasi dalam Juta MT; persentase realisasi dalam % |
| satuan | `satuan` | String | - | Juta MT atau % (sesuai komponen) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KuotaDanRealisasiLpgTabung3KgRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    komponen: str | None = Field(default=None, alias="komponen", description="Kuota LPG Tabung 3 kg, Realisasi LPG Tabung 3 kg, atau Persentase Realisasi")
    nilai: float | None = Field(default=None, alias="nilai", description="Kuota dan realisasi dalam Juta MT; persentase realisasi dalam %")
    satuan: str | None = Field(default=None, alias="satuan", description="Juta MT atau % (sesuai komponen)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
