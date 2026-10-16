# Data Dictionary: Kemnaker Perusahaan Skala Upah Table 2

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kemnaker Perusahaan Skala Upah Table 2`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Kemnaker Perusahaan Skala Upah Table 2](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=VbDfbE&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xODAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kemnaker_perusahaan_skala_upah_table_2/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi ("Jumlah" = nasional). |
| A | `a` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori A – Pertanian, Kehutanan dan Perikanan. |
| B | `b` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori B – Pertambangan dan Penggalian. |
| C | `c` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori C – Industri Pengolahan. |
| D | `d` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori D – Pengadaan Listrik dan Gas. |
| E | `e` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori E – Pengadaan Air, Pengelolaan Sampah, Limbah, dan Daur Ulang. |
| F | `f` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori F – Konstruksi. |
| G | `g` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori G – Perdagangan Besar dan Eceran; Reparasi dan Perawatan Mobil dan Sepeda Motor. |
| H | `h` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori H – Transportasi dan Pergudangan. |
| I | `i` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori I – Penyediaan Akomodasi dan Makan Minum. |
| J | `j` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori J – Informasi dan Komunikasi. |
| K | `k` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori K – Jasa Keuangan dan Asuransi. |
| L | `l` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori L – Real Estat. |
| M_N | `m_n` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori M,N – Jasa Perusahaan. |
| O | `o` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori O – Administrasi Pemerintahan, Pertahanan dan Jaminan Sosial Wajib. |
| P | `p` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori P – Jasa Pendidikan. |
| Q | `q` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori Q – Jasa Kesehatan dan Kegiatan Sosial. |
| R_S_T_U | `r_s_t_u` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori R,S,T,U – Jasa Lainnya. |
| Tidak_Teridentifikasi | `tidak_teridentifikasi` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah yang lapangan usahanya belum teridentifikasi. |
| Jumlah | `jumlah` | Integer | Perusahaan | Total seluruh lapangan usaha. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KemnakerPerusahaanSkalaUpahTable2Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    a: int | None = Field(default=None, alias="A", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori A – Pertanian, Kehutanan dan Perikanan.")
    b: int | None = Field(default=None, alias="B", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori B – Pertambangan dan Penggalian.")
    c: int | None = Field(default=None, alias="C", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori C – Industri Pengolahan.")
    d: int | None = Field(default=None, alias="D", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori D – Pengadaan Listrik dan Gas.")
    e: int | None = Field(default=None, alias="E", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori E – Pengadaan Air, Pengelolaan Sampah, Limbah, dan Daur Ulang.")
    f: int | None = Field(default=None, alias="F", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori F – Konstruksi.")
    g: int | None = Field(default=None, alias="G", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori G – Perdagangan Besar dan Eceran; Reparasi dan Perawatan Mobil dan Sepeda Motor.")
    h: int | None = Field(default=None, alias="H", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori H – Transportasi dan Pergudangan.")
    i: int | None = Field(default=None, alias="I", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori I – Penyediaan Akomodasi dan Makan Minum.")
    j: int | None = Field(default=None, alias="J", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori J – Informasi dan Komunikasi.")
    k: int | None = Field(default=None, alias="K", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori K – Jasa Keuangan dan Asuransi.")
    l: int | None = Field(default=None, alias="L", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori L – Real Estat.")
    m_n: int | None = Field(default=None, alias="M_N", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori M,N – Jasa Perusahaan.")
    o: int | None = Field(default=None, alias="O", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori O – Administrasi Pemerintahan, Pertahanan dan Jaminan Sosial Wajib.")
    p: int | None = Field(default=None, alias="P", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori P – Jasa Pendidikan.")
    q: int | None = Field(default=None, alias="Q", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori Q – Jasa Kesehatan dan Kegiatan Sosial.")
    r_s_t_u: int | None = Field(default=None, alias="R_S_T_U", description="Perusahaan yang melaporkan Struktur Skala Upah lapangan usaha kategori R,S,T,U – Jasa Lainnya.")
    tidak_teridentifikasi: int | None = Field(default=None, alias="Tidak_Teridentifikasi", description="Perusahaan yang melaporkan Struktur Skala Upah yang lapangan usahanya belum teridentifikasi.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh lapangan usaha.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
