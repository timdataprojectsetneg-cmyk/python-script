# Data Dictionary: Kasus Pelindungan WNI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Kasus Pelindungan WNI`
- Publisher: Kemlu
- Data access: `pdf`
- Update frequency: Tahunan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Pelindungan WNI di Luar Negeri (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemlu/kasus_pelindungan_wni/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tahun | `tahun` | Integer | Tahun | Tahun laporan kinerja. |
| Kelompok Kasus | `kelompok_kasus` | String | - | Kelompok pada Matriks Informasi Kinerja. |
| Jenis Kasus | `jenis_kasus` | String | - | Subjenis kasus sesuai label lampiran. |
| Ditangani | `ditangani` | Integer | Kasus | Angka kolom ditangani, dipertahankan meski terdapat anomali antarbagian. |
| Selesai | `selesai` | Integer | Kasus | Angka kolom selesai. Tidak diasumsikan cohort yang sama dengan ditangani. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Halaman tabel sumber (130–132). |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KasusPelindunganWniRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun laporan kinerja.")
    kelompok_kasus: str | None = Field(default=None, alias="Kelompok Kasus", description="Kelompok pada Matriks Informasi Kinerja.")
    jenis_kasus: str | None = Field(default=None, alias="Jenis Kasus", description="Subjenis kasus sesuai label lampiran.")
    ditangani: int | None = Field(default=None, alias="Ditangani", description="Angka kolom ditangani, dipertahankan meski terdapat anomali antarbagian.")
    selesai: int | None = Field(default=None, alias="Selesai", description="Angka kolom selesai. Tidak diasumsikan cohort yang sama dengan ditangani.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Halaman tabel sumber (130–132).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
