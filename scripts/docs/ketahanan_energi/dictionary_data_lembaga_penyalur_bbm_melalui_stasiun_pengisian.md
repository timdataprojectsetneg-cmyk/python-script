# Data Dictionary: DATA LEMBAGA PENYALUR BBM MELALUI STASIUN PENGISIAN - (KBLI 47301) 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `DATA LEMBAGA PENYALUR BBM MELALUI STASIUN PENGISIAN - (KBLI 47301) `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Per Semester
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Penyalur BBM Pertamina](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=3M745q&nav=MTVfezQxNEE3MzEwLTFGMDUtNDMzRC05NTM5LTM4NUY0MDIwODYwN30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/data_lembaga_penyalur_bbm_melalui_stasiun_pengisian/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No | `no` | Integer | - | Nomor urut baris tabel |
| No SPBU | `no_spbu` | String | - | Nomor SPBU/penyalur, mis. 4854304 atau 4P57611 |
| Nama Penyalur | `nama_penyalur` | String | - | Nama badan usaha penyalur BBM |
| Bentuk Penyalur | `bentuk_penyalur` | String | - | SPBU, SPBUN, Pertashop, AMT, atau SPBB (Agen BBM/SPBU/SPBN/SPB Bunker/Lainnya) |
| Alamat SPBU | `alamat_spbu` | String | - | Alamat stasiun pengisian sebagaimana tertulis di laporan |
| Kota/Kabupaten | `kota_kabupaten` | String | - | Kota/kabupaten lokasi SPBU, mis. Kab Kebumen |
| Provinsi | `provinsi` | String | - | Provinsi lokasi SPBU |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DataLembagaPenyalurBbmMelaluiStasiunPengisianRecord(BaseModel):
    no: int | None = Field(default=None, alias="No", description="Nomor urut baris tabel")
    no_spbu: str | None = Field(default=None, alias="No SPBU", description="Nomor SPBU/penyalur, mis. 4854304 atau 4P57611")
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama badan usaha penyalur BBM")
    bentuk_penyalur: str | None = Field(default=None, alias="Bentuk Penyalur", description="SPBU, SPBUN, Pertashop, AMT, atau SPBB (Agen BBM/SPBU/SPBN/SPB Bunker/Lainnya)")
    alamat_spbu: str | None = Field(default=None, alias="Alamat SPBU", description="Alamat stasiun pengisian sebagaimana tertulis di laporan")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi SPBU, mis. Kab Kebumen")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi SPBU")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
