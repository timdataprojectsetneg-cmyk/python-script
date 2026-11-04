# Data Dictionary: Gambar 27 Peta Ruas Pipa Cirebon–Semarang

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Gambar 27 Peta Ruas Pipa Cirebon–Semarang`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Peta Ruas Pipa](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=rd8eh6&nav=MTVfezE2OTIzODRGLUNDMkItNEI1My04NkEyLUVGQzUzMTdBNTRCRX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/gambar_27_peta_ruas_pipa_cirebon_semarang/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| nama_ruas | `nama_ruas` | Text | - | Nama ruas pipa pada header peta: Cirebon–Kandang Haur Timur, Pemalang–Cirebon, Batang–Pemalang |
| panjang_ruas | `panjang_ruas` | Numeric (Decimal) | km | Panjang perkiraan ruas, tertulis dengan tanda ± di peta |
| row_jenis | `row_jenis` | Categorical | - | Jenis jalur hak lintas (ROW) yang dilalui: Jalan Tol, Jalan Nasional, atau Pertagas. Satu ruas bisa punya lebih dari satu jenis |
| row_keterangan | `row_keterangan` | Text | - | Rincian ROW: titik awal–akhir (mis. gate tol) atau badan usaha jalan tol (BUJT) yang terlibat |
| fasilitas_pendukung | `fasilitas_pendukung` | Text | - | Fasilitas yang disebut pada ruas tersebut, mis. kompresor. Kosong bila tidak ada |
| periode_data | `periode_data` | Text | - | Posisi tanggal pelaporan progres, mis. "Hingga Desember 2024" atau "24 Desember 2025" |
| progres_realisasi | `progres_realisasi` | Numeric (Decimal) | % | Progres fisik terealisasi pada periode tersebut |
| progres_rencana | `progres_rencana` | Numeric (Decimal) | % | Progres fisik rencana (s-curve) pada periode yang sama |
| deviasi | `deviasi` | Numeric (Decimal) | poin persen | Kolom turunan (formula): realisasi − rencana. Positif berarti di atas rencana |
| keterangan_status | `keterangan_status` | Text | - | Status pekerjaan yang tertulis pada teks, mis. penanaman pipa selesai dan masuk tahap precommissioning |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Gambar27PetaRuasPipaCirebonSemarangRecord(BaseModel):
    nama_ruas: str | None = Field(default=None, alias="nama_ruas", description="Nama ruas pipa pada header peta: Cirebon–Kandang Haur Timur, Pemalang–Cirebon, Batang–Pemalang")
    panjang_ruas: str | None = Field(default=None, alias="panjang_ruas", description="Panjang perkiraan ruas, tertulis dengan tanda ± di peta")
    row_jenis: str | None = Field(default=None, alias="row_jenis", description="Jenis jalur hak lintas (ROW) yang dilalui: Jalan Tol, Jalan Nasional, atau Pertagas. Satu ruas bisa punya lebih dari satu jenis")
    row_keterangan: str | None = Field(default=None, alias="row_keterangan", description="Rincian ROW: titik awal–akhir (mis. gate tol) atau badan usaha jalan tol (BUJT) yang terlibat")
    fasilitas_pendukung: str | None = Field(default=None, alias="fasilitas_pendukung", description="Fasilitas yang disebut pada ruas tersebut, mis. kompresor. Kosong bila tidak ada")
    periode_data: str | None = Field(default=None, alias="periode_data", description="Posisi tanggal pelaporan progres, mis. \"Hingga Desember 2024\" atau \"24 Desember 2025\"")
    progres_realisasi: str | None = Field(default=None, alias="progres_realisasi", description="Progres fisik terealisasi pada periode tersebut")
    progres_rencana: str | None = Field(default=None, alias="progres_rencana", description="Progres fisik rencana (s-curve) pada periode yang sama")
    deviasi: str | None = Field(default=None, alias="deviasi", description="Kolom turunan (formula): realisasi − rencana. Positif berarti di atas rencana")
    keterangan_status: str | None = Field(default=None, alias="keterangan_status", description="Status pekerjaan yang tertulis pada teks, mis. penanaman pipa selesai dan masuk tahap precommissioning")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
