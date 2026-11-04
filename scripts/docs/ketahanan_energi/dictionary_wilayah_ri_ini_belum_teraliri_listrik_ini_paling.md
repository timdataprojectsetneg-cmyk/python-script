# Data Dictionary: CNBC - Wilayah RI Ini Belum Teraliri Listrik, Ini Paling BanyaK

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `CNBC - Wilayah RI Ini Belum Teraliri Listrik, Ini Paling BanyaK`
- Publisher: cnbc
- Data access: `scraper`
- Update frequency: Rilis Berita
- Eligible: `True`
- Data Dictionary file: [Daerah yang belum dialiri listrik](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=rvUZOf&nav=MTVfe0I4OEUwODc2LTNCM0YtNEYxOC04M0JBLUJGM0Y3NUEwMjA4RH0)
- Target module: `ingestion/usecases/ketahanan_energi/cnbc/wilayah_ri_ini_belum_teraliri_listrik_ini_paling/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi (38 provinsi) |
| Periode | `periode` | String | - | Triwulan I 2026 |
| RD_PLN | `rd_pln` | Numeric | % | Rasio desa berlistrik PLN, yaitu persentase desa yang dialiri listrik PLN |
| RD_NAS | `rd_nas` | Numeric | % | Rasio desa berlistrik nasional, yaitu persentase desa berlistrik dari PLN dan sumber non-PLN |
| Kategori_RD_PLN | `kategori_rd_pln` | String | - | Kelas pada legenda peta: 100, 90-99, 70-89, 40-69, atau <40 |
| Sample Data | `sample_data` | - | - | - |
| Provinsi | `provinsi` | Periode | RD_PLN | RD_NAS |
| Aceh | `aceh` | TW I 2026 | 100 | 100 |
| Sumatera Utara | `sumatera_utara` | TW I 2026 | 99.28 | 100 |
| Sumatera Barat | `sumatera_barat` | TW I 2026 | 100 | 100 |
| Riau | `riau` | TW I 2026 | 100 | 100 |
| Kepulauan Riau | `kepulauan_riau` | TW I 2026 | 99.761 | 100 |
| Jambi | `jambi` | TW I 2026 | 99.874 | 100 |
| Sumatera Selatan | `sumatera_selatan` | TW I 2026 | 99.356 | 100 |
| Kepulauan Bangka Belitung | `kepulauan_bangka_belitung` | TW I 2026 | 100 | 100 |
| Bengkulu | `bengkulu` | TW I 2026 | 100 | 100 |
| Lampung | `lampung` | TW I 2026 | 99.774 | 100 |
| Banten | `banten` | TW I 2026 | 99.936 | 100 |
| DKI Jakarta | `dki_jakarta` | TW I 2026 | 100 | 100 |
| Jawa Barat | `jawa_barat` | TW I 2026 | 100 | 100 |
| DI Yogyakarta | `di_yogyakarta` | TW I 2026 | 100 | 100 |
| Jawa Tengah | `jawa_tengah` | TW I 2026 | 100 | 100 |
| Jawa Timur | `jawa_timur` | TW I 2026 | 99.965 | 100 |
| Bali | `bali` | TW I 2026 | 100 | 100 |
| Nusa Tenggara Barat | `nusa_tenggara_barat` | TW I 2026 | 99.571 | 100 |
| Nusa Tenggara Timur | `nusa_tenggara_timur` | TW I 2026 | 96.804 | 100 |
| Kalimantan Barat | `kalimantan_barat` | TW I 2026 | 85.874 | 100 |
| Kalimantan Tengah | `kalimantan_tengah` | TW I 2026 | 83.832 | 100 |
| Kalimantan Selatan | `kalimantan_selatan` | TW I 2026 | 99.454 | 100 |
| Kalimantan Timur | `kalimantan_timur` | TW I 2026 | 92.967 | 100 |
| Kalimantan Utara | `kalimantan_utara` | TW I 2026 | 81.95 | 100 |
| Sulawesi Utara | `sulawesi_utara` | TW I 2026 | 99.565 | 100 |
| Gorontalo | `gorontalo` | TW I 2026 | 99.863 | 100 |
| Sulawesi Tengah | `sulawesi_tengah` | TW I 2026 | 95.935 | 100 |
| Sulawesi Barat | `sulawesi_barat` | TW I 2026 | 97.222 | 100 |
| Sulawesi Selatan | `sulawesi_selatan` | TW I 2026 | 98.987 | 100 |
| Sulawesi Tenggara | `sulawesi_tenggara` | TW I 2026 | 97.899 | 100 |
| Maluku Utara | `maluku_utara` | TW I 2026 | 94.262 | 100 |
| Maluku | `maluku` | TW I 2026 | 90.688 | 100 |
| Papua Barat Daya | `papua_barat_daya` | TW I 2026 | 66.338 | 100 |
| Papua Barat | `papua_barat` | TW I 2026 | 70.51 | 100 |
| Papua | `papua` | TW I 2026 | 82.883 | 100 |
| Papua Tengah | `papua_tengah` | TW I 2026 | 26.821 | 100 |
| Papua Pegunungan | `papua_pegunungan` | TW I 2026 | 21.165 | 100 |
| Papua Selatan | `papua_selatan` | TW I 2026 | 56.957 | 100 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class WilayahRiIniBelumTeraliriListrikIniPalingRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (38 provinsi)")
    periode: str | None = Field(default=None, alias="Periode", description="Triwulan I 2026")
    rd_pln: str | None = Field(default=None, alias="RD_PLN", description="Rasio desa berlistrik PLN, yaitu persentase desa yang dialiri listrik PLN")
    rd_nas: str | None = Field(default=None, alias="RD_NAS", description="Rasio desa berlistrik nasional, yaitu persentase desa berlistrik dari PLN dan sumber non-PLN")
    kategori_rd_pln: str | None = Field(default=None, alias="Kategori_RD_PLN", description="Kelas pada legenda peta: 100, 90-99, 70-89, 40-69, atau <40")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="RD_NAS")
    aceh: str | None = Field(default=None, alias="Aceh")
    sumatera_utara: str | None = Field(default=None, alias="Sumatera Utara")
    sumatera_barat: str | None = Field(default=None, alias="Sumatera Barat")
    riau: str | None = Field(default=None, alias="Riau")
    kepulauan_riau: str | None = Field(default=None, alias="Kepulauan Riau")
    jambi: str | None = Field(default=None, alias="Jambi")
    sumatera_selatan: str | None = Field(default=None, alias="Sumatera Selatan")
    kepulauan_bangka_belitung: str | None = Field(default=None, alias="Kepulauan Bangka Belitung")
    bengkulu: str | None = Field(default=None, alias="Bengkulu")
    lampung: str | None = Field(default=None, alias="Lampung")
    banten: str | None = Field(default=None, alias="Banten")
    dki_jakarta: str | None = Field(default=None, alias="DKI Jakarta")
    jawa_barat: str | None = Field(default=None, alias="Jawa Barat")
    di_yogyakarta: str | None = Field(default=None, alias="DI Yogyakarta")
    jawa_tengah: str | None = Field(default=None, alias="Jawa Tengah")
    jawa_timur: str | None = Field(default=None, alias="Jawa Timur")
    bali: str | None = Field(default=None, alias="Bali")
    nusa_tenggara_barat: str | None = Field(default=None, alias="Nusa Tenggara Barat")
    nusa_tenggara_timur: str | None = Field(default=None, alias="Nusa Tenggara Timur")
    kalimantan_barat: str | None = Field(default=None, alias="Kalimantan Barat")
    kalimantan_tengah: str | None = Field(default=None, alias="Kalimantan Tengah")
    kalimantan_selatan: str | None = Field(default=None, alias="Kalimantan Selatan")
    kalimantan_timur: str | None = Field(default=None, alias="Kalimantan Timur")
    kalimantan_utara: str | None = Field(default=None, alias="Kalimantan Utara")
    sulawesi_utara: str | None = Field(default=None, alias="Sulawesi Utara")
    gorontalo: str | None = Field(default=None, alias="Gorontalo")
    sulawesi_tengah: str | None = Field(default=None, alias="Sulawesi Tengah")
    sulawesi_barat: str | None = Field(default=None, alias="Sulawesi Barat")
    sulawesi_selatan: str | None = Field(default=None, alias="Sulawesi Selatan")
    sulawesi_tenggara: str | None = Field(default=None, alias="Sulawesi Tenggara")
    maluku_utara: str | None = Field(default=None, alias="Maluku Utara")
    maluku: str | None = Field(default=None, alias="Maluku")
    papua_barat_daya: str | None = Field(default=None, alias="Papua Barat Daya")
    papua_barat: str | None = Field(default=None, alias="Papua Barat")
    papua: str | None = Field(default=None, alias="Papua")
    papua_tengah: str | None = Field(default=None, alias="Papua Tengah")
    papua_pegunungan: str | None = Field(default=None, alias="Papua Pegunungan")
    papua_selatan: str | None = Field(default=None, alias="Papua Selatan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
