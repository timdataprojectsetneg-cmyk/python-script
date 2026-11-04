# Data Dictionary: Realisasi Subsidi dan Kompensasi s.d. 31 Agustus 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Realisasi Subsidi dan Kompensasi s.d. 31 Agustus 2026`
- Publisher: kemenkeu
- Data access: `Manual`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Kemenkeu - Realisasi Subsidi dan Kompensasi](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=Fdx1eD&nav=MTVfe0FFQjZBRUE5LUM5NEQtNDE3Ni04RkMwLUE2ODUxN0FBNjVDMn0)
- Target module: `ingestion/usecases/ketahanan_energi/kemenkeu/realisasi_subsidi_dan_kompensasi_s_d_31_agustus_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Text/Integer | tahun / periode kumulatif | Tahun atau periode realisasi. 2022-2025 merupakan tahunan, sedangkan 2026 adalah kumulatif s.d. 31 Agustus 2026. |
| Realisasi Subsidi | `realisasi_subsidi` | Numeric | Rp triliun | Nilai realisasi belanja subsidi pada periode/tahun yang ditampilkan |
| Realisasi Kompensasi | `realisasi_kompensasi` | Numeric | Rp triliun | Nilai realisasi belanja kompensasi pada periode/tahun yang ditampilkan |
| Total Subsidi dan Kompensasi | `total_subsidi_dan_kompensasi` | Numeric | Rp triliun | Total realisasi subsidi dan kompensasi |
| Pertumbuhan | `pertumbuhan` | Numeric | % | Pertumbuhan realisasi subsidi dan kompensasi dibandingkan periode sebelumnya |
| Persentase terhadap APBN | `persentase_terhadap_apbn` | Numeric | % | Persentase realisasi subsidi dan kompensasi terhadap APBN |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class RealisasiSubsidiDanKompensasiSD31Agustus2026Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Tahun atau periode realisasi. 2022-2025 merupakan tahunan, sedangkan 2026 adalah kumulatif s.d. 31 Agustus 2026.")
    realisasi_subsidi: str | None = Field(default=None, alias="Realisasi Subsidi", description="Nilai realisasi belanja subsidi pada periode/tahun yang ditampilkan")
    realisasi_kompensasi: str | None = Field(default=None, alias="Realisasi Kompensasi", description="Nilai realisasi belanja kompensasi pada periode/tahun yang ditampilkan")
    total_subsidi_dan_kompensasi: str | None = Field(default=None, alias="Total Subsidi dan Kompensasi", description="Total realisasi subsidi dan kompensasi")
    pertumbuhan: str | None = Field(default=None, alias="Pertumbuhan", description="Pertumbuhan realisasi subsidi dan kompensasi dibandingkan periode sebelumnya")
    persentase_terhadap_apbn: str | None = Field(default=None, alias="Persentase terhadap APBN", description="Persentase realisasi subsidi dan kompensasi terhadap APBN")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
