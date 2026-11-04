# Data Dictionary: Kontan - PLN Jaga Stok Batubara di 15,9 Hari, Sudah Amankan Kontrak 163 Juta Ton di 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Kontan - PLN Jaga Stok Batubara di 15,9 Hari, Sudah Amankan Kontrak 163 Juta Ton di 2026`
- Publisher: kontan
- Data access: `scraper`
- Update frequency: Rilis Berita
- Eligible: `True`
- Data Dictionary file: [Kontan - Stok Energi HOP](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=UZg8dv&nav=MTVfezhGMTczRjc0LTY3MzctNEUwQi05NTVFLUZCQ0VGRUVDRkQzQX0)
- Target module: `ingestion/usecases/ketahanan_energi/kontan/pln_jaga_stok_batubara_di_15_9_hari_sudah_amankan_kontrak/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Wilayah | `wilayah` | String | - | Wilayah pulau/regional: Jawa-Madura-Bali, Sumatera, Nusa Tenggara (NTB dan NTT), Kalimantan, Sulawesi, Ternate dan Tidore, Papua, atau Nasional |
| Jenis_Bahan_Bakar | `jenis_bahan_bakar` | String | - | Bahan bakar pembangkit yang stoknya diukur: Batubara atau Gas |
| HOP | `hop` | Numeric | Hari | Hari Operasi Pembangkit, yaitu lama pembangkit dapat beroperasi dengan stok bahan bakar yang tersedia tanpa pasokan baru |
| Periode | `periode` | String | - | Posisi data: sampai dengan April 2026 |
| Sumber_Pernyataan | `sumber_pernyataan` | String | - | Pihak yang menyampaikan data (Direktur Utama PLN dalam RDP Komisi XII DPR RI) |
| Sample Data | `sample_data` | - | - | - |
| Wilayah | `wilayah` | Jenis_Bahan_Bakar | HOP | Periode |
| Jawa, Madura, dan Bali | `jawa_madura_dan_bali` | Batubara | 10.31 | s.d. April 2026 |
| Sumatera | `sumatera` | Batubara | 16.23 | s.d. April 2026 |
| Nusa Tenggara (NTB dan NTT) | `nusa_tenggara_ntb_dan_ntt` | Batubara | 14.59 | s.d. April 2026 |
| Kalimantan | `kalimantan` | Batubara | 22.47 | s.d. April 2026 |
| Sulawesi | `sulawesi` | Batubara | 13.12 | s.d. April 2026 |
| Ternate dan Tidore | `ternate_dan_tidore` | Batubara | 27.28 | s.d. April 2026 |
| Papua | `papua` | Batubara | 47.95 | s.d. April 2026 |
| Nasional | `nasional` | Batubara | 15.9 | s.d. April 2026 |
| Nasional | `nasional` | Gas | 12 | s.d. April 2026 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PlnJagaStokBatubaraDi159HariSudahAmankanKontrakRecord(BaseModel):
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Wilayah pulau/regional: Jawa-Madura-Bali, Sumatera, Nusa Tenggara (NTB dan NTT), Kalimantan, Sulawesi, Ternate dan Tidore, Papua, atau Nasional")
    jenis_bahan_bakar: str | None = Field(default=None, alias="Jenis_Bahan_Bakar", description="Bahan bakar pembangkit yang stoknya diukur: Batubara atau Gas")
    hop: str | None = Field(default=None, alias="HOP", description="Hari Operasi Pembangkit, yaitu lama pembangkit dapat beroperasi dengan stok bahan bakar yang tersedia tanpa pasokan baru")
    periode: str | None = Field(default=None, alias="Periode", description="Posisi data: sampai dengan April 2026")
    sumber_pernyataan: str | None = Field(default=None, alias="Sumber_Pernyataan", description="Pihak yang menyampaikan data (Direktur Utama PLN dalam RDP Komisi XII DPR RI)")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Periode")
    jawa_madura_dan_bali: str | None = Field(default=None, alias="Jawa, Madura, dan Bali", description="s.d. April 2026")
    sumatera: str | None = Field(default=None, alias="Sumatera", description="s.d. April 2026")
    nusa_tenggara_ntb_dan_ntt: str | None = Field(default=None, alias="Nusa Tenggara (NTB dan NTT)", description="s.d. April 2026")
    kalimantan: str | None = Field(default=None, alias="Kalimantan", description="s.d. April 2026")
    sulawesi: str | None = Field(default=None, alias="Sulawesi", description="s.d. April 2026")
    ternate_dan_tidore: str | None = Field(default=None, alias="Ternate dan Tidore", description="s.d. April 2026")
    papua: str | None = Field(default=None, alias="Papua", description="s.d. April 2026")
    nasional: str | None = Field(default=None, alias="Nasional", description="s.d. April 2026")
    nasional: str | None = Field(default=None, alias="Nasional", description="s.d. April 2026")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
