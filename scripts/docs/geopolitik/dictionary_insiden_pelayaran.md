# Data Dictionary: Insiden Pelayaran UKMTO

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Insiden Pelayaran UKMTO`
- Publisher: UKMTO
- Data access: `api`
- Update frequency: Real-time (polling tiap jam)
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/ukmto/insiden_pelayaran/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| incidentIssuer | `incidentissuer` | String | - | Penerbit laporan (UKMTO). |
| incidentNumber | `incidentnumber` | Integer | Nomor | Nomor insiden tahunan (mis. 148 → "WARNING 148-26"). Nomor bisa meloncat (sampel: 161 tidak ada) dan urutan respons tidak selalu urut. |
| sitecoreId | `sitecoreid` | String | UUID | ID unik record di CMS UKMTO. Kunci dedup/upsert (record bisa diperbarui, mis. reklasifikasi). |
| utcDateCreated | `utcdatecreated` | Datetime | UTC (ISO 8601) | Waktu laporan dibuat/diterbitkan UKMTO. |
| utcDateOfIncident | `utcdateofincident` | Datetime | UTC (ISO 8601) | Waktu kejadian. Dipakai untuk kronologi & peta. Bisa lebih awal (laporan "time-late") atau bahkan lebih lambat dari utcDateCreated (inkonsistensi input). |
| pinColour | `pincolour` | String | Kategori | Warna penanda di peta UKMTO (Red / Yellow). Indikasi tingkat keparahan versi UKMTO. |
| incidentTypeName | `incidenttypename` | String | Kategori | Jenis insiden: Attack, Suspicious Activity, Advisory (dan jenis lain, mis. Boarding, Hijack). |
| incidentTypeLevel | `incidenttypelevel` | Integer | Kode | Kode numerik jenis insiden (sampel: 0 = Suspicious Activity, 1 = Attack, 3 = Advisory). |
| locationLatitude | `locationlatitude` | Decimal | Derajat | Lintang kejadian (desimal). Untuk peta insiden & penghitungan per chokepoint. |
| locationLongitude | `locationlongitude` | Decimal | Derajat | Bujur kejadian (desimal). |
| locationLatitudeDDDMMSS | `locationlatitudedddmmss` | String | DDMMSS + N/S | Lintang format derajat-menit-detik (mis. 262600N). Huruf arah kadang kecil (n/e). |
| locationLongitudeDDDMMSS | `locationlongitudedddmmss` | String | DDDMMSS + E/W | Bujur format derajat-menit-detik (mis. 0562910E). |
| region | `region` | String | Kode | Kode wilayah UKMTO (sampel seluruhnya "IO" = Indian Ocean). |
| place | `place` | String | - | Nama perairan, mis. Strait of Hormuz, Bab el Mandeb, Gulf of Aden, Gulf of Oman. Dipetakan ke chokepoint PortWatch. |
| vesselName | `vesselname` | String | - | Nama kapal. Umumnya disamarkan (".", "-", "TKR", "MERCHANT", "vessel") — tidak bisa dipakai sebagai identitas kapal. |
| vesselType | `vesseltype` | String | Kategori | Jenis kapal: Tanker, Cargo, Tug, dll. Ada spasi di akhir nilai ("Tanker "). |
| vesselUnderPirateControl | `vesselunderpiratecontrol` | Boolean | - | True bila kapal dikuasai perompak. |
| dateVesselTaken | `datevesseltaken` | Datetime | UTC | Tanggal kapal dikuasai (bila ada). Kosong pada sampel. |
| crewHeld | `crewheld` | Integer | Orang | Jumlah awak yang ditahan. |
| otherDetails | `otherdetails` | Text | - | Narasi laporan: lokasi relatif (mis. "11NM west of Bukha, Oman"), arah transit, sumber laporan, korban, kerusakan, dampak lingkungan, dan update/reklasifikasi ("Update 001"). Detail ini hanya ada di teks — perlu ekstraksi AI. Mengandung \r\n. |
| hideFromTicker | `hidefromticker` | Boolean | - | Flag tampilan ticker situs UKMTO (tidak relevan untuk analisis). |
| extendTickerTime | `extendtickertime` | Boolean | - | Flag tampilan ticker situs UKMTO (tidak relevan untuk analisis). |

## Generated Pydantic model

```python
from datetime import datetime
from pydantic import BaseModel, Field


