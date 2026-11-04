# Data Dictionary: PLN - Statistik PLN 2025 - Table 18 : Jumlah Gangguan Distribusi per 100 kms

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PLN - Statistik PLN 2025 - Table 18 : Jumlah Gangguan Distribusi per 100 kms`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Jumlah Gangguan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=axpUP9&nav=MTVfezA1MzFGMDg2LTNDMkUtNDA3OC05ODkwLTgzQjEwMThFQTBBQ30)
- Target module: `ingestion/usecases/ketahanan_energi/pln/jumlah_gangguan_distribusi_per_100_kms/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| unit_pln | `unit_pln` | string | - | Nama unit PLN, baris agregat "Luar Jawa" dan "Jawa", atau "Indonesia" |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "unit", "sub_unit" (bertanda "-" di sumber), "subtotal_wilayah", atau "total" |
| induk_unit | `induk_unit` | string | - | Nama unit induk untuk baris "sub_unit". Null untuk baris lain |
| kelompok_wilayah | `kelompok_wilayah` | string | - | Kelompok wilayah: "Luar Jawa" atau "Jawa". Null untuk baris total |
| tahun | `tahun` | integer | Tahun | Tahun data (2025) |
| jumlah_gangguan_kali | `jumlah_gangguan_kali` | integer | Kali | Jumlah gangguan distribusi (Number of Interruption). Null jika "-" |
| panjang_jaringan_jtm_kms | `panjang_jaringan_jtm_kms` | number | kms | Panjang jaringan Jaringan Tegangan Menengah (JTM). Null jika "-" |
| jumlah_gangguan_per_100kms | `jumlah_gangguan_per_100kms` | number | Kali/100 kms | Jumlah gangguan per 100 kms jaringan JTM. Null jika "-" |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class JumlahGangguanDistribusiPer100KmsRecord(BaseModel):
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN, baris agregat \"Luar Jawa\" dan \"Jawa\", atau \"Indonesia\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\" (bertanda \"-\" di sumber), \"subtotal_wilayah\", atau \"total\"")
    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\". Null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah: \"Luar Jawa\" atau \"Jawa\". Null untuk baris total")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    jumlah_gangguan_kali: int | None = Field(default=None, alias="jumlah_gangguan_kali", description="Jumlah gangguan distribusi (Number of Interruption). Null jika \"-\"")
    panjang_jaringan_jtm_kms: float | None = Field(default=None, alias="panjang_jaringan_jtm_kms", description="Panjang jaringan Jaringan Tegangan Menengah (JTM). Null jika \"-\"")
    jumlah_gangguan_per_100kms: float | None = Field(default=None, alias="jumlah_gangguan_per_100kms", description="Jumlah gangguan per 100 kms jaringan JTM. Null jika \"-\"")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
