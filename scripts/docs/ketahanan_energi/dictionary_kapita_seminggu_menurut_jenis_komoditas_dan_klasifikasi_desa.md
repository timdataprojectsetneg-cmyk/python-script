# Data Dictionary: 3.3 Rata-rata Pengeluaran per Kapita Seminggu Menurut Jenis Komoditas dan Klasifikasi Desa

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `3.3 Rata-rata Pengeluaran per Kapita Seminggu Menurut Jenis Komoditas dan Klasifikasi Desa`
- Publisher: bps
- Data access: `Manual`
- Update frequency: Semesteran
- Eligible: `True`
- Data Dictionary file: [BPS - Rata rata Pengeluaran](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=TrhNTM&nav=MTVfezc3RTA4MDEwLTVBNzEtNDc5My04Njk2LUNBNDRCREU0ODQ4NX0)
- Target module: `ingestion/usecases/ketahanan_energi/bps/kapita_seminggu_menurut_jenis_komoditas_dan_klasifikasi_desa/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Komoditas | `komoditas` | Text | jenis komoditas | Komoditas rumah tangga. |
| Perkotaan | `perkotaan` | Decimal | Rp/kapita/minggu | Pengeluaran rata-rata per kapita per minggu di perkotaan. |
| Perdesaan | `perdesaan` | Decimal | Rp/kapita/minggu | Pengeluaran rata-rata per kapita per minggu di perdesaan. |
| Perkotaan dan Perdesaan | `perkotaan_dan_perdesaan` | Decimal | Rp/kapita/minggu | Pengeluaran rata-rata per kapita per minggu gabungan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KapitaSemingguMenurutJenisKomoditasDanKlasifikasiDesaRecord(BaseModel):
    komoditas: str | None = Field(default=None, alias="Komoditas", description="Komoditas rumah tangga.")
    perkotaan: float | None = Field(default=None, alias="Perkotaan", description="Pengeluaran rata-rata per kapita per minggu di perkotaan.")
    perdesaan: float | None = Field(default=None, alias="Perdesaan", description="Pengeluaran rata-rata per kapita per minggu di perdesaan.")
    perkotaan_dan_perdesaan: float | None = Field(default=None, alias="Perkotaan dan Perdesaan", description="Pengeluaran rata-rata per kapita per minggu gabungan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
