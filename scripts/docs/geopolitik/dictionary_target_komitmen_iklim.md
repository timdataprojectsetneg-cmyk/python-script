# Data Dictionary: Target Komitmen Iklim

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Target Komitmen Iklim`
- Publisher: UNFCCC
- Data access: `pdf`
- Update frequency: Sesuai pengajuan NDC
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/unfccc/target_komitmen_iklim/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Indikator | `indikator` | String | - | Indikator kuantitatif dari Second NDC. |
| Skenario/Konteks | `skenario_konteks` | String | - | Skenario emisi atau kebijakan pendukung yang dikutip dokumen. |
| Tahun Target | `tahun_target` | Integer | Tahun | Horizon target/proyeksi. |
| Nilai Bawah | `nilai_bawah` | Decimal | Mengikuti satuan | Batas bawah; untuk target tunggal nilainya sama dengan batas atas. |
| Nilai Atas | `nilai_atas` | Decimal | Mengikuti satuan | Batas atas rentang asli. |
| Satuan | `satuan` | String | - | Satuan sumber, bukan hasil konversi. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Nomor halaman PDF bukti. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TargetKomitmenIklimRecord(BaseModel):
    indikator: str | None = Field(default=None, alias="Indikator", description="Indikator kuantitatif dari Second NDC.")
    skenario_konteks: str | None = Field(default=None, alias="Skenario/Konteks", description="Skenario emisi atau kebijakan pendukung yang dikutip dokumen.")
    tahun_target: int | None = Field(default=None, alias="Tahun Target", description="Horizon target/proyeksi.")
    nilai_bawah: float | None = Field(default=None, alias="Nilai Bawah", description="Batas bawah; untuk target tunggal nilainya sama dengan batas atas.")
    nilai_atas: float | None = Field(default=None, alias="Nilai Atas", description="Batas atas rentang asli.")
    satuan: str | None = Field(default=None, alias="Satuan", description="Satuan sumber, bukan hasil konversi.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Nomor halaman PDF bukti.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
