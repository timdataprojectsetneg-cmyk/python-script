# Data Dictionary: Keputusan Menteri Energi dan Sumber Daya Mineral Nomor 439.K/MG.01/MEM.M/2023 tentang Formula Harga Dasar Jenis Bahan Bakar Minyak Tertentu

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Keputusan Menteri Energi dan Sumber Daya Mineral Nomor 439.K/MG.01/MEM.M/2023 tentang Formula Harga Dasar Jenis Bahan Bakar Minyak Tertentu`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Regulatory / event-based
- Eligible: `True`
- Data Dictionary file: [ESDM - Formula Harga Dasar BBM](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=qU96EI&nav=MTVfe0Q0MEExQ0UyLUU0N0QtNDI4MS1BRDBELTEzM0JFQjdFOTk5QX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energi_dan_sumber_daya_mineral_nomor_439_k_mg_01_mem_m_2023/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jenis BBM | `jenis_bbm` | Text | - | Jenis BBM Tertentu yang memiliki formula harga dasar. |
| Komponen Harga Dasar | `komponen_harga_dasar` | Text | - | Harga dasar terdiri atas biaya perolehan, biaya distribusi, biaya penyimpanan, dan margin. |
| Persentase HIP | `persentase_hip` | Decimal | % | Bobot Harga Indeks Pasar dalam formula harga dasar. |
| Konstanta Formula | `konstanta_formula` | Decimal | Rp/liter | Nilai rupiah per liter yang ditambahkan ke komponen HIP dalam formula. |
| Formula Harga Dasar | `formula_harga_dasar` | Text | - | Rumus resmi harga dasar untuk masing-masing jenis BBM Tertentu. |
| Basis Penyediaan | `basis_penyediaan` | Text | - | Biaya perolehan terkait penyediaan BBM dari produksi kilang dalam negeri dan/atau impor sampai terminal/depot, berdasarkan penjelasan Ditjen Migas. |
| Periode Harga Indeks | `periode_harga_indeks` | Text | - | Perhitungan harga indeks pasar menggunakan periode pengamatan yang ditetapkan dalam ketentuan formula. |
| Unit Konversi | `unit_konversi` | Integer | liter/barrel | 1 barrel setara 159 liter sebagaimana digunakan dalam formula harga dasar BBM. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EnergiDanSumberDayaMineralNomor439KMg01MemM2023Record(BaseModel):
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis BBM Tertentu yang memiliki formula harga dasar.")
    komponen_harga_dasar: str | None = Field(default=None, alias="Komponen Harga Dasar", description="Harga dasar terdiri atas biaya perolehan, biaya distribusi, biaya penyimpanan, dan margin.")
    persentase_hip: float | None = Field(default=None, alias="Persentase HIP", description="Bobot Harga Indeks Pasar dalam formula harga dasar.")
    konstanta_formula: float | None = Field(default=None, alias="Konstanta Formula", description="Nilai rupiah per liter yang ditambahkan ke komponen HIP dalam formula.")
    formula_harga_dasar: str | None = Field(default=None, alias="Formula Harga Dasar", description="Rumus resmi harga dasar untuk masing-masing jenis BBM Tertentu.")
    basis_penyediaan: str | None = Field(default=None, alias="Basis Penyediaan", description="Biaya perolehan terkait penyediaan BBM dari produksi kilang dalam negeri dan/atau impor sampai terminal/depot, berdasarkan penjelasan Ditjen Migas.")
    periode_harga_indeks: str | None = Field(default=None, alias="Periode Harga Indeks", description="Perhitungan harga indeks pasar menggunakan periode pengamatan yang ditetapkan dalam ketentuan formula.")
    unit_konversi: int | None = Field(default=None, alias="Unit Konversi", description="1 barrel setara 159 liter sebagaimana digunakan dalam formula harga dasar BBM.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
