# Data Dictionary: Gambar 33- Rencana Pembangunan Jargas APBN 2025-2026 , Gambar 36 Sebaran Kilang Minyak Bumi 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Gambar 33- Rencana Pembangunan Jargas APBN 2025-2026 , Gambar 36 Sebaran Kilang Minyak Bumi `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Sebaran Kilang](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=maJZnX&nav=MTVfezg3QjcxQTY5LUI5NjktNEM1RS1BRThBLTYwODQ1MkFEOTBEM30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/rencana_pembangunan_jargas_apbn_2025_2026_gambar_36_sebaran/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| gambar | `gambar` | Categorical | - | Sumber gambar: Gambar 33 (Rencana Pembangunan Jargas APBN 2025-2026) atau Gambar 36 (Sebaran Kilang Minyak Bumi) |
| periode | `periode` | String | - | Periode rencana: 2025-2026 (Gambar 33) atau 2025 (Gambar 36) |
| nama_wilayah | `nama_wilayah` | String | - | Kab/Kota penerima jargas (Gambar 33) atau nama kilang (Gambar 36) |
| nilai | `nilai` | Numeric (Decimal) | SR atau MBSD | Target pembangunan jargas dalam SR (Gambar 33) atau kapasitas kilang dalam MBSD (Gambar 36) |
| satuan | `satuan` | Categorical | - | SR (Gambar 33) atau MBSD (Gambar 36) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class RencanaPembangunanJargasApbn20252026Gambar36SebaranRecord(BaseModel):
    gambar: str | None = Field(default=None, alias="gambar", description="Sumber gambar: Gambar 33 atau Gambar 36")
    periode: str | None = Field(default=None, alias="periode", description="Periode rencana: 2025-2026 (Gambar 33) atau 2025 (Gambar 36)")
    nama_wilayah: str | None = Field(default=None, alias="nama_wilayah", description="Kab/Kota penerima jargas (Gambar 33) atau nama kilang (Gambar 36)")
    nilai: float | None = Field(default=None, alias="nilai", description="Target jargas dalam SR (Gambar 33) atau kapasitas kilang dalam MBSD (Gambar 36)")
    satuan: str | None = Field(default=None, alias="satuan", description="SR (Gambar 33) atau MBSD (Gambar 36)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
