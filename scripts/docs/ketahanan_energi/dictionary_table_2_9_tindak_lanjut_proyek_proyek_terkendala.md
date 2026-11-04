# Data Dictionary: Table 2.9 : Tindak Lanjut Proyek-Proyek Terkendala

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Table 2.9 : Tindak Lanjut Proyek-Proyek Terkendala`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Status Proyek yang terkendala](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=OdPBP2&nav=MTVfe0JGRDYxQzNBLTEwQzItNDIwNC1CRDUyLUI1RDkxNTc3QTJFNn0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/table_2_9_tindak_lanjut_proyek_proyek_terkendala/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| no | `no` | integer | - | Nomor urut proyek |
| status_proyek | `status_proyek` | string | - | Kelompok proyek di sumber: "Selesai" (no 1-17) atau "Dilanjutkan" (no 18-34) |
| pembangkit | `pembangkit` | string | - | Nama pembangkit terkendala |
| kapasitas | `kapasitas` | string | MW | Kapasitas dalam format jumlah unit x MW per unit (misalnya "2x7"), atau MW tunggal (misalnya "30") |
| pengembang | `pengembang` | string | - | Pengembang proyek: PLN atau IPP |
| keterangan_dilanjutkan | `keterangan_dilanjutkan` | string | - | Bernilai "Dilanjutkan" jika proyek dilanjutkan. Null jika kosong di sumber |
| keterangan_diganti | `keterangan_diganti` | string | - | Bentuk penggantian proyek (GI, PLTMG, PLTD, MPP, "Relokasi MPP", "Relokasi Sorong***", dll.). Null jika kosong di sumber |
| rencana_cod | `rencana_cod` | string | - | Rencana COD: "Operasi" untuk yang sudah beroperasi, tahun (misalnya "2033"), atau keterangan bertahap (misalnya "2025 (14 MW)/2026 (14 MW)") |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Table29TindakLanjutProyekProyekTerkendalaRecord(BaseModel):
    no: int | None = Field(default=None, alias="no", description="Nomor urut proyek")
    status_proyek: str | None = Field(default=None, alias="status_proyek", description="Kelompok proyek di sumber: \"Selesai\" (no 1-17) atau \"Dilanjutkan\" (no 18-34)")
    pembangkit: str | None = Field(default=None, alias="pembangkit", description="Nama pembangkit terkendala")
    kapasitas: str | None = Field(default=None, alias="kapasitas", description="Kapasitas dalam format jumlah unit x MW per unit (misalnya \"2x7\"), atau MW tunggal (misalnya \"30\")")
    pengembang: str | None = Field(default=None, alias="pengembang", description="Pengembang proyek: PLN atau IPP")
    keterangan_dilanjutkan: str | None = Field(default=None, alias="keterangan_dilanjutkan", description="Bernilai \"Dilanjutkan\" jika proyek dilanjutkan. Null jika kosong di sumber")
    keterangan_diganti: str | None = Field(default=None, alias="keterangan_diganti", description="Bentuk penggantian proyek (GI, PLTMG, PLTD, MPP, \"Relokasi MPP\", \"Relokasi Sorong***\", dll.). Null jika kosong di sumber")
    rencana_cod: str | None = Field(default=None, alias="rencana_cod", description="Rencana COD: \"Operasi\" untuk yang sudah beroperasi, tahun (misalnya \"2033\"), atau keterangan bertahap (misalnya \"2025 (14 MW)/2026 (14 MW)\")")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
