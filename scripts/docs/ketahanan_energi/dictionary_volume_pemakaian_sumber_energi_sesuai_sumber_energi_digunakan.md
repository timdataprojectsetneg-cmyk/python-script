# Data Dictionary: Table Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Table Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Table Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan (109 )](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=zG8xEZ&nav=MTVfezMxOEM5Mzg3LTdGMzAtNDlDNS1CQjI4LUY5MTAwOEJENkZBOH0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/volume_pemakaian_sumber_energi_sesuai_sumber_energi_digunakan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| kategori | `kategori` | string | - | Kelompok sumber energi: "Sumber Energi Tak Terbarukan", "Sumber Energi Terbarukan", atau "Total Energi Terpakai dari Sumber Energi Tak Terbarukan dan Terbarukan" |
| sumber_energi | `sumber_energi` | string | - | Nama sumber atau jenis energi (Bahan Bakar Minyak, Batu Bara, Gas Alam, Biomassa, Bahan Bakar Nabati), atau "Total" untuk baris total |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "item" (sumber energi), "subtotal" (total per kategori), atau "grand_total" (total keseluruhan) |
| tahun | `tahun` | integer | Tahun | Tahun data (2023, 2024, 2025) |
| nilai | `nilai` | integer | GigaJoule (GJ) | Nilai energi terpakai untuk produksi listrik pada sumber energi dan tahun terkait |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class VolumePemakaianSumberEnergiSesuaiSumberEnergiDigunakanRecord(BaseModel):
    kategori: str | None = Field(default=None, alias="kategori", description="Kelompok sumber energi: \"Sumber Energi Tak Terbarukan\", \"Sumber Energi Terbarukan\", atau \"Total Energi Terpakai dari Sumber Energi Tak Terbarukan dan Terbarukan\"")
    sumber_energi: str | None = Field(default=None, alias="sumber_energi", description="Nama sumber atau jenis energi (Bahan Bakar Minyak, Batu Bara, Gas Alam, Biomassa, Bahan Bakar Nabati), atau \"Total\" untuk baris total")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (sumber energi), \"subtotal\" (total per kategori), atau \"grand_total\" (total keseluruhan)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai energi terpakai untuk produksi listrik pada sumber energi dan tahun terkait")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
