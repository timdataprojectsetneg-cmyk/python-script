# Data Dictionary: Tarif Listrik per Golongan - PLN Tariff Adjustment

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tarif Listrik per Golongan - PLN Tariff Adjustment`
- Publisher: pln
- Data access: `pdf`
- Update frequency: Quarterly
- Eligible: `True`
- Data Dictionary file: [PLN - Tariff Adjustment](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=wmpAJK&nav=MTVfe0MwOTQwRTIxLUM1RTYtNENFRS1CRjY5LUVBMjQyNjY4OEU0Rn0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/tarif_listrik_per_golongan_pln_tariff_adjustment/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode Berlaku | `periode_berlaku` | Text | periode | Periode tarif yang berlaku. |
| Golongan Pelanggan | `golongan_pelanggan` | Text | kode golongan | Kode golongan tarif pelanggan PLN. |
| Daya | `daya` | Text | VA atau kVA | Rentang daya yang termasuk dalam golongan. |
| Tegangan | `tegangan` | Text | TR, TM, TT | Tingkat tegangan pelayanan. |
| Tarif Listrik | `tarif_listrik` | Decimal | Rp/kWh | Tarif tenaga listrik untuk golongan pelanggan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class TarifListrikPerGolonganPlnTariffAdjustmentRecord(BaseModel):
    periode_berlaku: str | None = Field(default=None, alias="Periode Berlaku", description="Periode tarif yang berlaku.")
    golongan_pelanggan: str | None = Field(default=None, alias="Golongan Pelanggan", description="Kode golongan tarif pelanggan PLN.")
    daya: str | None = Field(default=None, alias="Daya", description="Rentang daya yang termasuk dalam golongan.")
    tegangan: str | None = Field(default=None, alias="Tegangan", description="Tingkat tegangan pelayanan.")
    tarif_listrik: float | None = Field(default=None, alias="Tarif Listrik", description="Tarif tenaga listrik untuk golongan pelanggan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
