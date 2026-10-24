# Data Dictionary: ESDM - PETA SEBARAN RASIO ELEKTRIFIKASI (RE) TRIWULAN I 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `ESDM - PETA SEBARAN RASIO ELEKTRIFIKASI (RE) TRIWULAN I 2026`
- Publisher: esdm
- Data access: `pdf`
- Update frequency: Triwulan
- Eligible: `True`
- Data Dictionary file: [ESDM - Rasio Elektrifikasi Nasional](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=72JsWU&nav=MTVfezUzODgyRjYzLTQzQjAtNDVENy05NTlCLUJFODg1ODFEM0Y3Mn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/peta_sebaran_rasio_elektrifikasi_triwulan_i_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Sistem | `sistem` | String | - | Sistem kelistrikan pada tabel sumber (contoh: Sumatera-Bangka) |
| Skenario | `skenario` | String | - | Skenario perencanaan: ARED atau RE Base |
| Kelompok | `kelompok` | String | - | Bagian tabel: Kebutuhan, Pasokan Eksisting, atau Rekapitulasi |
| Uraian | `uraian` | String | - | Nama indikator, misalnya Beban Puncak Neto, Total Daya Mampu Neto (DMN), atau Reserve Margin |
| Satuan | `satuan` | String | - | Satuan indikator: GWh, MW, atau % |
| 2025 s.d. 2034 | `2025_s_d_2034` | Numeric | Sesuai kolom Satuan | Nilai proyeksi per tahun (satu kolom per tahun |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PetaSebaranRasioElektrifikasiTriwulanI2026Record(BaseModel):
    sistem: str | None = Field(default=None, alias="Sistem", description="Sistem kelistrikan pada tabel sumber (contoh: Sumatera-Bangka)")
    skenario: str | None = Field(default=None, alias="Skenario", description="Skenario perencanaan: ARED atau RE Base")
    kelompok: str | None = Field(default=None, alias="Kelompok", description="Bagian tabel: Kebutuhan, Pasokan Eksisting, atau Rekapitulasi")
    uraian: str | None = Field(default=None, alias="Uraian", description="Nama indikator, misalnya Beban Puncak Neto, Total Daya Mampu Neto (DMN), atau Reserve Margin")
    satuan: str | None = Field(default=None, alias="Satuan", description="Satuan indikator: GWh, MW, atau %")
    2025_s_d_2034: str | None = Field(default=None, alias="2025 s.d. 2034", description="Nilai proyeksi per tahun (satu kolom per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
