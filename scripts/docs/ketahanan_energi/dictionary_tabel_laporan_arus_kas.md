# Data Dictionary: Tabel Laporan arus kas

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel Laporan arus kas`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Statement of Cash Flows](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=foIC2M&nav=MTVfezUzMkQ1MURBLThGMTUtNEYyQy04REU5LTQxNUVBRjI3NkMxM30)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tabel_laporan_arus_kas/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Integer | Tahun | Tahun buku |
| Aktivitas | `aktivitas` | Categorical | - | Operasi atau Investasi |
| Komponen Arus Kas | `komponen_arus_kas` | String | - | Pos pada laporan arus kas metode langsung |
| Jenis | `jenis` | Categorical | - | Capex, Penerimaan, atau Total |
| Nilai | `nilai` | Numeric (Float) | Rp juta | Bertanda kurung = kas keluar |
| Rasio | `rasio` | Numeric (Float) | - | Rumus: capex / depresiasi (sheet COGS) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TabelLaporanArusKasRecord(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku")
    aktivitas: str | None = Field(default=None, alias="Aktivitas", description="Operasi atau Investasi")
    komponen_arus_kas: str | None = Field(default=None, alias="Komponen Arus Kas", description="Pos pada laporan arus kas metode langsung")
    jenis: str | None = Field(default=None, alias="Jenis", description="Capex, Penerimaan, atau Total")
    nilai: str | None = Field(default=None, alias="Nilai", description="Bertanda kurung = kas keluar")
    rasio: str | None = Field(default=None, alias="Rasio", description="Rumus: capex / depresiasi (sheet COGS)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
