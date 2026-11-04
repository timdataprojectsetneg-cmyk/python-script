# Data Dictionary: Tabel SAIFI Per Regional

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel SAIFI Per Regional`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - SAIFI Per Regional](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=HqbklD&nav=MTVfezQ2NDI5MzM5LTZGMkMtNDJEMy04NkUwLTg3RTA1NTgxMDEzRX0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tabel_saifi_per_regional/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Regional | `regional` | String | - | Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIFI) |
| Tipe_Baris | `tipe_baris` | String | - | Regional atau Nasional |
| SAIFI_2023 | `saifi_2023` | Numeric | Kali/pelanggan | Rata-rata frekuensi pemadaman per pelanggan tahun 2023 |
| SAIFI_2024 | `saifi_2024` | Numeric | Kali/pelanggan | Rata-rata frekuensi pemadaman per pelanggan tahun 2024 |
| SAIFI_2025 | `saifi_2025` | Numeric | Kali/pelanggan | Rata-rata frekuensi pemadaman per pelanggan tahun 2025 |
| Selisih_2024_2025 | `selisih_2024_2025` | Numeric | Kali/pelanggan | SAIFI_2025 dikurangi SAIFI_2024. Negatif berarti frekuensi pemadaman menurun |
| Perubahan_Persen | `perubahan_persen` | Numeric | % | Selisih_2024_2025 dibagi SAIFI_2024. Negatif berarti membaik |
| Sample Data | `sample_data` | - | - | - |
| Regional | `regional` | Tipe_Baris | SAIFI_2023 | SAIFI_2024 |
| Sumatera dan Kalimantan | `sumatera_dan_kalimantan` | Regional | 5.98 | 5.04 |
| Jawa, Madura, dan Bali | `jawa_madura_dan_bali` | Regional | 3.08 | 2.12 |
| Sulawesi, Maluku, Papua, dan Nusa Tenggara | `sulawesi_maluku_papua_dan_nusa_tenggara` | Regional | 6.63 | 4.87 |
| Jumlah SAIFI | `jumlah_saifi` | Nasional | 4.27 | 3.23 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TabelSaifiPerRegionalRecord(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIFI)")
    tipe_baris: str | None = Field(default=None, alias="Tipe_Baris", description="Regional atau Nasional")
    saifi_2023: str | None = Field(default=None, alias="SAIFI_2023", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2023")
    saifi_2024: str | None = Field(default=None, alias="SAIFI_2024", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2024")
    saifi_2025: str | None = Field(default=None, alias="SAIFI_2025", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2025")
    selisih_2024_2025: str | None = Field(default=None, alias="Selisih_2024_2025", description="SAIFI_2025 dikurangi SAIFI_2024. Negatif berarti frekuensi pemadaman menurun")
    perubahan_persen: str | None = Field(default=None, alias="Perubahan_Persen", description="Selisih_2024_2025 dibagi SAIFI_2024. Negatif berarti membaik")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    regional: str | None = Field(default=None, alias="Regional", description="SAIFI_2024")
    sumatera_dan_kalimantan: str | None = Field(default=None, alias="Sumatera dan Kalimantan")
    jawa_madura_dan_bali: str | None = Field(default=None, alias="Jawa, Madura, dan Bali")
    sulawesi_maluku_papua_dan_nusa_tenggara: str | None = Field(default=None, alias="Sulawesi, Maluku, Papua, dan Nusa Tenggara")
    jumlah_saifi: str | None = Field(default=None, alias="Jumlah SAIFI")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
