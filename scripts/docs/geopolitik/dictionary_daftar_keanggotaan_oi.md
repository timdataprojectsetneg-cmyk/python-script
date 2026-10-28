# Data Dictionary: Daftar Keanggotaan OI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Daftar Keanggotaan OI`
- Publisher: Kemlu
- Data access: `pdf`
- Update frequency: Sesuai pemutakhiran daftar
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemlu/daftar_keanggotaan_oi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No pada Kelompok | `no_pada_kelompok` | Integer | Urutan | Nomor urut sebagaimana tabel; dapat berulang antarbagian dokumen. |
| Nama Organisasi Internasional | `nama_organisasi_internasional` | String | - | Nama organisasi/forum pada daftar resmi. |
| Status dan Tahun | `status_dan_tahun` | String | - | Status keanggotaan atau kontribusi dan tahun jika dicantumkan. |
| Dasar Hukum | `dasar_hukum` | String | - | Dasar hukum Indonesia sebagaimana dokumen. |
| Unit Terkait di Kemlu | `unit_terkait_di_kemlu` | String | - | Unit Kemlu yang dicantumkan sebagai pengampu. |
| Keterangan | `keterangan` | String | - | Catatan sumber, termasuk peran, forum turunan atau situs bila tersedia. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Halaman PDF tempat record diekstrak. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DaftarKeanggotaanOiRecord(BaseModel):
    no_pada_kelompok: int | None = Field(default=None, alias="No pada Kelompok", description="Nomor urut sebagaimana tabel; dapat berulang antarbagian dokumen.")
    nama_organisasi_internasional: str | None = Field(default=None, alias="Nama Organisasi Internasional", description="Nama organisasi/forum pada daftar resmi.")
    status_dan_tahun: str | None = Field(default=None, alias="Status dan Tahun", description="Status keanggotaan atau kontribusi dan tahun jika dicantumkan.")
    dasar_hukum: str | None = Field(default=None, alias="Dasar Hukum", description="Dasar hukum Indonesia sebagaimana dokumen.")
    unit_terkait_di_kemlu: str | None = Field(default=None, alias="Unit Terkait di Kemlu", description="Unit Kemlu yang dicantumkan sebagai pengampu.")
    keterangan: str | None = Field(default=None, alias="Keterangan", description="Catatan sumber, termasuk peran, forum turunan atau situs bila tersedia.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Halaman PDF tempat record diekstrak.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
