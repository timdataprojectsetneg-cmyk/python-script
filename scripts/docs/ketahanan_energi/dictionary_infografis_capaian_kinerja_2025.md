# Data Dictionary: Infografis Capaian Kinerja 2025

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Infografis Capaian Kinerja 2025`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Migas - Sasaran Penyaluran](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=5Q0XJi&nav=MTVfezMzQjREMTQxLUIyOEUtNDg2RC04RkQ1LTQwRkYzRUYzRjQzM30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/infografis_capaian_kinerja_2025/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Label | `label` | Tipe Data | Satuan | Deskripsi |
| tahun | `tahun` | Integer | Tahun | Tahun data. Capaian kinerja 2025; khusus realisasi anggaran tersedia 2021-2025 |
| kelompok | `kelompok` | String | - | Kelompok indikator sesuai infografis: Realisasi Anggaran, PNBP, Penyaluran JBT dan JBKP, BBM Satu Harga, Infrastruktur Gas Bumi, Pengangkutan dan Niaga Gas Bumi |
| indikator | `indikator` | String | - | Nama indikator dalam kelompok, mis. Anggaran BPH Migas, JBT Minyak Solar, Pipa Transmisi |
| tipe_nilai | `tipe_nilai` | String | - | Jenis nilai: Pagu, Target, Realisasi, Realisasi Kumulatif, Persentase, Penetapan Kuota, Penyaluran |
| nilai | `nilai` | Decimal | Sesuai kolom satuan | Nilai angka indikator (pemisah desimal titik; pemisah ribuan dihilangkan) |
| satuan | `satuan` | String | - | Satuan nilai: Miliar Rupiah, %, Juta Kilo Liter, Lembaga Penyalur, KM, Miliar MSCF |
| Cakupan Wilayah | `cakupan_wilayah` | String | Wilayah | Cakupan agregasi data, dalam sumber ini nasional |
| Periode Verifikasi | `periode_verifikasi` | String | Periode | Periode yang digunakan untuk menghitung realisasi penyaluran |
| Sumber | `sumber` | String | - | Laporan Kinerja BPH Migas Tahun 2025 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class InfografisCapaianKinerja2025Record(BaseModel):
    label: str | None = Field(default=None, alias="Label", description="Deskripsi")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data. Capaian kinerja 2025; khusus realisasi anggaran tersedia 2021-2025")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Kelompok indikator sesuai infografis: Realisasi Anggaran, PNBP, Penyaluran JBT dan JBKP, BBM Satu Harga, Infrastruktur Gas Bumi, Pengangkutan dan Niaga Gas Bumi")
    indikator: str | None = Field(default=None, alias="indikator", description="Nama indikator dalam kelompok, mis. Anggaran BPH Migas, JBT Minyak Solar, Pipa Transmisi")
    tipe_nilai: str | None = Field(default=None, alias="tipe_nilai", description="Jenis nilai: Pagu, Target, Realisasi, Realisasi Kumulatif, Persentase, Penetapan Kuota, Penyaluran")
    nilai: float | None = Field(default=None, alias="nilai", description="Nilai angka indikator (pemisah desimal titik; pemisah ribuan dihilangkan)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai: Miliar Rupiah, %, Juta Kilo Liter, Lembaga Penyalur, KM, Miliar MSCF")
    cakupan_wilayah: str | None = Field(default=None, alias="Cakupan Wilayah", description="Cakupan agregasi data, dalam sumber ini nasional")
    periode_verifikasi: str | None = Field(default=None, alias="Periode Verifikasi", description="Periode yang digunakan untuk menghitung realisasi penyaluran")
    sumber: str | None = Field(default=None, alias="Sumber", description="Laporan Kinerja BPH Migas Tahun 2025")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
