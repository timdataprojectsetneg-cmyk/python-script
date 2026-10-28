# Data Dictionary: Impor Komoditas Strategis

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Impor Komoditas Strategis`
- Publisher: UN
- Data access: `api`
- Update frequency: Tahunan (query sampel)
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/un/impor_komoditas_strategis/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| period | `period` | Integer | Tahun | Tahun perdagangan. |
| reporterCode | `reportercode` | Integer | UN M49 | Kode negara pelapor. 360 = Indonesia. |
| flowCode | `flowcode` | String | Kode | X = ekspor; M = impor. |
| partnerCode | `partnercode` | Integer | UN M49 | Kode negara mitra dalam hasil API. |
| partner_name | `partner_name` | String | - | Label mitra dipetakan dari kode UN M49; bukan field terisi API preview. |
| cmdCode | `cmdcode` | String | HS | TOTAL = semua barang; 10 = serealia; 27 = bahan bakar mineral; 72 = besi/baja; 85 = mesin/peralatan listrik. |
| primaryValue | `primaryvalue` | Decimal | USD | Nilai utama perdagangan dari API. |
| isReported | `isreported` | Boolean | - | Flag data dilaporkan langsung, dipertahankan dari sumber. |
| isAggregate | `isaggregate` | Boolean | - | Flag agregasi sumber. |
| totalCommodityValue | `totalcommodityvalue` | Decimal | USD | Total impor Indonesia untuk kelompok HS yang sama (partnerCode=0), sebagai denominator pangsa pemasok. |
| supplierShare | `suppliershare` | Decimal | Proporsi 0–1 | Nilai impor dari negara pemasok dibagi total impor Indonesia untuk kelompok HS yang sama. Ini indikator konsentrasi pemasok, bukan ketergantungan bersih setelah produksi domestik. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ImporKomoditasStrategisRecord(BaseModel):
    period: int | None = Field(default=None, alias="period", description="Tahun perdagangan.")
    reportercode: int | None = Field(default=None, alias="reporterCode", description="Kode negara pelapor. 360 = Indonesia.")
    flowcode: str | None = Field(default=None, alias="flowCode", description="X = ekspor; M = impor.")
    partnercode: int | None = Field(default=None, alias="partnerCode", description="Kode negara mitra dalam hasil API.")
    partner_name: str | None = Field(default=None, alias="partner_name", description="Label mitra dipetakan dari kode UN M49; bukan field terisi API preview.")
    cmdcode: str | None = Field(default=None, alias="cmdCode", description="TOTAL = semua barang; 10 = serealia; 27 = bahan bakar mineral; 72 = besi/baja; 85 = mesin/peralatan listrik.")
    primaryvalue: float | None = Field(default=None, alias="primaryValue", description="Nilai utama perdagangan dari API.")
    isreported: bool | None = Field(default=None, alias="isReported", description="Flag data dilaporkan langsung, dipertahankan dari sumber.")
    isaggregate: bool | None = Field(default=None, alias="isAggregate", description="Flag agregasi sumber.")
    totalcommodityvalue: float | None = Field(default=None, alias="totalCommodityValue", description="Total impor Indonesia untuk kelompok HS yang sama (partnerCode=0), sebagai denominator pangsa pemasok.")
    suppliershare: float | None = Field(default=None, alias="supplierShare", description="Nilai impor dari negara pemasok dibagi total impor Indonesia untuk kelompok HS yang sama. Ini indikator konsentrasi pemasok, bukan ketergantungan bersih setelah produksi domestik.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
