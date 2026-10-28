# Data Dictionary: Gempa Dirasakan BMKG

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Gempa Dirasakan BMKG`
- Publisher: BMKG
- Data access: `api`
- Update frequency: Real-time (polling tiap 5–15 menit)
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Situasi Global dan Kawasan (1).xlsx
- Target module: `ingestion/usecases/geopolitik/bmkg/gempa_dirasakan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal | `tanggal` | String | DD Mon YYYY (ID) | Tanggal kejadian dalam WIB, nama bulan bahasa Indonesia (mis. "25 Okt 2026"). |
| Jam | `jam` | String | HH:MM:SS WIB | Jam kejadian WIB (teks berakhiran "WIB"). |
| DateTime | `datetime` | Datetime | ISO 8601 UTC | Waktu kejadian UTC (+00:00). Dipakai sebagai waktu baku; kunci dedup bersama koordinat. |
| point/coordinates | `point_coordinates` | String | "lintang,bujur" desimal | Koordinat episenter dalam satu string (mis. "-0.73,131.39"); urutan lintang dulu lalu bujur — perlu dipecah. |
| Lintang | `lintang` | String | Derajat + LU/LS | Lintang teks (mis. "0.73 LS"). Redundan dengan coordinates. |
| Bujur | `bujur` | String | Derajat + BT/BB | Bujur teks (mis. "131.39 BT"). |
| Magnitude | `magnitude` | Decimal | Magnitudo (M) | Kekuatan gempa. |
| Kedalaman | `kedalaman` | String | km (teks) | Kedalaman hiposenter, teks berakhiran " km" — perlu diubah ke angka. |
| Wilayah | `wilayah` | String | - | Lokasi relatif episenter (mis. "Pusat gempa berada di laut 13 km timur laut Kota Sorong"); jarak & arah hanya di teks. |
| Dirasakan | `dirasakan` | String | Skala MMI + daerah | Intensitas guncangan per daerah (mis. "III Kota Bengkulu, II - III Curup"); format bebas, beberapa daerah dipisah koma — perlu parsing. |

## Generated Pydantic model

```python
from datetime import datetime
from pydantic import BaseModel, Field


class GempaDirasakanBmkgRecord(BaseModel):
    tanggal: str | None = Field(default=None, alias="Tanggal", description="Tanggal kejadian dalam WIB, nama bulan bahasa Indonesia (mis. \"25 Okt 2026\").")
    jam: str | None = Field(default=None, alias="Jam", description="Jam kejadian WIB (teks berakhiran \"WIB\").")
    datetime: datetime | None = Field(default=None, alias="DateTime", description="Waktu kejadian UTC (+00:00). Dipakai sebagai waktu baku; kunci dedup bersama koordinat.")
    point_coordinates: str | None = Field(default=None, alias="point/coordinates", description="Koordinat episenter dalam satu string (mis. \"-0.73,131.39\"); urutan lintang dulu lalu bujur — perlu dipecah.")
    lintang: str | None = Field(default=None, alias="Lintang", description="Lintang teks (mis. \"0.73 LS\"). Redundan dengan coordinates.")
    bujur: str | None = Field(default=None, alias="Bujur", description="Bujur teks (mis. \"131.39 BT\").")
    magnitude: float | None = Field(default=None, alias="Magnitude", description="Kekuatan gempa.")
    kedalaman: str | None = Field(default=None, alias="Kedalaman", description="Kedalaman hiposenter, teks berakhiran \" km\" — perlu diubah ke angka.")
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Lokasi relatif episenter (mis. \"Pusat gempa berada di laut 13 km timur laut Kota Sorong\"); jarak & arah hanya di teks.")
    dirasakan: str | None = Field(default=None, alias="Dirasakan", description="Intensitas guncangan per daerah (mis. \"III Kota Bengkulu, II - III Curup\"); format bebas, beberapa daerah dipisah koma — perlu parsing.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
