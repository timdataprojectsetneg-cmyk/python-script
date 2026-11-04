# Data Dictionary: BPH Migas – BPH Migas Pastikan Pasokan dan Penyaluran BBM Terjaga dengan Baik

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPH Migas – BPH Migas Pastikan Pasokan dan Penyaluran BBM Terjaga dengan Baik`
- Publisher: esdm
- Data access: `scraper`
- Update frequency: Berkala
- Eligible: `True`
- Data Dictionary file: [BPH Migas_Pasokan dan Penyaluran](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=bt32A5&nav=MTVfezBFNzQxQTNCLTVDMDktNDUwQS04RURFLTc2ODU3ODYxMTQ5N30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/migas_pastikan_pasokan_dan_penyaluran_bbm_terjaga_dengan_baik/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tanggal_publikasi | `tanggal_publikasi` | Date | YYYY-MM-DD | Tanggal artikel terbit |
| cakupan | `cakupan` | String | - | Cakupan wilayah data |
| kapasitas_penyimpanan_bbm | `kapasitas_penyimpanan_bbm` | Integer | KL | Kapasitas penyimpanan BBM nasional saat ini |
| jenis_bbm_cadangan | `jenis_bbm_cadangan` | String | - | Jenis BBM untuk cadangan penyangga |
| kebutuhan_cadangan_penyangga_2035 | `kebutuhan_cadangan_penyangga_2035` | Decimal | Juta barel | Kebutuhan cadangan penyangga hingga 2035 |
| tambahan_ketahanan_stok | `tambahan_ketahanan_stok` | Decimal | Hari | Tambahan ketahanan dari penambahan kapasitas penyimpanan |
| dasar_hukum | `dasar_hukum` | String | - | Regulasi yang dirujuk |
| sumber | `sumber` | String | - | Nama sumber dan penyampai |

## Generated Pydantic model

```python
from datetime import date as DateType
from pydantic import BaseModel, Field


class MigasPastikanPasokanDanPenyaluranBbmTerjagaDenganBaikRecord(BaseModel):
    tanggal_publikasi: DateType | None = Field(default=None, alias="tanggal_publikasi", description="Tanggal artikel terbit")
    cakupan: str | None = Field(default=None, alias="cakupan", description="Cakupan wilayah data")
    kapasitas_penyimpanan_bbm: int | None = Field(default=None, alias="kapasitas_penyimpanan_bbm", description="Kapasitas penyimpanan BBM nasional saat ini")
    jenis_bbm_cadangan: str | None = Field(default=None, alias="jenis_bbm_cadangan", description="Jenis BBM untuk cadangan penyangga")
    kebutuhan_cadangan_penyangga_2035: float | None = Field(default=None, alias="kebutuhan_cadangan_penyangga_2035", description="Kebutuhan cadangan penyangga hingga 2035")
    tambahan_ketahanan_stok: float | None = Field(default=None, alias="tambahan_ketahanan_stok", description="Tambahan ketahanan dari penambahan kapasitas penyimpanan")
    dasar_hukum: str | None = Field(default=None, alias="dasar_hukum", description="Regulasi yang dirujuk")
    sumber: str | None = Field(default=None, alias="sumber", description="Nama sumber dan penyampai")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
