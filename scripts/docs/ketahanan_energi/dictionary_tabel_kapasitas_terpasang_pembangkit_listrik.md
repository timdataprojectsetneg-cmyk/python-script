# Data Dictionary: Tabel Kapasitas Terpasang Pembangkit Listrik (MW)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel Kapasitas Terpasang Pembangkit Listrik (MW)`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Tabel Kapasitas Terpasang Pembangkit Listrik (MW) Hal 215](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=aha29r&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wMTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tabel_kapasitas_terpasang_pembangkit_listrik/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Regional | `regional` | String | - | Wilayah regional PLN (misal: Sumatera dan Kalimantan; Jawa, Madura, dan Bali; Sulawesi, Maluku, Papua, dan Nusa Tenggara) beserta baris total (Jumlah SAIDI) |
| Tahun | `tahun` | Year | - | Tahun pengukuran SAIDI (2023, 2024, 2025) |
| SAIDI | `saidi` | Float | menit/pelanggan | Rata-rata durasi gangguan listrik yang dialami setiap pelanggan dalam satu tahun pada regional tersebut |
| Selisih | `selisih` | Float | menit/pelanggan | Selisih perubahan SAIDI antara tahun 2024 dan 2025 (2025 - 2024). Nilai negatif berarti durasi gangguan berkurang (keandalan membaik). Hanya terisi pada baris tahun 2025; tahun lain null |
| Persentase | `persentase` | Percent | % | Persentase perubahan SAIDI dari tahun 2024 ke 2025. Nilai negatif berarti penurunan. Hanya terisi pada baris tahun 2025; tahun lain null |
| tipe_baris | `tipe_baris` | String | - | Tipe baris: detail (data per regional) atau total (Jumlah SAIDI nasional) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TabelKapasitasTerpasangPembangkitListrikRecord(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Wilayah regional PLN (misal: Sumatera dan Kalimantan; Jawa, Madura, dan Bali; Sulawesi, Maluku, Papua, dan Nusa Tenggara) beserta baris total (Jumlah SAIDI)")
    tahun: str | None = Field(default=None, alias="Tahun", description="Tahun pengukuran SAIDI (2023, 2024, 2025)")
    saidi: float | None = Field(default=None, alias="SAIDI", description="Rata-rata durasi gangguan listrik yang dialami setiap pelanggan dalam satu tahun pada regional tersebut")
    selisih: float | None = Field(default=None, alias="Selisih", description="Selisih perubahan SAIDI antara tahun 2024 dan 2025 (2025 - 2024). Nilai negatif berarti durasi gangguan berkurang (keandalan membaik). Hanya terisi pada baris tahun 2025; tahun lain null")
    persentase: str | None = Field(default=None, alias="Persentase", description="Persentase perubahan SAIDI dari tahun 2024 ke 2025. Nilai negatif berarti penurunan. Hanya terisi pada baris tahun 2025; tahun lain null")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Tipe baris: detail (data per regional) atau total (Jumlah SAIDI nasional)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
