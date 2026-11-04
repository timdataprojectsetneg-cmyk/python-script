# Data Dictionary: Tabel Saidi Per Regional

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel Saidi Per Regional`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - SAIDI per Regional](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=4agKB4&nav=MTVfezg0MEMwRjYzLUY3MDUtNERDQS1BODIyLUNBRUY0QjMzRUQwRX0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tabel_saidi_per_regional/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Regional | `regional` | String | - | Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIDI) |
| Tipe_Baris | `tipe_baris` | String | - | Regional atau Nasional |
| SAIDI_2023 | `saidi_2023` | Numeric | Menit/pelanggan | Rata-rata lama pemadaman per pelanggan tahun 2023 |
| SAIDI_2024 | `saidi_2024` | Numeric | Menit/pelanggan | Rata-rata lama pemadaman per pelanggan tahun 2024 |
| SAIDI_2025 | `saidi_2025` | Numeric | Menit/pelanggan | Rata-rata lama pemadaman per pelanggan tahun 2025 |
| Selisih_2024_2025 | `selisih_2024_2025` | Numeric | Menit/pelanggan | SAIDI_2025 dikurangi SAIDI_2024. Negatif berarti durasi pemadaman menurun |
| Perubahan_Persen | `perubahan_persen` | Numeric | % | Selisih_2024_2025 dibagi SAIDI_2024. Negatif berarti membaik |
| Sample Data | `sample_data` | - | - | - |
| Regional | `regional` | Tipe_Baris | SAIDI_2023 | SAIDI_2024 |
| Sumatera dan Kalimantan | `sumatera_dan_kalimantan` | Regional | 521.32 | 626.67 |
| Jawa, Madura, dan Bali | `jawa_madura_dan_bali` | Regional | 229.79 | 158.34 |
| Sulawesi, Maluku, Papua, dan Nusa Tenggara | `sulawesi_maluku_papua_dan_nusa_tenggara` | Regional | 490.13 | 466.89 |
| Jumlah SAIDI | `jumlah_saidi` | Nasional | 338.13 | 320.24 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TabelSaidiPerRegionalRecord(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIDI)")
    tipe_baris: str | None = Field(default=None, alias="Tipe_Baris", description="Regional atau Nasional")
    saidi_2023: str | None = Field(default=None, alias="SAIDI_2023", description="Rata-rata lama pemadaman per pelanggan tahun 2023")
    saidi_2024: str | None = Field(default=None, alias="SAIDI_2024", description="Rata-rata lama pemadaman per pelanggan tahun 2024")
    saidi_2025: str | None = Field(default=None, alias="SAIDI_2025", description="Rata-rata lama pemadaman per pelanggan tahun 2025")
    selisih_2024_2025: str | None = Field(default=None, alias="Selisih_2024_2025", description="SAIDI_2025 dikurangi SAIDI_2024. Negatif berarti durasi pemadaman menurun")
    perubahan_persen: str | None = Field(default=None, alias="Perubahan_Persen", description="Selisih_2024_2025 dibagi SAIDI_2024. Negatif berarti membaik")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    regional: str | None = Field(default=None, alias="Regional", description="SAIDI_2024")
    sumatera_dan_kalimantan: str | None = Field(default=None, alias="Sumatera dan Kalimantan")
    jawa_madura_dan_bali: str | None = Field(default=None, alias="Jawa, Madura, dan Bali")
    sulawesi_maluku_papua_dan_nusa_tenggara: str | None = Field(default=None, alias="Sulawesi, Maluku, Papua, dan Nusa Tenggara")
    jumlah_saidi: str | None = Field(default=None, alias="Jumlah SAIDI")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
