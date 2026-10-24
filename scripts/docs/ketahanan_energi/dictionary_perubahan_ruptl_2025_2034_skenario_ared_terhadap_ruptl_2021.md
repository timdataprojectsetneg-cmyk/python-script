# Data Dictionary: PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia`
- Publisher: pln
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Perubahan RUPTL 2025 – 2034 Skenario ARED](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=frjGAS&nav=MTVfe0UyOEY1NENGLTdEOTEtNDcxRC1BNkIwLUVDNTExRDI4NkNERn0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/perubahan_ruptl_2025_2034_skenario_ared_terhadap_ruptl_2021/models.py`

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


class PerubahanRuptl20252034SkenarioAredTerhadapRuptl2021Record(BaseModel):
    sistem: str | None = Field(default=None, alias="Sistem", description="Sistem kelistrikan pada tabel sumber (contoh: Sumatera-Bangka)")
    skenario: str | None = Field(default=None, alias="Skenario", description="Skenario perencanaan: ARED atau RE Base")
    kelompok: str | None = Field(default=None, alias="Kelompok", description="Bagian tabel: Kebutuhan, Pasokan Eksisting, atau Rekapitulasi")
    uraian: str | None = Field(default=None, alias="Uraian", description="Nama indikator, misalnya Beban Puncak Neto, Total Daya Mampu Neto (DMN), atau Reserve Margin")
    satuan: str | None = Field(default=None, alias="Satuan", description="Satuan indikator: GWh, MW, atau %")
    2025_s_d_2034: str | None = Field(default=None, alias="2025 s.d. 2034", description="Nilai proyeksi per tahun (satu kolom per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
