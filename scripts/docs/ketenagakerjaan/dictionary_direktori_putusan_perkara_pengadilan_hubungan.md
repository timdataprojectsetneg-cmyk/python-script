# Data Dictionary: Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)`
- Publisher: MA RI
- Data access: `scraper`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=64rngc&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wMzAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/ma_ri/direktori_putusan_perkara_pengadilan_hubungan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nomor_Perkara | `nomor_perkara` | String | - | Nomor putusan, format <no>/Pdt.Sus-PHI/<tahun>/PN <kode>. |
| Wilayah Pengadilan | `wilayah_pengadilan` | String | - | Pengadilan yang memutus (PN tingkat pertama / Mahkamah Agung). |
| Tanggal_Register | `tanggal_register` | Date | DD-MM-YYYY | Tanggal perkara didaftarkan. |
| Tanggal_Putus | `tanggal_putus` | Date | DD-MM-YYYY | Tanggal putusan. |
| Tanggal_Upload | `tanggal_upload` | Date | DD-MM-YYYY | Tanggal putusan diunggah ke Direktori Putusan. |
| Lama penyelesaian hari kerja | `lama_penyelesaian_hari_kerja` | integer | - | Durasi penanganan perkara dari registrasi hingga putusan (maksimal 50 hari kerja berdasarkan Pasal 103 UU No. 2/2004) |
| status penyelesaian | `status_penyelesaian` | String | - | Amar putusan sengketa (Kabul Seluruhnya, Kabul Sebagian, Ditolak, Dicabut, Akta Perdamaian/Dading) |
| Penggugat | `penggugat` | String | - | Pihak penggugat (pekerja/serikat pekerja/perusahaan). |
| Tergugat | `tergugat` | String | - | Pihak tergugat (perusahaan/pekerja). |
| Sektor industri | `sektor_industri` | string | - | Sektor lapangan usaha entitas tergugat (Tekstil & Garmen, Manufaktur Otomotif, Logistik & Pergudangan, Perdagangan Ritel, Jasa Perhotelan, dsb.) |
| ringkasan_pokok_sengketa | `ringkasan_pokok_sengketa` | text | - | Ringkasan objek tuntutan perselisihan (penuntutan uang pesangon PHK efisiensi, selisih upah minimum, tunjangan hak normatif) |
| provinsi | `provinsi` | string | - | Nama provinsi yurisdiksi perselisihan hubungan industrial |
| Putusan | `putusan` | Json | URL | Tautan halaman detail putusan (lihat sheet MA Putusan Perkara PHI (2)). |
| link_file | `link_file` | string | - | link file dari web |
| minio_file | `minio_file` | string | - | file pdf di minio-sitroom.setneg.go.id |

