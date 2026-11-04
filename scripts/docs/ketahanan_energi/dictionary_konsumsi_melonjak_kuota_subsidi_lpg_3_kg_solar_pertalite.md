# Data Dictionary: Artikel KONTAN - Konsumsi Melonjak, Kuota Subsidi LPG 3 kg, Solar & Pertalite Terancam Jebol pada 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Artikel KONTAN - Konsumsi Melonjak, Kuota Subsidi LPG 3 kg, Solar & Pertalite Terancam Jebol pada 2026`
- Publisher: esdm
- Data access: `scraper`
- Update frequency: Insidental
- Eligible: `True`
- Data Dictionary file: [ESDM-Pertamina - RDP 26 Agu 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=6I58yl&nav=MTVfe0QyRTk5QjEwLUI3Q0MtNDIyMi04OEVDLUQ4MkM2QjNDRTM0Q30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/konsumsi_melonjak_kuota_subsidi_lpg_3_kg_solar_pertalite/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Text | bulan | Periode realisasi kumulatif yang disebut dalam RDP 26 Agustus 2026. |
| Jenis Energi | `jenis_energi` | Text | produk | Jenis energi bersubsidi atau penugasan. |
| Kuota | `kuota` | Decimal | juta MT atau juta KL | Kuota 2026 yang dirujuk dalam bahan rapat atau APBN, bila tersedia. |
| Realisasi s.d. Juli | `realisasi_s_d_juli` | Decimal | juta MT atau juta KL | Volume kumulatif sampai Juli 2026. |
| Prognosa 2026 | `prognosa_2026` | Decimal | juta MT atau juta KL | Proyeksi volume sampai akhir 2026 menurut paparan rapat. |
| Keterangan terhadap Kuota | `keterangan_terhadap_kuota` | Text | persen atau teks | Rasio atau selisih prognosa terhadap kuota bila angka kuota tersedia. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KonsumsiMelonjakKuotaSubsidiLpg3KgSolarPertaliteRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode realisasi kumulatif yang disebut dalam RDP 26 Agustus 2026.")
    jenis_energi: str | None = Field(default=None, alias="Jenis Energi", description="Jenis energi bersubsidi atau penugasan.")
    kuota: float | None = Field(default=None, alias="Kuota", description="Kuota 2026 yang dirujuk dalam bahan rapat atau APBN, bila tersedia.")
    realisasi_s_d_juli: float | None = Field(default=None, alias="Realisasi s.d. Juli", description="Volume kumulatif sampai Juli 2026.")
    prognosa_2026: float | None = Field(default=None, alias="Prognosa 2026", description="Proyeksi volume sampai akhir 2026 menurut paparan rapat.")
    keterangan_terhadap_kuota: str | None = Field(default=None, alias="Keterangan terhadap Kuota", description="Rasio atau selisih prognosa terhadap kuota bila angka kuota tersedia.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
