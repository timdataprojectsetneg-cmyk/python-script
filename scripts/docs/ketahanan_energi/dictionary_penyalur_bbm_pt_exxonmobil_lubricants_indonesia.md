# Data Dictionary: Penyalur BBM PT ExxonMobil Lubricants Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Penyalur BBM PT ExxonMobil Lubricants Indonesia`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Per Semester
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Penyalur PT Exxon](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=tgHakD&nav=MTVfezI3MkVEOTcxLTM0MzYtNDA2MC05MDgxLUIwRkM5OTYwNkIxMX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/penyalur_bbm_pt_exxonmobil_lubricants_indonesia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nama Penyalur | `nama_penyalur` | String | - | Nama badan usaha penyalur BBM |
| Alamat Penyalur | `alamat_penyalur` | String | - | Alamat penyalur sebagaimana tertulis di laporan |
| Wilayah Penyaluran | `wilayah_penyaluran` | String | - | Provinsi wilayah penyaluran penyalur agen BBM industri (KBLI 47302); satu record per provinsi. Null untuk baris microsite |
| Nomor Microsite | `nomor_microsite` | String | - | Nomor microsite sarana fasilitas penyalur, mis. 1223-31004. Null untuk baris wilayah penyaluran |
| Kota/Kabupaten | `kota_kabupaten` | String | - | Kota/kabupaten lokasi microsite. Null untuk baris wilayah penyaluran |
| Provinsi | `provinsi` | String | - | Provinsi lokasi microsite. Null untuk baris wilayah penyaluran |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PenyalurBbmPtExxonmobilLubricantsIndonesiaRecord(BaseModel):
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama badan usaha penyalur BBM")
    alamat_penyalur: str | None = Field(default=None, alias="Alamat Penyalur", description="Alamat penyalur sebagaimana tertulis di laporan")
    wilayah_penyaluran: str | None = Field(default=None, alias="Wilayah Penyaluran", description="Provinsi wilayah penyaluran penyalur agen BBM industri (KBLI 47302); satu record per provinsi. Null untuk baris microsite")
    nomor_microsite: str | None = Field(default=None, alias="Nomor Microsite", description="Nomor microsite sarana fasilitas penyalur, mis. 1223-31004. Null untuk baris wilayah penyaluran")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi microsite. Null untuk baris wilayah penyaluran")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi microsite. Null untuk baris wilayah penyaluran")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
