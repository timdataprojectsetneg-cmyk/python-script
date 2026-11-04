# Data Dictionary: DAFTAR PENYALUR BADAN USAHA NIAGA UMUM BAHAN BAKAR MINYAK MELALUI STASIUN PENGISIAN BBM (KBLI 47301)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `DAFTAR PENYALUR BADAN USAHA NIAGA UMUM BAHAN BAKAR MINYAK MELALUI STASIUN PENGISIAN BBM (KBLI 47301)`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Per Semester
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Penyalur BBM Umum](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=K4BVh9&nav=MTVfezgxNzVERjhFLTk1MTctNDBGQy05MTZDLTZGRjgxQTBDNDUyNX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/daftar_penyalur_badan_usaha_niaga_umum_bahan_bakar/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No. Badan Usaha | `no_badan_usaha` | Integer | - | Nomor urut badan usaha niaga |
| Nama Badan Usaha | `nama_badan_usaha` | String | - | Nama badan usaha niaga |
| No. Penyalur | `no_penyalur` | Integer | - | Nomor urut penyalur dalam badan usaha |
| Nama Penyalur | `nama_penyalur` | String | - | Nama penyalur (agen/SPBU/SPBN/SPBKB) |
| Bentuk Penyalur | `bentuk_penyalur` | String | - | Bentuk penyalur: SPBU, SPBN, SPBKB, SPBKB (3T), dan sejenisnya |
| Alamat Fasilitas | `alamat_fasilitas` | String | - | Alamat fasilitas penyalur |
| Nama Stasiun | `nama_stasiun` | String | - | Nama stasiun pengisian BBM (SPBU BP ...). Hanya terisi untuk badan usaha yang mencantumkannya; null bila tidak ada |
| Kota/Kabupaten | `kota_kabupaten` | String | - | Kota/kabupaten lokasi fasilitas |
| Provinsi | `provinsi` | String | - | Provinsi lokasi fasilitas. Null bila dokumen tidak mencantumkan provinsi |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DaftarPenyalurBadanUsahaNiagaUmumBahanBakarRecord(BaseModel):
    no_badan_usaha: int | None = Field(default=None, alias="No. Badan Usaha", description="Nomor urut badan usaha niaga")
    nama_badan_usaha: str | None = Field(default=None, alias="Nama Badan Usaha", description="Nama badan usaha niaga")
    no_penyalur: int | None = Field(default=None, alias="No. Penyalur", description="Nomor urut penyalur dalam badan usaha")
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama penyalur (agen/SPBU/SPBN/SPBKB)")
    bentuk_penyalur: str | None = Field(default=None, alias="Bentuk Penyalur", description="Bentuk penyalur: SPBU, SPBN, SPBKB, SPBKB (3T), dan sejenisnya")
    alamat_fasilitas: str | None = Field(default=None, alias="Alamat Fasilitas", description="Alamat fasilitas penyalur")
    nama_stasiun: str | None = Field(default=None, alias="Nama Stasiun", description="Nama stasiun pengisian BBM (SPBU BP ...). Hanya terisi untuk badan usaha yang mencantumkannya; null bila tidak ada")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi fasilitas")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi fasilitas. Null bila dokumen tidak mencantumkan provinsi")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
