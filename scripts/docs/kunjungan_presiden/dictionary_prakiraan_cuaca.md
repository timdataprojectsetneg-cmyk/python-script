# Data Dictionary: BMKG Prakiraan Cuaca

> Generated from Kesiapan Kunjungan.xlsx (sheet BMKG - Prakiraan Cuaca). Reference for the Pydantic model in `models.py`.

- Use case: `kunjungan_presiden`
- Publisher: `bmkg`
- Source: `prakiraan_cuaca`
- Data access: `api`
- Update frequency: 2 kali sehari (Prakiraan 3 hari ke depan, resolusi 3 jam)
- Eligible: `True`
- Endpoint URL: `https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={kode_wilayah}`
- Target module: `ingestion/usecases/kunjungan_presiden/bmkg/prakiraan_cuaca/models.py`
- Target schema / table: `raw_kunker.raw_bmkg_prakiraan_cuaca`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| adm4 | `adm4` | String | kode wilayah | Kode wilayah administrasi tingkat IV (kelurahan/desa) Kemendagri. |
| provinsi | `provinsi` | String | - | Nama provinsi. |
| kotkab | `kotkab` | String | - | Nama kabupaten/kota. |
| kecamatan | `kecamatan` | String | - | Nama kecamatan. |
| desa | `desa` | String | - | Nama desa/kelurahan. |
| lon | `lon` | Float | derajat | Longitude titik koordinat lokasi administrasi. |
| lat | `lat` | Float | derajat | Latitude titik koordinat lokasi administrasi. |
| timezone | `timezone` | String | zona waktu | Zona waktu lokasi (Asia/Jakarta, Asia/Makassar, Asia/Jayapura). |
| local_datetime | `local_datetime` | DateTime | WIB/setempat | Waktu prakiraan lokal (format YYYY-MM-DD HH:mm:ss). |
| utc_datetime | `utc_datetime` | DateTime | UTC | Waktu prakiraan standar UTC. |
| t | `t` | Float | °C | Suhu udara permukaan dalam derajat Celsius. |
| hu | `hu` | Float | % | Kelembapan relatif udara dalam persentase. |
| weather_desc | `weather_desc` | String | - | Kondisi cuaca dalam Bahasa Indonesia (Cerah, Berawan, Hujan Ringan, dll.). |
| weather_desc_en | `weather_desc_en` | String | - | Kondisi cuaca dalam Bahasa Inggris. |
| ws | `ws` | Float | km/jam | Kecepatan angin permukaan. |
| wd | `wd` | String | arah | Arah mata angin asal tiupan angin. |
| tcc | `tcc` | Float | % | Tutupan awan total (Total Cloud Cover). |
| vs_text | `vs_text` | String | km | Jarak pandang mendatar (Visibility). |
| analysis_date | `analysis_date` | DateTime | UTC | Waktu produksi data prakiraan oleh BMKG. |

## Pydantic Model

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class PrakiraanCuacaRecord(BaseModel):
    adm4: str = Field(description="Kode wilayah administrasi tingkat IV (kelurahan/desa).")
    provinsi: Optional[str] = Field(default=None, description="Nama provinsi.")
    kotkab: Optional[str] = Field(default=None, description="Nama kabupaten/kota.")
    kecamatan: Optional[str] = Field(default=None, description="Nama kecamatan.")
    desa: Optional[str] = Field(default=None, description="Nama desa/kelurahan.")
    lon: Optional[float] = Field(default=None, description="Longitude lokasi administrasi.")
    lat: Optional[float] = Field(default=None, description="Latitude lokasi administrasi.")
    timezone: Optional[str] = Field(default=None, description="Zona waktu lokasi.")
    local_datetime: Optional[str] = Field(default=None, description="Waktu prakiraan lokal (WIB/WITA/WIT).")
    utc_datetime: Optional[str] = Field(default=None, description="Waktu prakiraan UTC.")
    t: Optional[float] = Field(default=None, description="Suhu udara (derajat Celsius).")
    hu: Optional[float] = Field(default=None, description="Kelembapan udara (%).")
    weather_desc: Optional[str] = Field(default=None, description="Kondisi cuaca dalam Bahasa Indonesia.")
    weather_desc_en: Optional[str] = Field(default=None, description="Kondisi cuaca dalam Bahasa Inggris.")
    ws: Optional[float] = Field(default=None, description="Kecepatan angin (km/jam).")
    wd: Optional[str] = Field(default=None, description="Arah angin.")
    tcc: Optional[float] = Field(default=None, description="Tutupan awan (%).")
    vs_text: Optional[str] = Field(default=None, description="Jarak pandang (km).")
    analysis_date: Optional[str] = Field(default=None, description="Waktu analisis produksi data prakiraan.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

Record = PrakiraanCuacaRecord
```
