# Data Dictionary: Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)`
- Publisher: MA RI
- Data access: `scraper`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=GQWeHe&nav=MTVfezlBMUQyMjZELTM5N0EtNDkyNC1CQTVGLTc3NzE4QjQ3QUZCN30)
- Target module: `ingestion/usecases/ketenagakerjaan/ma_ri/direktori_putusan_perkara_pengadilan_hubungan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| nomor_perkara | `nomor_perkara` | String | - | Nomor registrasi resmi perkara sengketa pada Pengadilan Hubungan Industrial (contoh: 12/Pdt.Sus-PHI/2024/PN Jkt.Pst) |
| jenis_perselisihan | `jenis_perselisihan` | String | - | Klasifikasi sengketa ketenagakerjaan menurut UU No. 2/2004 (Perselisihan Hak, Perselisihan Kepentingan, Perselisihan PHK, Perselisihan Antar Serikat Pekerja) |
| tanggal_mulai_daftar | `tanggal_mulai_daftar` | Date | YYYY-MM-DD | Tanggal pendaftaran berkas gugatan di kepaniteraan Pengadilan Hubungan Industrial |
| tanggal_selesai_putus | `tanggal_selesai_putus` | Date | YYYY-MM-DD | Tanggal pembacaan putusan sidang oleh majelis hakim PHI |
| lama_penyelesaian_hari_kerja | `lama_penyelesaian_hari_kerja` | Integer | Hari Kerja | Durasi penanganan perkara dari registrasi hingga putusan (maksimal 50 hari kerja berdasarkan Pasal 103 UU No. 2/2004) |
| status_penyelesaian | `status_penyelesaian` | String | - | Amar putusan sengketa (Kabul Seluruhnya, Kabul Sebagian, Ditolak, Dicabut, Akta Perdamaian/Dading) |
| nama_penggugat | `nama_penggugat` | String | - | Identitas pihak penggugat (Pekerja / Karyawan / Serikat Pekerja) |
| nama_perusahaan_tergugat | `nama_perusahaan_tergugat` | String | - | Identitas pihak tergugat / nama badan usaha pemberi kerja (PT, CV, Badan Usaha) |
| sektor_industri | `sektor_industri` | String | - | Sektor lapangan usaha entitas tergugat (Tekstil & Garmen, Manufaktur Otomotif, Logistik & Pergudangan, Perdagangan Ritel, Jasa Perhotelan, dsb.) |
| wilayah_pengadilan | `wilayah_pengadilan` | String | - | Pengadilan Negeri / Pengadilan Hubungan Industrial penanganan perkara |
| provinsi | `provinsi` | String | - | Nama provinsi yurisdiksi perselisihan hubungan industrial |
| tahun_periode | `tahun_periode` | Integer | Tahun | Tahun pencatatan dan penyelesaian sengketa hubungan industrial (2025/2026) |
| ringkasan_pokok_sengketa | `ringkasan_pokok_sengketa` | String | - | Ringkasan objek tuntutan perselisihan (penuntutan uang pesangon PHK efisiensi, selisih upah minimum, tunjangan hak normatif) |
| putusan | `putusan` | json | - | - |
| link_file | `link_file` | String | - | link url pdf |
| minio_file | `minio_file` | String | - | path bukcet file minio |

### JSON field: `putusan` (putusan)

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nomor_Perkara | `nomor_perkara` | String | - | Nomor putusan, format khas: <no>/Pdt.Sus-PHI/<tahun>/PN <kode> (tingkat PN) atau <no> K/Pdt.Sus-PHI/<tahun> (tingkat kasasi MA). |
| Tingkat_Proses | `tingkat_proses` | String | - | Tingkat proses perkara, contoh: 'Pertama' (PN) atau 'Kasasi' (MA). |
| Klasifikasi | `klasifikasi` | String | - | Kategori perkara, contoh: 'Perdata Khusus >> PHI'. |
| Kata_Kunci | `kata_kunci` | String | - | Kata kunci pencarian terkait kasus, contoh: 'PHI Jayapura'. |
| Tahun | `tahun` | Integer | - | Tahun perkara sebagaimana tercantum di sistem. PERINGATAN: pada contoh yang diperiksa, field ini bisa TIDAK konsisten dengan Tanggal_Register/Tanggal_Dibacakan - lihat catatan anomali. |
| Pengadilan | `pengadilan` | String | - | Nama pengadilan yang memutus (PN <kab/kota> untuk tingkat pertama; MAHKAMAH AGUNG untuk kasasi) - proxy wilayah. |
| Jenis_Lembaga_Peradilan | `jenis_lembaga_peradilan` | String | - | Jenis lembaga, contoh: 'PN' (Pengadilan Negeri). |
| Tanggal_Register | `tanggal_register` | Date | - | Tanggal perkara didaftarkan di pengadilan. |
| Tanggal_Musyawarah | `tanggal_musyawarah` | Date | - | Tanggal musyawarah hakim. PERINGATAN: pada contoh yang diperiksa (36/Pdt.Sus-PHI-2019/PN Jap), tanggal ini (23-10-2019) tercatat SEBELUM Tanggal_Register (11-08-2021) - urutan tidak logis, indikasi galat input, perlu verifikasi manual. |
| Tanggal_Dibacakan | `tanggal_dibacakan` | Date | - | Tanggal putusan dibacakan (= Tanggal_Putus). PERINGATAN: beberapa data teramati menunjukkan tanggal di masa depan (anomali, perlu verifikasi manual). |
| Tanggal_Upload | `tanggal_upload` | Date | - | Tanggal putusan diunggah ke Direktori Putusan MA. |
| Hakim_Ketua | `hakim_ketua` | String | - | Nama hakim ketua yang menyidangkan. |
| Hakim_Anggota | `hakim_anggota` | String | - | Nama hakim anggota (bisa lebih dari satu, dipisah koma). |
| Panitera | `panitera` | String | - | Nama panitera pengganti. |
| Penggugat | `penggugat` | String | - | Nama pihak penggugat (bisa individu/pekerja atau perusahaan). |
| Tergugat | `tergugat` | String | - | Nama pihak tergugat (bisa perusahaan/entitas atau individu). |
| Amar | `amar` | String | - | Kategori umum hasil putusan (contoh: 'Lain-lain'). PERINGATAN: sering bernilai generik 'Lain-lain' - status penyelesaian riil harus dibaca dari Catatan_Amar, bukan field ini saja. |
| Amar_Lainnya | `amar_lainnya` | String | - | Flag tambahan terkait amar (contoh nilai teramati: 'NO'). |
| Catatan_Amar | `catatan_amar` | text | - | Narasi lengkap hasil putusan (isi amar). Ini field PALING AKURAT untuk mengisi 'status penyelesaian' pada requirement KAK, karena Amar sendiri sering generik. |
| Kaidah | `kaidah` | String | - | Ringkasan kaidah hukum dari putusan, jika ada (sering kosong/'-'). |
| Abstrak | `abstrak` | text | - | Ringkasan/abstrak kasus, jika ada (sering kosong). |
| Status_Putusan_Listing | `status_putusan_listing` | String | - | Status ringkas yang tampil di halaman LISTING/pencarian (bukan halaman detail), contoh: 'Berkekuatan Hukum Tetap'. Tidak selalu muncul untuk setiap kasus. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class Putusan(BaseModel):
    nomor_perkara: str | None = Field(default=None, alias="Nomor_Perkara", description="Nomor putusan, format khas: <no>/Pdt.Sus-PHI/<tahun>/PN <kode> (tingkat PN) atau <no> K/Pdt.Sus-PHI/<tahun> (tingkat kasasi MA).")
    tingkat_proses: str | None = Field(default=None, alias="Tingkat_Proses", description="Tingkat proses perkara, contoh: 'Pertama' (PN) atau 'Kasasi' (MA).")
    klasifikasi: str | None = Field(default=None, alias="Klasifikasi", description="Kategori perkara, contoh: 'Perdata Khusus >> PHI'.")
    kata_kunci: str | None = Field(default=None, alias="Kata_Kunci", description="Kata kunci pencarian terkait kasus, contoh: 'PHI Jayapura'.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun perkara sebagaimana tercantum di sistem. PERINGATAN: pada contoh yang diperiksa, field ini bisa TIDAK konsisten dengan Tanggal_Register/Tanggal_Dibacakan - lihat catatan anomali.")
    pengadilan: str | None = Field(default=None, alias="Pengadilan", description="Nama pengadilan yang memutus (PN <kab/kota> untuk tingkat pertama; MAHKAMAH AGUNG untuk kasasi) - proxy wilayah.")
    jenis_lembaga_peradilan: str | None = Field(default=None, alias="Jenis_Lembaga_Peradilan", description="Jenis lembaga, contoh: 'PN' (Pengadilan Negeri).")
    tanggal_register: date | None = Field(default=None, alias="Tanggal_Register", description="Tanggal perkara didaftarkan di pengadilan.")
    tanggal_musyawarah: date | None = Field(default=None, alias="Tanggal_Musyawarah", description="Tanggal musyawarah hakim. PERINGATAN: pada contoh yang diperiksa (36/Pdt.Sus-PHI-2019/PN Jap), tanggal ini (23-10-2019) tercatat SEBELUM Tanggal_Register (11-08-2021) - urutan tidak logis, indikasi galat input, perlu verifikasi manual.")
    tanggal_dibacakan: date | None = Field(default=None, alias="Tanggal_Dibacakan", description="Tanggal putusan dibacakan (= Tanggal_Putus). PERINGATAN: beberapa data teramati menunjukkan tanggal di masa depan (anomali, perlu verifikasi manual).")
    tanggal_upload: date | None = Field(default=None, alias="Tanggal_Upload", description="Tanggal putusan diunggah ke Direktori Putusan MA.")
    hakim_ketua: str | None = Field(default=None, alias="Hakim_Ketua", description="Nama hakim ketua yang menyidangkan.")
    hakim_anggota: str | None = Field(default=None, alias="Hakim_Anggota", description="Nama hakim anggota (bisa lebih dari satu, dipisah koma).")
    panitera: str | None = Field(default=None, alias="Panitera", description="Nama panitera pengganti.")
    penggugat: str | None = Field(default=None, alias="Penggugat", description="Nama pihak penggugat (bisa individu/pekerja atau perusahaan).")
    tergugat: str | None = Field(default=None, alias="Tergugat", description="Nama pihak tergugat (bisa perusahaan/entitas atau individu).")
    amar: str | None = Field(default=None, alias="Amar", description="Kategori umum hasil putusan (contoh: 'Lain-lain'). PERINGATAN: sering bernilai generik 'Lain-lain' - status penyelesaian riil harus dibaca dari Catatan_Amar, bukan field ini saja.")
    amar_lainnya: str | None = Field(default=None, alias="Amar_Lainnya", description="Flag tambahan terkait amar (contoh nilai teramati: 'NO').")
    catatan_amar: str | None = Field(default=None, alias="Catatan_Amar", description="Narasi lengkap hasil putusan (isi amar). Ini field PALING AKURAT untuk mengisi 'status penyelesaian' pada requirement KAK, karena Amar sendiri sering generik.")
    kaidah: str | None = Field(default=None, alias="Kaidah", description="Ringkasan kaidah hukum dari putusan, jika ada (sering kosong/'-').")
    abstrak: str | None = Field(default=None, alias="Abstrak", description="Ringkasan/abstrak kasus, jika ada (sering kosong).")
    status_putusan_listing: str | None = Field(default=None, alias="Status_Putusan_Listing", description="Status ringkas yang tampil di halaman LISTING/pencarian (bukan halaman detail), contoh: 'Berkekuatan Hukum Tetap'. Tidak selalu muncul untuk setiap kasus.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class DirektoriPutusanPerkaraPengadilanHubunganRecord(BaseModel):
    nomor_perkara: str | None = Field(default=None, alias="nomor_perkara", description="Nomor registrasi resmi perkara sengketa pada Pengadilan Hubungan Industrial (contoh: 12/Pdt.Sus-PHI/2024/PN Jkt.Pst)")
    jenis_perselisihan: str | None = Field(default=None, alias="jenis_perselisihan", description="Klasifikasi sengketa ketenagakerjaan menurut UU No. 2/2004 (Perselisihan Hak, Perselisihan Kepentingan, Perselisihan PHK, Perselisihan Antar Serikat Pekerja)")
    tanggal_mulai_daftar: date | None = Field(default=None, alias="tanggal_mulai_daftar", description="Tanggal pendaftaran berkas gugatan di kepaniteraan Pengadilan Hubungan Industrial")
    tanggal_selesai_putus: date | None = Field(default=None, alias="tanggal_selesai_putus", description="Tanggal pembacaan putusan sidang oleh majelis hakim PHI")
    lama_penyelesaian_hari_kerja: int | None = Field(default=None, alias="lama_penyelesaian_hari_kerja", description="Durasi penanganan perkara dari registrasi hingga putusan (maksimal 50 hari kerja berdasarkan Pasal 103 UU No. 2/2004)")
    status_penyelesaian: str | None = Field(default=None, alias="status_penyelesaian", description="Amar putusan sengketa (Kabul Seluruhnya, Kabul Sebagian, Ditolak, Dicabut, Akta Perdamaian/Dading)")
    nama_penggugat: str | None = Field(default=None, alias="nama_penggugat", description="Identitas pihak penggugat (Pekerja / Karyawan / Serikat Pekerja)")
    nama_perusahaan_tergugat: str | None = Field(default=None, alias="nama_perusahaan_tergugat", description="Identitas pihak tergugat / nama badan usaha pemberi kerja (PT, CV, Badan Usaha)")
    sektor_industri: str | None = Field(default=None, alias="sektor_industri", description="Sektor lapangan usaha entitas tergugat (Tekstil & Garmen, Manufaktur Otomotif, Logistik & Pergudangan, Perdagangan Ritel, Jasa Perhotelan, dsb.)")
    wilayah_pengadilan: str | None = Field(default=None, alias="wilayah_pengadilan", description="Pengadilan Negeri / Pengadilan Hubungan Industrial penanganan perkara")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi yurisdiksi perselisihan hubungan industrial")
    tahun_periode: int | None = Field(default=None, alias="tahun_periode", description="Tahun pencatatan dan penyelesaian sengketa hubungan industrial (2025/2026)")
    ringkasan_pokok_sengketa: str | None = Field(default=None, alias="ringkasan_pokok_sengketa", description="Ringkasan objek tuntutan perselisihan (penuntutan uang pesangon PHK efisiensi, selisih upah minimum, tunjangan hak normatif)")
    putusan: Putusan | None = Field(default=None, alias="putusan", description="nomor_perkara: Nomor putusan, format khas: <no>/Pdt.Sus-PHI/<tahun>/PN <kode> (tingkat PN) atau <no> K/Pdt.Sus-PHI/<tahun> (tingkat kasasi MA).; tingkat_proses: Tingkat proses perkara, contoh: 'Pertama' (PN) atau 'Kasasi' (MA).; klasifikasi: Kategori perkara, contoh: 'Perdata Khusus >> PHI'.; kata_kunci: Kata kunci pencarian terkait kasus, contoh: 'PHI Jayapura'.; tahun: Tahun perkara sebagaimana tercantum di sistem. PERINGATAN: pada contoh yang diperiksa, field ini bisa TIDAK konsisten dengan Tanggal_Register/Tanggal_Dibacakan - lihat catatan anomali.; pengadilan: Nama pengadilan yang memutus (PN <kab/kota> untuk tingkat pertama; MAHKAMAH AGUNG untuk kasasi) - proxy wilayah.; jenis_lembaga_peradilan: Jenis lembaga, contoh: 'PN' (Pengadilan Negeri).; tanggal_register: Tanggal perkara didaftarkan di pengadilan.; tanggal_musyawarah: Tanggal musyawarah hakim. PERINGATAN: pada contoh yang diperiksa (36/Pdt.Sus-PHI-2019/PN Jap), tanggal ini (23-10-2019) tercatat SEBELUM Tanggal_Register (11-08-2021) - urutan tidak logis, indikasi galat input, perlu verifikasi manual.; tanggal_dibacakan: Tanggal putusan dibacakan (= Tanggal_Putus). PERINGATAN: beberapa data teramati menunjukkan tanggal di masa depan (anomali, perlu verifikasi manual).; tanggal_upload: Tanggal putusan diunggah ke Direktori Putusan MA.; hakim_ketua: Nama hakim ketua yang menyidangkan.; hakim_anggota: Nama hakim anggota (bisa lebih dari satu, dipisah koma).; panitera: Nama panitera pengganti.; penggugat: Nama pihak penggugat (bisa individu/pekerja atau perusahaan).; tergugat: Nama pihak tergugat (bisa perusahaan/entitas atau individu).; amar: Kategori umum hasil putusan (contoh: 'Lain-lain'). PERINGATAN: sering bernilai generik 'Lain-lain' - status penyelesaian riil harus dibaca dari Catatan_Amar, bukan field ini saja.; amar_lainnya: Flag tambahan terkait amar (contoh nilai teramati: 'NO').; catatan_amar: Narasi lengkap hasil putusan (isi amar). Ini field PALING AKURAT untuk mengisi 'status penyelesaian' pada requirement KAK, karena Amar sendiri sering generik.; kaidah: Ringkasan kaidah hukum dari putusan, jika ada (sering kosong/'-').; abstrak: Ringkasan/abstrak kasus, jika ada (sering kosong).; status_putusan_listing: Status ringkas yang tampil di halaman LISTING/pencarian (bukan halaman detail), contoh: 'Berkekuatan Hukum Tetap'. Tidak selalu muncul untuk setiap kasus.")
    link_file: str | None = Field(default=None, alias="link_file", description="link url pdf")
    minio_file: str | None = Field(default=None, alias="minio_file", description="path bukcet file minio")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
