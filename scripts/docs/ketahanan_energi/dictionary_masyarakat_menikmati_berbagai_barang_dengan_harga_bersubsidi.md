# Data Dictionary: Masyarakat menikmati berbagai barang dengan harga bersubsidi

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Masyarakat menikmati berbagai barang dengan harga bersubsidi`
- Publisher: kemenkeu
- Data access: `Manual`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Kemenkeu - APBN KiTa Sep 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=HVAb69&nav=MTVfe0E0MjA3MDZELUVDMjctNDk0MC1BOTM3LTI2NUYwMjg5REZFM30)
- Target module: `ingestion/usecases/ketahanan_energi/kemenkeu/masyarakat_menikmati_berbagai_barang_dengan_harga_bersubsidi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Text/Integer | periode kumulatif | Periode realisasi. Pada sample 2026 dan 2025, angka menunjukkan realisasi s.d. 31 Agustus pada tahun masing-masing. |
| Jenis Barang Subsidi | `jenis_barang_subsidi` | String | - | Jenis barang atau layanan yang memperoleh subsidi |
| Realisasi 2026 | `realisasi_2026` | Numeric | Sesuai jenis barang | Volume atau jumlah penerima/pelanggan pada 2026 |
| Realisasi 2025 | `realisasi_2025` | Numeric | Sesuai jenis barang | Volume atau jumlah penerima/pelanggan pada 2025 |
| Growth | `growth` | Numeric | % | Pertumbuhan realisasi 2026 dibandingkan 2025 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class MasyarakatMenikmatiBerbagaiBarangDenganHargaBersubsidiRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode realisasi. Pada sample 2026 dan 2025, angka menunjukkan realisasi s.d. 31 Agustus pada tahun masing-masing.")
    jenis_barang_subsidi: str | None = Field(default=None, alias="Jenis Barang Subsidi", description="Jenis barang atau layanan yang memperoleh subsidi")
    realisasi_2026: str | None = Field(default=None, alias="Realisasi 2026", description="Volume atau jumlah penerima/pelanggan pada 2026")
    realisasi_2025: str | None = Field(default=None, alias="Realisasi 2025", description="Volume atau jumlah penerima/pelanggan pada 2025")
    growth: str | None = Field(default=None, alias="Growth", description="Pertumbuhan realisasi 2026 dibandingkan 2025")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
