# Data Dictionary: ESDM - PETA SEBARAN RASIO ELEKTRIFIKASI (RE) TRIWULAN I 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `ESDM - PETA SEBARAN RASIO ELEKTRIFIKASI (RE) TRIWULAN I 2026`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Triwulan
- Eligible: `True`
- Data Dictionary file: [ESDM - Rasio Elektrifikasi Nasional](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=72JsWU&nav=MTVfezUzODgyRjYzLTQzQjAtNDVENy05NTlCLUJFODg1ODFEM0Y3Mn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/peta_sebaran_rasio_elektrifikasi_triwulan_i_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | - | Periode data peta, mis. Triwulan I 2026 |
| Provinsi | `provinsi` | String | - | Nama provinsi sebagaimana tertulis pada peta (huruf kapital) |
| RE PLN | `re_pln_persen` | Numeric (Decimal) | % | Rasio elektrifikasi PLN per provinsi (angka biru pada peta) |
| RE NAS | `re_nas_persen` | Numeric (Decimal) | % | Rasio elektrifikasi nasional per provinsi (angka merah pada peta) |
| Satuan | `satuan` | String | - | Satuan nilai RE: % |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PetaSebaranRasioElektrifikasiTriwulanI2026Record(BaseModel):
    periode: str | None = Field(default=None, alias="periode", description="Periode data peta, mis. Triwulan I 2026")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi sebagaimana tertulis pada peta")
    re_pln_persen: float | None = Field(default=None, alias="re_pln_persen", description="Rasio elektrifikasi PLN per provinsi (%)")
    re_nas_persen: float | None = Field(default=None, alias="re_nas_persen", description="Rasio elektrifikasi nasional per provinsi (%)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai RE: %")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
