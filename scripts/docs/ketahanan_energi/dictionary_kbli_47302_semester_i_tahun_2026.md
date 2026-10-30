# Data Dictionary: Daftar Penyalur Badan Usaha Niaga Umum Bahan Bakar Minyak melalui selain di Stasiun Pengisian (Agen BBM Industri) – KBLI 47302 Semester I Tahun 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Daftar Penyalur Badan Usaha Niaga Umum Bahan Bakar Minyak melalui selain di Stasiun Pengisian (Agen BBM Industri) – KBLI 47302 Semester I Tahun 2026`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Per Semester
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Penyalur BBM Agen](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=LbDOMV&nav=MTVfezMzQzBGMTZBLURBRTAtNENCQS04QkMzLTUyQ0VBNzc1NTQzMn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/kbli_47302_semester_i_tahun_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No. Badan Usaha | `no_badan_usaha` | Integer | - | Nomor urut badan usaha niaga umum |
| Nama Badan Usaha | `nama_badan_usaha` | String | - | Nama badan usaha niaga umum BBM |
| No. Penyalur | `no_penyalur` | Integer | - | Nomor urut penyalur dalam badan usaha; null jika badan usaha tidak memiliki penyalur |
| Nama Penyalur | `nama_penyalur` | String | - | Nama penyalur BBM agen industri |
| Alamat Kantor | `alamat_kantor` | String | - | Alamat kantor penyalur sebagaimana tertulis di laporan |
| Wilayah Penyaluran (Provinsi) | `wilayah_penyaluran` | String | - | Wilayah penyaluran, dapat berisi beberapa provinsi/wilayah dalam satu teks |
| Keterangan | `keterangan` | String | - | Status badan usaha bila tidak memiliki penyalur, mis. TIDAK MEMILIKI PENYALUR, BELUM MELAPORKAN PENYALUR, atau sanksi |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Kbli47302SemesterITahun2026Record(BaseModel):
    no_badan_usaha: int | None = Field(default=None, alias="no_badan_usaha", description="Nomor urut badan usaha niaga umum")
    nama_badan_usaha: str | None = Field(default=None, alias="nama_badan_usaha", description="Nama badan usaha niaga umum BBM")
    no_penyalur: int | None = Field(default=None, alias="no_penyalur", description="Nomor urut penyalur dalam badan usaha")
    nama_penyalur: str | None = Field(default=None, alias="nama_penyalur", description="Nama penyalur BBM agen industri")
    alamat_kantor: str | None = Field(default=None, alias="alamat_kantor", description="Alamat kantor penyalur sebagaimana tertulis di laporan")
    wilayah_penyaluran: str | None = Field(default=None, alias="wilayah_penyaluran", description="Wilayah penyaluran, dapat berisi beberapa provinsi/wilayah")
    keterangan: str | None = Field(default=None, alias="keterangan", description="Status badan usaha bila tidak memiliki penyalur")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
