# Data Dictionary: Tabel  Nilai Energi Terpakai Untuk Produksi Listrik dari Pemakaian Sumber Energi

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel  Nilai Energi Terpakai Untuk Produksi Listrik dari Pemakaian Sumber Energi`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Nilai Energi Terpakai Produksi (Page 110)](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=usKHDd&nav=MTVfezBFRDJCM0MxLUZBMTUtNEFBRi05RjlCLUJFOTA0MTlDMEM3Rn0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/nilai_energi_terpakai_untuk_produksi_listrik/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| jenis_pemakaian | `jenis_pemakaian` | string | - | Jenis pemakaian sendiri listrik untuk operasional: "Sentral Pembangkit (termasuk Susut Trafo Pembangkit)", "Gardu Induk", "Distribusi", atau "Total" |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "item" (jenis pemakaian) atau "total" (total keseluruhan) |
| satuan | `satuan` | string | - | Satuan nilai pada baris tersebut: "GWh" atau "GJ" |
| tahun | `tahun` | integer | Tahun | Tahun data (2023, 2024, 2025) |
| nilai | `nilai` | number | GWh atau GJ (sesuai kolom satuan) | Besar pemakaian sendiri listrik untuk operasional pada jenis pemakaian, satuan, dan tahun terkait. Desimal untuk GWh, bilangan bulat untuk GJ |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class NilaiEnergiTerpakaiUntukProduksiListrikRecord(BaseModel):
    jenis_pemakaian: str | None = Field(default=None, alias="jenis_pemakaian", description="Jenis pemakaian sendiri listrik untuk operasional: \"Sentral Pembangkit (termasuk Susut Trafo Pembangkit)\", \"Gardu Induk\", \"Distribusi\", atau \"Total\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (jenis pemakaian) atau \"total\" (total keseluruhan)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai pada baris tersebut: \"GWh\" atau \"GJ\"")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: float | None = Field(default=None, alias="nilai", description="Besar pemakaian sendiri listrik untuk operasional pada jenis pemakaian, satuan, dan tahun terkait. Desimal untuk GWh, bilangan bulat untuk GJ")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