### JSON field: `putusan` (Putusan)

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nomor_Perkara | `nomor_perkara` | String | - | Nomor putusan. |
| Tingkat_Proses | `tingkat_proses` | String | - | Tingkat proses: Pertama / Banding / Kasasi / Peninjauan Kembali. |
| Klasifikasi | `klasifikasi` | String | - | Kategori perkara (Perdata Khusus PHI). |
| Kata_Kunci | `kata_kunci` | String | - | Kata kunci perkara dari pengadilan. |
| Tahun | `tahun` | Integer | - | Tahun perkara (pernah teramati anomali, mis. 2029). |
| Tanggal_Register | `tanggal_register` | Date | - | Tanggal perkara didaftarkan. |
| Lembaga_Peradilan | `lembaga_peradilan` | String | - | Nama pengadilan. |
| Jenis_Lembaga | `jenis_lembaga` | String | - | Jenis lembaga peradilan (PN/MA). |
| Hakim_Ketua | `hakim_ketua` | String | - | Nama hakim ketua. |
| Hakim_Anggota | `hakim_anggota` | String | - | Nama hakim anggota (dipisah koma). |
| Panitera | `panitera` | String | - | Nama panitera pengganti. |
| Amar | `amar` | String | - | Kategori amar (sering generik "Lain-lain"). |
| Amar_Lainnya | `amar_lainnya` | String | - | Keterangan amar tambahan (mis. DICABUT, NO). |
| Catatan_Amar | `catatan_amar` | Text | - | Narasi lengkap amar putusan; dasar penentuan status penyelesaian. |
| Tanggal_Musyawarah | `tanggal_musyawarah` | Date | - | Tanggal musyawarah majelis hakim. |
| Tanggal_Dibacakan | `tanggal_dibacakan` | Date | - | Tanggal putusan dibacakan. |
| Kaidah | `kaidah` | String | - | Kaidah hukum (sering kosong). |
| Abstrak | `abstrak` | Text | - | Abstrak perkara (sering kosong). |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class Putusan(BaseModel):
    nomor_perkara: str | None = Field(default=None, alias="Nomor_Perkara", description="Nomor putusan.")
    tingkat_proses: str | None = Field(default=None, alias="Tingkat_Proses", description="Tingkat proses: Pertama / Banding / Kasasi / Peninjauan Kembali.")
    klasifikasi: str | None = Field(default=None, alias="Klasifikasi", description="Kategori perkara (Perdata Khusus PHI).")
    kata_kunci: str | None = Field(default=None, alias="Kata_Kunci", description="Kata kunci perkara dari pengadilan.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun perkara (pernah teramati anomali, mis. 2029).")
    tanggal_register: date | None = Field(default=None, alias="Tanggal_Register", description="Tanggal perkara didaftarkan.")
    lembaga_peradilan: str | None = Field(default=None, alias="Lembaga_Peradilan", description="Nama pengadilan.")
    jenis_lembaga: str | None = Field(default=None, alias="Jenis_Lembaga", description="Jenis lembaga peradilan (PN/MA).")
    hakim_ketua: str | None = Field(default=None, alias="Hakim_Ketua", description="Nama hakim ketua.")
    hakim_anggota: str | None = Field(default=None, alias="Hakim_Anggota", description="Nama hakim anggota (dipisah koma).")
    panitera: str | None = Field(default=None, alias="Panitera", description="Nama panitera pengganti.")
    amar: str | None = Field(default=None, alias="Amar", description="Kategori amar (sering generik \"Lain-lain\").")
    amar_lainnya: str | None = Field(default=None, alias="Amar_Lainnya", description="Keterangan amar tambahan (mis. DICABUT, NO).")
    catatan_amar: str | None = Field(default=None, alias="Catatan_Amar", description="Narasi lengkap amar putusan; dasar penentuan status penyelesaian.")
    tanggal_musyawarah: date | None = Field(default=None, alias="Tanggal_Musyawarah", description="Tanggal musyawarah majelis hakim.")
    tanggal_dibacakan: date | None = Field(default=None, alias="Tanggal_Dibacakan", description="Tanggal putusan dibacakan.")
    kaidah: str | None = Field(default=None, alias="Kaidah", description="Kaidah hukum (sering kosong).")
    abstrak: str | None = Field(default=None, alias="Abstrak", description="Abstrak perkara (sering kosong).")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class DirektoriPutusanPerkaraPengadilanHubunganRecord(BaseModel):
    nomor_perkara: str | None = Field(default=None, alias="Nomor_Perkara", description="Nomor putusan, format <no>/Pdt.Sus-PHI/<tahun>/PN <kode>.")
    wilayah_pengadilan: str | None = Field(default=None, alias="Wilayah Pengadilan", description="Pengadilan yang memutus (PN tingkat pertama / Mahkamah Agung).")
    tanggal_register: date | None = Field(default=None, alias="Tanggal_Register", description="Tanggal perkara didaftarkan.")
    tanggal_putus: date | None = Field(default=None, alias="Tanggal_Putus", description="Tanggal putusan.")
    tanggal_upload: date | None = Field(default=None, alias="Tanggal_Upload", description="Tanggal putusan diunggah ke Direktori Putusan.")
    lama_penyelesaian_hari_kerja: int | None = Field(default=None, alias="Lama penyelesaian hari kerja", description="Durasi penanganan perkara dari registrasi hingga putusan (maksimal 50 hari kerja berdasarkan Pasal 103 UU No. 2/2004)")
    status_penyelesaian: str | None = Field(default=None, alias="status penyelesaian", description="Amar putusan sengketa (Kabul Seluruhnya, Kabul Sebagian, Ditolak, Dicabut, Akta Perdamaian/Dading)")
    penggugat: str | None = Field(default=None, alias="Penggugat", description="Pihak penggugat (pekerja/serikat pekerja/perusahaan).")
    tergugat: str | None = Field(default=None, alias="Tergugat", description="Pihak tergugat (perusahaan/pekerja).")
    sektor_industri: str | None = Field(default=None, alias="Sektor industri", description="Sektor lapangan usaha entitas tergugat (Tekstil & Garmen, Manufaktur Otomotif, Logistik & Pergudangan, Perdagangan Ritel, Jasa Perhotelan, dsb.)")
    ringkasan_pokok_sengketa: str | None = Field(default=None, alias="ringkasan_pokok_sengketa", description="Ringkasan objek tuntutan perselisihan (penuntutan uang pesangon PHK efisiensi, selisih upah minimum, tunjangan hak normatif)")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi yurisdiksi perselisihan hubungan industrial")
    putusan: Putusan | None = Field(default=None, alias="Putusan", description="Tautan halaman detail putusan (lihat sheet MA Putusan Perkara PHI (2)).")
    link_file: str | None = Field(default=None, alias="link_file", description="link file dari web")
    minio_file: str | None = Field(default=None, alias="minio_file", description="file pdf di minio-sitroom.setneg.go.id")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
