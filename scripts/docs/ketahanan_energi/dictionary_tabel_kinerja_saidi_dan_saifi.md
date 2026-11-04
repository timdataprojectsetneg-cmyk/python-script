# Data Dictionary: Tabel Kinerja SAIDI dan SAIFI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel Kinerja SAIDI dan SAIFI`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Indeks Frekuensi Gangguan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=lg8jJp&nav=MTVfezQzRkIxODJGLTdFREUtNEVEMC05MTMzLTA0Nzk1NDhDMjJCQX0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tabel_kinerja_saidi_dan_saifi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| keterangan | `keterangan` | string | - | Indikator kinerja keandalan listrik: "Rerata Durasi Gangguan Per Pelanggan (SAIDI)" atau "Rerata Frekuensi Gangguan Per Pelanggan (SAIFI)" |
| satuan | `satuan` | string | - | Satuan nilai pada indikator tersebut: "Menit/Pelanggan" (SAIDI) atau "Kali/Pelanggan" (SAIFI) |
| tahun | `tahun` | integer | Tahun | Tahun data (2023, 2024, 2025) |
| nilai | `nilai` | number | Menit/Pelanggan atau Kali/Pelanggan (sesuai kolom satuan) | Nilai SAIDI atau SAIFI pada tahun terkait, dalam format desimal standar (titik) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TabelKinerjaSaidiDanSaifiRecord(BaseModel):
    keterangan: str | None = Field(default=None, alias="keterangan", description="Indikator kinerja keandalan listrik: \"Rerata Durasi Gangguan Per Pelanggan (SAIDI)\" atau \"Rerata Frekuensi Gangguan Per Pelanggan (SAIFI)\"")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai pada indikator tersebut: \"Menit/Pelanggan\" (SAIDI) atau \"Kali/Pelanggan\" (SAIFI)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: float | None = Field(default=None, alias="nilai", description="Nilai SAIDI atau SAIFI pada tahun terkait, dalam format desimal standar (titik)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
