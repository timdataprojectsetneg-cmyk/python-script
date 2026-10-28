# Data Dictionary: Kejadian Bencana BNPB

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Kejadian Bencana BNPB`
- Publisher: BNPB
- Data access: `excel`
- Update frequency: Harian
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Situasi Global dan Kawasan (1).xlsx
- Target module: `ingestion/usecases/geopolitik/bnpb/kejadian_bencana/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No. | `no` | Integer | Urutan | Nomor urut baris pada hasil unduhan (bukan ID kejadian; berubah tiap unduh). |
| Kode Identitas Bencana | `kode_identitas_bencana` | String | Kode | Kode identitas kejadian BNPB. KOSONG di seluruh baris sampel — tidak bisa dipakai sebagai kunci; dedup pakai (Tanggal, Kejadian, ID Kabupaten, Lokasi). |
| ID Kabupaten | `id_kabupaten` | Integer | Kode wilayah (4 digit) | Kode kabupaten/kota (pola kode wilayah Kemendagri/BPS, mis. 3315 = Grobogan). Satu-satunya kunci lokasi: tidak ada koordinat, marker peta = titik tengah kabupaten (perlu tabel referensi kabupaten + koordinat). |
| Tanggal Kejadian | `tanggal_kejadian` | Date | Tanggal | Tanggal kejadian (tanpa jam; di Excel bertipe datetime 00:00:00). |
| Kejadian | `kejadian` | String | Kategori | Jenis bencana, huruf kapital (sampel: KEBAKARAN HUTAN DAN LAHAN 90, BANJIR 4, KEKERINGAN 4). Jenis lain mengikuti daftar BNPB (gempa bumi, tanah longsor, cuaca ekstrem, dll.). |
| Lokasi | `lokasi` | String | - | Kecamatan/desa terdampak, teks bebas diawali "Kecamatan:" dengan karakter "\n" literal (bukan baris baru); kadang memuat ringkasan "( 1 Kecamatan / 3 Desa )". Perlu dibersihkan. |
| Kabupaten | `kabupaten` | String | - | Nama kabupaten/kota. |
| Provinsi | `provinsi` | String | - | Nama provinsi. |
| Kronologi & Dokumentasi | `kronologi_dokumentasi` | String | - | Hanya teks "Dokumentasi" di seluruh baris — tautan ke kronologi/foto tidak ikut terunduh. |
| Penyebab | `penyebab` | String | - | Penyebab kejadian. KOSONG di seluruh sampel. |
| Meninggal | `meninggal` | Integer | Orang | Korban meninggal. Kosong = tidak ada laporan (bukan pasti 0); sampel: 1 baris terisi. |
| Hilang | `hilang` | Integer | Orang | Korban hilang. Kosong di seluruh sampel. |
| Terluka | `terluka` | Integer | Orang | Korban luka. Kosong di seluruh sampel. |
| Rumah Rusak | `rumah_rusak` | Integer | Unit | Rumah rusak (gabungan; tidak dipisah ringan/sedang/berat). 0 di sebagian besar baris. |
| Rumah Terendam | `rumah_terendam` | Integer | Unit | Rumah terendam (banjir). Kosong kecuali 1 baris. |
| Fasum Rusak | `fasum_rusak` | Integer | Unit | Fasilitas umum rusak. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class KejadianBencanaBnpbRecord(BaseModel):
    no: int | None = Field(default=None, alias="No.", description="Nomor urut baris pada hasil unduhan (bukan ID kejadian; berubah tiap unduh).")
    kode_identitas_bencana: str | None = Field(default=None, alias="Kode Identitas Bencana", description="Kode identitas kejadian BNPB. KOSONG di seluruh baris sampel — tidak bisa dipakai sebagai kunci; dedup pakai (Tanggal, Kejadian, ID Kabupaten, Lokasi).")
    id_kabupaten: int | None = Field(default=None, alias="ID Kabupaten", description="Kode kabupaten/kota (pola kode wilayah Kemendagri/BPS, mis. 3315 = Grobogan). Satu-satunya kunci lokasi: tidak ada koordinat, marker peta = titik tengah kabupaten (perlu tabel referensi kabupaten + koordinat).")
    tanggal_kejadian: date | None = Field(default=None, alias="Tanggal Kejadian", description="Tanggal kejadian (tanpa jam; di Excel bertipe datetime 00:00:00).")
    kejadian: str | None = Field(default=None, alias="Kejadian", description="Jenis bencana, huruf kapital (sampel: KEBAKARAN HUTAN DAN LAHAN 90, BANJIR 4, KEKERINGAN 4). Jenis lain mengikuti daftar BNPB (gempa bumi, tanah longsor, cuaca ekstrem, dll.).")
    lokasi: str | None = Field(default=None, alias="Lokasi", description="Kecamatan/desa terdampak, teks bebas diawali \"Kecamatan:\" dengan karakter \"\\n\" literal (bukan baris baru); kadang memuat ringkasan \"( 1 Kecamatan / 3 Desa )\". Perlu dibersihkan.")
    kabupaten: str | None = Field(default=None, alias="Kabupaten", description="Nama kabupaten/kota.")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    kronologi_dokumentasi: str | None = Field(default=None, alias="Kronologi & Dokumentasi", description="Hanya teks \"Dokumentasi\" di seluruh baris — tautan ke kronologi/foto tidak ikut terunduh.")
    penyebab: str | None = Field(default=None, alias="Penyebab", description="Penyebab kejadian. KOSONG di seluruh sampel.")
    meninggal: int | None = Field(default=None, alias="Meninggal", description="Korban meninggal. Kosong = tidak ada laporan (bukan pasti 0); sampel: 1 baris terisi.")
    hilang: int | None = Field(default=None, alias="Hilang", description="Korban hilang. Kosong di seluruh sampel.")
    terluka: int | None = Field(default=None, alias="Terluka", description="Korban luka. Kosong di seluruh sampel.")
    rumah_rusak: int | None = Field(default=None, alias="Rumah Rusak", description="Rumah rusak (gabungan; tidak dipisah ringan/sedang/berat). 0 di sebagian besar baris.")
    rumah_terendam: int | None = Field(default=None, alias="Rumah Terendam", description="Rumah terendam (banjir). Kosong kecuali 1 baris.")
    fasum_rusak: int | None = Field(default=None, alias="Fasum Rusak", description="Fasilitas umum rusak.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
