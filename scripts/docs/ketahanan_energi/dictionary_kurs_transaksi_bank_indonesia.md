# Data Dictionary: JISDOR dan Kurs Transaksi BI - "KURS TRANSAKSI BANK INDONESIA"

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `JISDOR dan Kurs Transaksi BI - "KURS TRANSAKSI BANK INDONESIA"`
- Publisher: bi
- Data access: `scraper`
- Update frequency: Daily (hari kerja)
- Eligible: `True`
- Data Dictionary file: [BI - JISDOR](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=MwQoBs&nav=MTVfezYyMkQ1QjFBLTZGOTAtNEM4Qy05RDc4LUIwQkE3MzAxNTEwQn0)
- Target module: `ingestion/usecases/ketahanan_energi/bi/kurs_transaksi_bank_indonesia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal | `tanggal` | Date | tanggal | Tanggal publikasi JISDOR. |
| Kurs JISDOR | `kurs_jisdor` | Decimal | Rp/USD | Nilai tukar referensi rupiah terhadap dolar AS. |

## Generated Pydantic model

```python
from datetime import date as DateType
from pydantic import BaseModel, Field


class KursTransaksiBankIndonesiaRecord(BaseModel):
    tanggal: DateType | None = Field(default=None, alias="Tanggal", description="Tanggal publikasi JISDOR.")
    kurs_jisdor: float | None = Field(default=None, alias="Kurs JISDOR", description="Nilai tukar referensi rupiah terhadap dolar AS.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
