# Data Dictionary: Artikel ANTARA - Pemerintah pangkas kuota BBM subsidi untuk 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Artikel ANTARA - Pemerintah pangkas kuota BBM subsidi untuk 2026`
- Publisher: antaranews
- Data access: `scraper`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [BPH Migas - Kuota 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=4IhRdv&nav=MTVfezYwNkI3RDgyLUYzRTktNDNCQS05OUZFLTUzNjk1MDRDQTYwNH0)
- Target module: `ingestion/usecases/ketahanan_energi/antaranews/pemerintah_pangkas_kuota_bbm_subsidi_untuk_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tahun | `tahun` | Integer | tahun | Tahun anggaran kuota. |
| Jenis BBM | `jenis_bbm` | Text | produk | Jenis BBM JBT/JBKP. |
| Kuota | `kuota` | Decimal | KL | Kuota penyaluran nasional yang diumumkan BPH Migas untuk 2026. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PemerintahPangkasKuotaBbmSubsidiUntuk2026Record(BaseModel):
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun anggaran kuota.")
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis BBM JBT/JBKP.")
    kuota: float | None = Field(default=None, alias="Kuota", description="Kuota penyaluran nasional yang diumumkan BPH Migas untuk 2026.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
