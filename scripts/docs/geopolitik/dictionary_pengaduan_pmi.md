# Data Dictionary: Pengaduan PMI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Pengaduan PMI`
- Publisher: BP2MI
- Data access: `pdf`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Pelindungan WNI di Luar Negeri (1).xlsx
- Target module: `ingestion/usecases/geopolitik/bp2mi/pengaduan_pmi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| NEGARA | `negara` | String | - | Negara/ekonomi sebagaimana tabel BP2MI; Lainnya adalah agregat negara di luar daftar. |
| JAN | `jan` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada JAN 2024; angka 0 berasal dari sumber. |
| FEB | `feb` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada FEB 2024; angka 0 berasal dari sumber. |
| MAR | `mar` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada MAR 2024; angka 0 berasal dari sumber. |
| APR | `apr` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada APR 2024; angka 0 berasal dari sumber. |
| MEI | `mei` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada MEI 2024; angka 0 berasal dari sumber. |
| JUN | `jun` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada JUN 2024; angka 0 berasal dari sumber. |
| JUL | `jul` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada JUL 2024; angka 0 berasal dari sumber. |
| AGU | `agu` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada AGU 2024; angka 0 berasal dari sumber. |
| SEP | `sep` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada SEP 2024; angka 0 berasal dari sumber. |
| OKT | `okt` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada OKT 2024; angka 0 berasal dari sumber. |
| NOV | `nov` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada NOV 2024; angka 0 berasal dari sumber. |
| DES | `des` | Integer | Layanan pengaduan | Jumlah layanan pengaduan pada DES 2024; angka 0 berasal dari sumber. |
| JUMLAH | `jumlah` | Integer | Layanan pengaduan | Jumlah Januari–Desember 2024. Nilai sumber telah dicocokkan dengan penjumlahan bulanan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PengaduanPmiRecord(BaseModel):
    negara: str | None = Field(default=None, alias="NEGARA", description="Negara/ekonomi sebagaimana tabel BP2MI; Lainnya adalah agregat negara di luar daftar.")
    jan: int | None = Field(default=None, alias="JAN", description="Jumlah layanan pengaduan pada JAN 2024; angka 0 berasal dari sumber.")
    feb: int | None = Field(default=None, alias="FEB", description="Jumlah layanan pengaduan pada FEB 2024; angka 0 berasal dari sumber.")
    mar: int | None = Field(default=None, alias="MAR", description="Jumlah layanan pengaduan pada MAR 2024; angka 0 berasal dari sumber.")
    apr: int | None = Field(default=None, alias="APR", description="Jumlah layanan pengaduan pada APR 2024; angka 0 berasal dari sumber.")
    mei: int | None = Field(default=None, alias="MEI", description="Jumlah layanan pengaduan pada MEI 2024; angka 0 berasal dari sumber.")
    jun: int | None = Field(default=None, alias="JUN", description="Jumlah layanan pengaduan pada JUN 2024; angka 0 berasal dari sumber.")
    jul: int | None = Field(default=None, alias="JUL", description="Jumlah layanan pengaduan pada JUL 2024; angka 0 berasal dari sumber.")
    agu: int | None = Field(default=None, alias="AGU", description="Jumlah layanan pengaduan pada AGU 2024; angka 0 berasal dari sumber.")
    sep: int | None = Field(default=None, alias="SEP", description="Jumlah layanan pengaduan pada SEP 2024; angka 0 berasal dari sumber.")
    okt: int | None = Field(default=None, alias="OKT", description="Jumlah layanan pengaduan pada OKT 2024; angka 0 berasal dari sumber.")
    nov: int | None = Field(default=None, alias="NOV", description="Jumlah layanan pengaduan pada NOV 2024; angka 0 berasal dari sumber.")
    des: int | None = Field(default=None, alias="DES", description="Jumlah layanan pengaduan pada DES 2024; angka 0 berasal dari sumber.")
    jumlah: int | None = Field(default=None, alias="JUMLAH", description="Jumlah Januari–Desember 2024. Nilai sumber telah dicocokkan dengan penjumlahan bulanan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