class InsidenPelayaranUkmtoRecord(BaseModel):
    incidentissuer: str | None = Field(default=None, alias="incidentIssuer", description="Penerbit laporan (UKMTO).")
    incidentnumber: int | None = Field(default=None, alias="incidentNumber", description="Nomor insiden tahunan (mis. 148 → \"WARNING 148-26\"). Nomor bisa meloncat (sampel: 161 tidak ada) dan urutan respons tidak selalu urut.")
    sitecoreid: str | None = Field(default=None, alias="sitecoreId", description="ID unik record di CMS UKMTO. Kunci dedup/upsert (record bisa diperbarui, mis. reklasifikasi).")
    utcdatecreated: datetime | None = Field(default=None, alias="utcDateCreated", description="Waktu laporan dibuat/diterbitkan UKMTO.")
    utcdateofincident: datetime | None = Field(default=None, alias="utcDateOfIncident", description="Waktu kejadian. Dipakai untuk kronologi & peta. Bisa lebih awal (laporan \"time-late\") atau bahkan lebih lambat dari utcDateCreated (inkonsistensi input).")
    pincolour: str | None = Field(default=None, alias="pinColour", description="Warna penanda di peta UKMTO (Red / Yellow). Indikasi tingkat keparahan versi UKMTO.")
    incidenttypename: str | None = Field(default=None, alias="incidentTypeName", description="Jenis insiden: Attack, Suspicious Activity, Advisory (dan jenis lain, mis. Boarding, Hijack).")
    incidenttypelevel: int | None = Field(default=None, alias="incidentTypeLevel", description="Kode numerik jenis insiden (sampel: 0 = Suspicious Activity, 1 = Attack, 3 = Advisory).")
    locationlatitude: float | None = Field(default=None, alias="locationLatitude", description="Lintang kejadian (desimal). Untuk peta insiden & penghitungan per chokepoint.")
    locationlongitude: float | None = Field(default=None, alias="locationLongitude", description="Bujur kejadian (desimal).")
    locationlatitudedddmmss: str | None = Field(default=None, alias="locationLatitudeDDDMMSS", description="Lintang format derajat-menit-detik (mis. 262600N). Huruf arah kadang kecil (n/e).")
    locationlongitudedddmmss: str | None = Field(default=None, alias="locationLongitudeDDDMMSS", description="Bujur format derajat-menit-detik (mis. 0562910E).")
    region: str | None = Field(default=None, alias="region", description="Kode wilayah UKMTO (sampel seluruhnya \"IO\" = Indian Ocean).")
    place: str | None = Field(default=None, alias="place", description="Nama perairan, mis. Strait of Hormuz, Bab el Mandeb, Gulf of Aden, Gulf of Oman. Dipetakan ke chokepoint PortWatch.")
    vesselname: str | None = Field(default=None, alias="vesselName", description="Nama kapal. Umumnya disamarkan (\".\", \"-\", \"TKR\", \"MERCHANT\", \"vessel\") — tidak bisa dipakai sebagai identitas kapal.")
    vesseltype: str | None = Field(default=None, alias="vesselType", description="Jenis kapal: Tanker, Cargo, Tug, dll. Ada spasi di akhir nilai (\"Tanker \").")
    vesselunderpiratecontrol: bool | None = Field(default=None, alias="vesselUnderPirateControl", description="True bila kapal dikuasai perompak.")
    datevesseltaken: datetime | None = Field(default=None, alias="dateVesselTaken", description="Tanggal kapal dikuasai (bila ada). Kosong pada sampel.")
    crewheld: int | None = Field(default=None, alias="crewHeld", description="Jumlah awak yang ditahan.")
    otherdetails: str | None = Field(default=None, alias="otherDetails", description="Narasi laporan: lokasi relatif (mis. \"11NM west of Bukha, Oman\"), arah transit, sumber laporan, korban, kerusakan, dampak lingkungan, dan update/reklasifikasi (\"Update 001\"). Detail ini hanya ada di teks — perlu ekstraksi AI. Mengandung \\r\\n.")
    hidefromticker: bool | None = Field(default=None, alias="hideFromTicker", description="Flag tampilan ticker situs UKMTO (tidak relevan untuk analisis).")
    extendtickertime: bool | None = Field(default=None, alias="extendTickerTime", description="Flag tampilan ticker situs UKMTO (tidak relevan untuk analisis).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
