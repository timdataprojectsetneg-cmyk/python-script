# Data Dictionary: Daftar Harga BBM - MyPertamina

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Daftar Harga BBM - MyPertamina`
- Publisher: pertamina
- Data access: `scraper`
- Update frequency: Berkala (non-subsidi berubah bulanan/ad hoc; per provinsi)
- Eligible: `True`
- Data Dictionary file: [Pertamina - Harga BBM](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=0OvRhy&nav=MTVfezEzMTE0QTk0LThFQzgtNDE2RC1COTczLTMxM0I4RTdCNTlFNH0)
- Target module: `ingestion/usecases/ketahanan_energi/pertamina/daftar_harga_bbm_mypertamina/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal Berlaku | `tanggal_berlaku` | Date | tanggal | Tanggal mulai berlakunya harga. |
| Wilayah | `wilayah` | Text | provinsi | Provinsi tempat harga berlaku. |
| Jenis BBM | `jenis_bbm` | Text | kategori | Jenis produk BBM. |
| Harga | `harga` | Decimal | Rp/liter | Harga jual eceran per liter. |
| Harga Periode Sebelumnya | `harga_periode_sebelumnya` | Decimal | Rp/liter | Harga periode sebelumnya untuk membandingkan perubahan. Tidak tersedia langsung pada halaman saat ini. |

## Generated Pydantic model

```python
from decimal import Decimal
from datetime import date as DateType
from pydantic import BaseModel, Field


class DaftarHargaBbmMypertaminaRecord(BaseModel):
    tanggal_berlaku: DateType | None = Field(default=None, alias="Tanggal Berlaku", description="Tanggal mulai berlakunya harga.")
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Provinsi tempat harga berlaku.")
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis produk BBM.")
    harga: Decimal | None = Field(default=None, alias="Harga", description="Harga jual eceran per liter.")
    harga_periode_sebelumnya: Decimal | None = Field(default=None, alias="Harga Periode Sebelumnya", description="Harga periode sebelumnya untuk membandingkan perubahan. Tidak tersedia langsung pada halaman saat ini.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
