# Data Dictionary: 6.5.1 Geothermal Resources and Reserves

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.5.1 Geothermal Resources and Reserves`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Geothermal Resources and Reserves](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=1bBm2n&nav=MTVfezg0MzEzNTdFLTY0ODMtNEQzMC1CRTQyLTFGRDdDMzkxNTA2M30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/geothermal_resources_and_reserves/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Label | `label` | Tipe Data | Satuan | Deskripsi |
| tahun | `tahun` | Integer | Tahun | Tahun posisi data (as of Desember 2025) |
| kategori | `kategori` | String | - | Kategori klasifikasi potensi panas bumi: Speculative, Hipotethical (kategori sumber daya/resources), Possible, Probable, Proven (kategori cadangan/reserves). Penulisan "Hipotethical" mengikuti dokumen sumber |
| provinsi | `provinsi` | String | - | Nama provinsi lokasi potensi panas bumi sesuai tabel sumber (contoh: Aceh, West Java, Southeast Sulawesi) |
| nilai | `nilai` | Integer | MW | Besaran potensi panas bumi (sumber daya atau cadangan) pada kategori dan provinsi terkait |
| satuan | `satuan` | String | - | Satuan nilai, yaitu MW (megawatt) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class GeothermalResourcesAndReservesRecord(BaseModel):
    label: str | None = Field(default=None, alias="Label", description="Deskripsi")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun posisi data (as of Desember 2025)")
    kategori: str | None = Field(default=None, alias="kategori", description="Kategori klasifikasi potensi panas bumi: Speculative, Hipotethical (kategori sumber daya/resources), Possible, Probable, Proven (kategori cadangan/reserves). Penulisan \"Hipotethical\" mengikuti dokumen sumber")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi lokasi potensi panas bumi sesuai tabel sumber (contoh: Aceh, West Java, Southeast Sulawesi)")
    nilai: int | None = Field(default=None, alias="nilai", description="Besaran potensi panas bumi (sumber daya atau cadangan) pada kategori dan provinsi terkait")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai, yaitu MW (megawatt)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
