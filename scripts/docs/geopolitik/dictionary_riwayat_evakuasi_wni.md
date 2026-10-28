# Data Dictionary: Riwayat Evakuasi WNI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Riwayat Evakuasi WNI`
- Publisher: Kemlu
- Data access: `pdf`
- Update frequency: Sesuai publikasi Renstra
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Pelindungan WNI di Luar Negeri (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemlu/riwayat_evakuasi_wni/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tahun | `tahun` | Integer | Tahun | Tahun evakuasi historis. |
| Negara/Wilayah | `negara_wilayah` | String | - | Negara atau gabungan negara pada ringkasan sumber. |
| Konteks | `konteks` | String | - | Konteks krisis diringkas dari narasi, bukan tingkat risiko. |
| WNI Dievakuasi | `wni_dievakuasi` | Integer | Orang | Jumlah WNI pada ringkasan tahunan. |
| WNA Dievakuasi | `wna_dievakuasi` | Integer | Orang | Jumlah WNA jika disebutkan; kosong bukan nol. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Halaman bukti pada Renstra. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class RiwayatEvakuasiWniRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun evakuasi historis.")
    negara_wilayah: str | None = Field(default=None, alias="Negara/Wilayah", description="Negara atau gabungan negara pada ringkasan sumber.")
    konteks: str | None = Field(default=None, alias="Konteks", description="Konteks krisis diringkas dari narasi, bukan tingkat risiko.")
    wni_dievakuasi: int | None = Field(default=None, alias="WNI Dievakuasi", description="Jumlah WNI pada ringkasan tahunan.")
    wna_dievakuasi: int | None = Field(default=None, alias="WNA Dievakuasi", description="Jumlah WNA jika disebutkan; kosong bukan nol.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Halaman bukti pada Renstra.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
