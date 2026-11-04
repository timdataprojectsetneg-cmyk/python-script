# Data Dictionary: Artikel BPH Migas - BPH Migas Pastikan Konsumen Pengguna BBM Subsidi dan Kompensasi lewat Teknologi Informasi

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Artikel BPH Migas - BPH Migas Pastikan Konsumen Pengguna BBM Subsidi dan Kompensasi lewat Teknologi Informasi`
- Publisher: bphmigas
- Data access: `scraper`
- Update frequency: Berkala
- Eligible: `True`
- Data Dictionary file: [BPH Migas - XStar dan penyaluran tepat sasaran](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=oc9Eir&nav=MTVfezMzQjREMTQxLUIyOEUtNDg2RC04RkQ1LTQwRkYzRUYzRjQzM30)
- Target module: `ingestion/usecases/ketahanan_energi/bphmigas/bph_migas_pastikan_konsumen_pengguna_bbm_subsidi_dan_kompensasi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jenis BBM | `jenis_bbm` | Text | produk | Jenis BBM yang menjadi objek surat rekomendasi. |
| Jenis Konsumen Pengguna | `jenis_konsumen_pengguna` | Text | kategori pengguna | Kelompok pengguna yang dapat memperoleh rekomendasi. |
| Estimasi Kebutuhan | `estimasi_kebutuhan` | Decimal | volume sesuai satuan | Perkiraan kebutuhan BBM yang diajukan. |
| Lokasi | `lokasi` | Text | wilayah | Lokasi pengguna atau penerbit rekomendasi. |
| Periode | `periode` | Text | periode | Masa berlaku rekomendasi atau periode kebutuhan. |
| Status Surat Rekomendasi | `status_surat_rekomendasi` | Text | status | Status proses atau dokumen rekomendasi. |
| Mekanisme | `mekanisme` | Text | mekanisme | Pengelolaan rekomendasi melalui XSTAR. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BphMigasPastikanKonsumenPenggunaBbmSubsidiDanKompensasiRecord(BaseModel):
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis BBM yang menjadi objek surat rekomendasi.")
    jenis_konsumen_pengguna: str | None = Field(default=None, alias="Jenis Konsumen Pengguna", description="Kelompok pengguna yang dapat memperoleh rekomendasi.")
    estimasi_kebutuhan: float | None = Field(default=None, alias="Estimasi Kebutuhan", description="Perkiraan kebutuhan BBM yang diajukan.")
    lokasi: str | None = Field(default=None, alias="Lokasi", description="Lokasi pengguna atau penerbit rekomendasi.")
    periode: str | None = Field(default=None, alias="Periode", description="Masa berlaku rekomendasi atau periode kebutuhan.")
    status_surat_rekomendasi: str | None = Field(default=None, alias="Status Surat Rekomendasi", description="Status proses atau dokumen rekomendasi.")
    mekanisme: str | None = Field(default=None, alias="Mekanisme", description="Pengelolaan rekomendasi melalui XSTAR.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
