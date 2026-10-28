# Data Dictionary: Imbauan dan Status Siaga

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Imbauan dan Status Siaga`
- Publisher: Kemlu
- Data access: `scraper`
- Update frequency: Sesuai perkembangan situasi
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Pelindungan WNI di Luar Negeri (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemlu/imbauan_status_siaga/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal Acuan | `tanggal_acuan` | Date | Tanggal | Tanggal imbauan/keputusan; tanggal estimasi WNI dapat berbeda dan dijelaskan. |
| Negara | `negara` | String | - | Negara terkait. |
| Wilayah | `wilayah` | String | - | Wilayah berlakunya imbauan sesuai sumber. |
| Status/Jenis Imbauan | `status_jenis_imbauan` | String | - | Status Siaga Kemlu jika eksplisit; lainnya dicatat sebagai imbauan tanpa mengarang level. |
| Tindakan yang Diumumkan | `tindakan_yang_diumumkan` | String | - | Ringkasan langkah pelindungan, bukan hasil implementasi. |
| Perwakilan/Penerbit | `perwakilan_penerbit` | String | - | Instansi yang menerbitkan atau menjalankan langkah. |
| Jumlah WNI Disebut Sumber | `jumlah_wni_disebut_sumber` | Integer | Orang | Jumlah agregat saat konteks sumber; kosong bukan nol. |
| URL Bukti | `url_bukti` | String | URL | Sumber per record. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class ImbauanDanStatusSiagaRecord(BaseModel):
    tanggal_acuan: date | None = Field(default=None, alias="Tanggal Acuan", description="Tanggal imbauan/keputusan; tanggal estimasi WNI dapat berbeda dan dijelaskan.")
    negara: str | None = Field(default=None, alias="Negara", description="Negara terkait.")
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Wilayah berlakunya imbauan sesuai sumber.")
    status_jenis_imbauan: str | None = Field(default=None, alias="Status/Jenis Imbauan", description="Status Siaga Kemlu jika eksplisit; lainnya dicatat sebagai imbauan tanpa mengarang level.")
    tindakan_yang_diumumkan: str | None = Field(default=None, alias="Tindakan yang Diumumkan", description="Ringkasan langkah pelindungan, bukan hasil implementasi.")
    perwakilan_penerbit: str | None = Field(default=None, alias="Perwakilan/Penerbit", description="Instansi yang menerbitkan atau menjalankan langkah.")
    jumlah_wni_disebut_sumber: int | None = Field(default=None, alias="Jumlah WNI Disebut Sumber", description="Jumlah agregat saat konteks sumber; kosong bukan nol.")
    url_bukti: str | None = Field(default=None, alias="URL Bukti", description="Sumber per record.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
