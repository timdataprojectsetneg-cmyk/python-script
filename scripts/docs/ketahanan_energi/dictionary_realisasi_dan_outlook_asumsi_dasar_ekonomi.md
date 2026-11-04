# Data Dictionary: REALISASI DAN OUTLOOK ASUMSI DASAR EKONOMI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `REALISASI DAN OUTLOOK ASUMSI DASAR EKONOMI`
- Publisher: kemenkeu
- Data access: `scraper`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Kemenkeu - ASUMSI DASAR EKONOMI](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=KQZlBO&nav=MTVfe0E0MjA3MDZELUVDMjctNDk0MC1BOTM3LTI2NUYwMjg5REZFM30)
- Target module: `ingestion/usecases/ketahanan_energi/kemenkeu/realisasi_dan_outlook_asumsi_dasar_ekonomi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Waktu | Tahun | Tahun asumsi makro yang dianalisis |
| Indikator | `indikator` | Kategorikal | - | Jenis indikator ekonomi makro |
| APBN | `apbn` | Numerik | Sesuai indikator | Nilai yang ditetapkan dalam APBN 2026 |
| Realisasi | `realisasi` | Numerik | Sesuai indikator | Nilai realisasi indikator pada periode yang tercantum dalam sumber |
| Outlook | `outlook` | Numerik/Rentang | Sesuai indikator | Perkiraan atau rentang nilai indikator untuk 2026 |
| Status Realisasi | `status_realisasi` | Kategorikal | - | Keterangan periode realisasi, misalnya eop atau ytd |
| Harga Minyak Mentah Indonesia | `harga_minyak_mentah_indonesia` | Numerik | US$/barel | Harga minyak mentah Indonesia yang digunakan dalam asumsi makro |
| Nilai Tukar | `nilai_tukar` | Numerik | Rp/US$ | Nilai tukar rupiah terhadap dolar AS |
| Lifting Minyak | `lifting_minyak` | Numerik | ribu barel/hari | Realisasi dan target lifting minyak |
| Lifting Gas | `lifting_gas` | Numerik | ribu barel setara minyak/hari | Realisasi dan target lifting gas |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class RealisasiDanOutlookAsumsiDasarEkonomiRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Tahun asumsi makro yang dianalisis")
    indikator: str | None = Field(default=None, alias="Indikator", description="Jenis indikator ekonomi makro")
    apbn: str | None = Field(default=None, alias="APBN", description="Nilai yang ditetapkan dalam APBN 2026")
    realisasi: str | None = Field(default=None, alias="Realisasi", description="Nilai realisasi indikator pada periode yang tercantum dalam sumber")
    outlook: str | None = Field(default=None, alias="Outlook", description="Perkiraan atau rentang nilai indikator untuk 2026")
    status_realisasi: str | None = Field(default=None, alias="Status Realisasi", description="Keterangan periode realisasi, misalnya eop atau ytd")
    harga_minyak_mentah_indonesia: str | None = Field(default=None, alias="Harga Minyak Mentah Indonesia", description="Harga minyak mentah Indonesia yang digunakan dalam asumsi makro")
    nilai_tukar: str | None = Field(default=None, alias="Nilai Tukar", description="Nilai tukar rupiah terhadap dolar AS")
    lifting_minyak: str | None = Field(default=None, alias="Lifting Minyak", description="Realisasi dan target lifting minyak")
    lifting_gas: str | None = Field(default=None, alias="Lifting Gas", description="Realisasi dan target lifting gas")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
