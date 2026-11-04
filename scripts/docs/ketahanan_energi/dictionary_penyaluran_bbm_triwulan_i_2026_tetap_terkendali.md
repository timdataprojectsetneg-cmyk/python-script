# Data Dictionary: Penyaluran BBM Triwulan I 2026 Tetap Terkendali

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Penyaluran BBM Triwulan I 2026 Tetap Terkendali`
- Publisher: bphmigas
- Data access: `Manual`
- Update frequency: Quarterly
- Eligible: `True`
- Data Dictionary file: [HILIR MIGAS Edisi 1 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=pZxURe&nav=MTVfezU1QzE0NzkyLUREODItNDVFOS04OUJBLURDOTJGQjBCMjYzMX0)
- Target module: `ingestion/usecases/ketahanan_energi/bphmigas/penyaluran_bbm_triwulan_i_2026_tetap_terkendali/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tahun | `tahun` | Integer | Tahun | Tahun kuota yang dianalisis |
| Periode Realisasi | `periode_realisasi` | Kategorikal | - | Periode waktu realisasi penyaluran |
| Jenis BBM | `jenis_bbm` | Kategorikal | - | Jenis BBM yang memiliki kuota penyaluran |
| Jenis BBM Subsidi | `jenis_bbm_subsidi` | Kategorikal | - | Klasifikasi BBM berdasarkan JBT atau JBKP |
| Kuota Nasional | `kuota_nasional` | Numerik | KL | Kuota penyaluran nasional untuk tahun 2026 |
| Realisasi Penyaluran | `realisasi_penyaluran` | Numerik | KL | Realisasi penyaluran pada periode yang dilaporkan |
| Persentase terhadap Kuota Nasional | `persentase_terhadap_kuota_nasional` | Numerik | % | Realisasi penyaluran dibandingkan kuota nasional tahunan |
| Persentase terhadap Kuota Periode | `persentase_terhadap_kuota_periode` | Numerik | % | Realisasi penyaluran dibandingkan kuota untuk periode tersebut |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PenyaluranBbmTriwulanI2026TetapTerkendaliRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun kuota yang dianalisis")
    periode_realisasi: str | None = Field(default=None, alias="Periode Realisasi", description="Periode waktu realisasi penyaluran")
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis BBM yang memiliki kuota penyaluran")
    jenis_bbm_subsidi: str | None = Field(default=None, alias="Jenis BBM Subsidi", description="Klasifikasi BBM berdasarkan JBT atau JBKP")
    kuota_nasional: str | None = Field(default=None, alias="Kuota Nasional", description="Kuota penyaluran nasional untuk tahun 2026")
    realisasi_penyaluran: str | None = Field(default=None, alias="Realisasi Penyaluran", description="Realisasi penyaluran pada periode yang dilaporkan")
    persentase_terhadap_kuota_nasional: str | None = Field(default=None, alias="Persentase terhadap Kuota Nasional", description="Realisasi penyaluran dibandingkan kuota nasional tahunan")
    persentase_terhadap_kuota_periode: str | None = Field(default=None, alias="Persentase terhadap Kuota Periode", description="Realisasi penyaluran dibandingkan kuota untuk periode tersebut")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
