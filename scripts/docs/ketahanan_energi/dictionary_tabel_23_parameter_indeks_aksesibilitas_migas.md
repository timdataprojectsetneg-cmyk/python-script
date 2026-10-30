# Data Dictionary: Tabel 23 Parameter Indeks Aksesibilitas Migas 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel 23 Parameter Indeks Aksesibilitas Migas `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Fasilitas Penyimpanan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=Fczg28&nav=MTVfezBCMzY4OEU2LTE2NEUtNDZEMi1CQTZCLUUzMzYyODEyREFDRX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/tabel_23_parameter_indeks_aksesibilitas_migas/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| jenis | `jenis` | Categorical | - | Kelompok: Infrastruktur, Fasilitas Pengolahan, Fasilitas Penyimpanan, atau Fasilitas Pengangkutan |
| kapasitas | `kapasitas` | Categorical | - | Jenis kapasitas, mis. Jargas (APBN+Non-APBN) Kumulatif, Konkit Nelayan, Kilang Minyak, LPG, LNG, CNG, Gas Bumi melalui Pipa |
| nilai | `nilai` | Numeric (Decimal) | Tergantung kolom | Nilai kapasitas per tahun; null bila tidak tersedia |
| satuan | `satuan` | Categorical | - | Satuan per baris, mis. SR, Paket, MBCD, Juta Ton/tahun, KL, Mton, m3, mmscfd |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class Tabel23ParameterIndeksAksesibilitasMigasRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jenis: str | None = Field(default=None, alias="jenis", description="Kelompok: Infrastruktur, Fasilitas Pengolahan, Fasilitas Penyimpanan, atau Fasilitas Pengangkutan")
    kapasitas: str | None = Field(default=None, alias="kapasitas", description="Jenis kapasitas, mis. Jargas (APBN+Non-APBN) Kumulatif, Kilang Minyak, LPG, LNG")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai kapasitas per tahun; null bila tidak tersedia")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan per baris, mis. SR, Paket, MBCD, KL, m3")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
