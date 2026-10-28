# Data Dictionary: Notifikasi ePing

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Notifikasi ePing`
- Publisher: WTO
- Data access: `api`
- Update frequency: Harian
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/wto/eping_notifikasi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| id | `id` | String | ID | ID unik notifikasi di ePing. Kunci dedup antar-pengambilan. |
| area | `area` | String | Kode | Jenis notifikasi WTO: SPS (sanitary & phytosanitary) atau TBT (hambatan teknis perdagangan). |
| notificationType | `notificationtype` | String | Kategori | Regular notification, Emergency notification, Addendum, Corrigendum, Revision. |
| distributionDate | `distributiondate` | Date | Tanggal | Tanggal notifikasi diedarkan WTO. Dipakai sebagai tanggal kejadian & filter periode. |
| commentDeadlineDate | `commentdeadlinedate` | Date | Tanggal | Batas waktu negara anggota (termasuk RI) mengirim komentar. Dasar peringatan tenggat. |
| proposedAdoptionDate | `proposedadoptiondate` | Date | Tanggal | Rencana tanggal adopsi aturan. Sering kosong (lihat proposedAdoptionDateText). |
| proposedEntryIntoForceDate | `proposedentryintoforcedate` | Date | Tanggal | Rencana tanggal mulai berlaku. Sering kosong; banyak berlaku "6 bulan setelah adopsi". |
| documentSymbol | `documentsymbol` | String | Kode | Simbol dokumen WTO, mis. G/SPS/N/MEX/477. Perlu trim spasi di depan. |
| notifyingMember | `notifyingmember` | String | - | Negara/anggota WTO yang menerbitkan aturan (negara mitra). |
| notifyingMemberCode | `notifyingmembercode` | String | Kode | Kode anggota ePing (C + kode numerik ISO 3166, mis. C484 = Meksiko). Dipetakan ke ISO3. |
| titlePlain | `titleplain` | String | - | Judul notifikasi tanpa HTML. Bahasa mengikuti notifikasi (EN/ES/FR). |
| descriptionPlain | `descriptionplain` | Text | - | Ringkasan isi aturan tanpa HTML. |
| productsFreeTextPlain | `productsfreetextplain` | String | - | Produk yang diatur (teks bebas). |
| hsCodeText | `hscodetext` | String | Kode HS | Daftar kode HS terdampak, dipisah koma. Kunci join ke data ekspor RI (BPS) untuk menilai dampak. Terisi ±58% notifikasi. |
| icsCodeText | `icscodetext` | String | Kode ICS | Kode standar ICS terkait. |
| keywords | `keywords` | String (list) | - | Kata kunci ePing (mis. Food safety, Pests), digabung "; ". |
| objectives | `objectives` | String (list) | - | Tujuan aturan (mis. Food safety, Protect territory), digabung "; ". |
| allTradingPartners | `alltradingpartners` | Boolean | - | True = berlaku untuk semua mitra dagang, termasuk Indonesia. |
| countriesAffected | `countriesaffected` | String (list) | - | Negara yang disebut terdampak bila aturan khusus negara tertentu. Indonesia terdampak bila allTradingPartners = True atau Indonesia tercantum di sini. |
| conformStandardYes | `conformstandardyes` | Boolean | - | True = aturan sesuai standar internasional (Codex/OIE/IPPC). Bisa dipakai sebagai indikator tingkat hambatan. |
| tradeFacilitatingMeasure | `tradefacilitatingmeasure` | Boolean | - | True = notifikasi bersifat memfasilitasi perdagangan (bukan pembatasan). |
| parentId | `parentid` | Integer | ID | ID notifikasi induk untuk addendum/revisi. Dipakai untuk menggabungkan riwayat satu aturan. |
| linkToNotification | `linktonotification` | String | URL | Tautan dokumen notifikasi resmi WTO (docx/pdf). |
| notifiedDocumentLink | `notifieddocumentlink` | String | URL | Tautan dokumen aturan dari negara penerbit; bisa lebih dari satu (dipisah baris baru). |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class NotifikasiEpingRecord(BaseModel):
    id: str | None = Field(default=None, alias="id", description="ID unik notifikasi di ePing. Kunci dedup antar-pengambilan.")
    area: str | None = Field(default=None, alias="area", description="Jenis notifikasi WTO: SPS (sanitary & phytosanitary) atau TBT (hambatan teknis perdagangan).")
    notificationtype: str | None = Field(default=None, alias="notificationType", description="Regular notification, Emergency notification, Addendum, Corrigendum, Revision.")
    distributiondate: date | None = Field(default=None, alias="distributionDate", description="Tanggal notifikasi diedarkan WTO. Dipakai sebagai tanggal kejadian & filter periode.")
    commentdeadlinedate: date | None = Field(default=None, alias="commentDeadlineDate", description="Batas waktu negara anggota (termasuk RI) mengirim komentar. Dasar peringatan tenggat.")
    proposedadoptiondate: date | None = Field(default=None, alias="proposedAdoptionDate", description="Rencana tanggal adopsi aturan. Sering kosong (lihat proposedAdoptionDateText).")
    proposedentryintoforcedate: date | None = Field(default=None, alias="proposedEntryIntoForceDate", description="Rencana tanggal mulai berlaku. Sering kosong; banyak berlaku \"6 bulan setelah adopsi\".")
    documentsymbol: str | None = Field(default=None, alias="documentSymbol", description="Simbol dokumen WTO, mis. G/SPS/N/MEX/477. Perlu trim spasi di depan.")
    notifyingmember: str | None = Field(default=None, alias="notifyingMember", description="Negara/anggota WTO yang menerbitkan aturan (negara mitra).")
    notifyingmembercode: str | None = Field(default=None, alias="notifyingMemberCode", description="Kode anggota ePing (C + kode numerik ISO 3166, mis. C484 = Meksiko). Dipetakan ke ISO3.")
    titleplain: str | None = Field(default=None, alias="titlePlain", description="Judul notifikasi tanpa HTML. Bahasa mengikuti notifikasi (EN/ES/FR).")
    descriptionplain: str | None = Field(default=None, alias="descriptionPlain", description="Ringkasan isi aturan tanpa HTML.")
    productsfreetextplain: str | None = Field(default=None, alias="productsFreeTextPlain", description="Produk yang diatur (teks bebas).")
    hscodetext: str | None = Field(default=None, alias="hsCodeText", description="Daftar kode HS terdampak, dipisah koma. Kunci join ke data ekspor RI (BPS) untuk menilai dampak. Terisi ±58% notifikasi.")
    icscodetext: str | None = Field(default=None, alias="icsCodeText", description="Kode standar ICS terkait.")
    keywords: str | None = Field(default=None, alias="keywords", description="Kata kunci ePing (mis. Food safety, Pests), digabung \"; \".")
    objectives: str | None = Field(default=None, alias="objectives", description="Tujuan aturan (mis. Food safety, Protect territory), digabung \"; \".")
    alltradingpartners: bool | None = Field(default=None, alias="allTradingPartners", description="True = berlaku untuk semua mitra dagang, termasuk Indonesia.")
    countriesaffected: str | None = Field(default=None, alias="countriesAffected", description="Negara yang disebut terdampak bila aturan khusus negara tertentu. Indonesia terdampak bila allTradingPartners = True atau Indonesia tercantum di sini.")
    conformstandardyes: bool | None = Field(default=None, alias="conformStandardYes", description="True = aturan sesuai standar internasional (Codex/OIE/IPPC). Bisa dipakai sebagai indikator tingkat hambatan.")
    tradefacilitatingmeasure: bool | None = Field(default=None, alias="tradeFacilitatingMeasure", description="True = notifikasi bersifat memfasilitasi perdagangan (bukan pembatasan).")
    parentid: int | None = Field(default=None, alias="parentId", description="ID notifikasi induk untuk addendum/revisi. Dipakai untuk menggabungkan riwayat satu aturan.")
    linktonotification: str | None = Field(default=None, alias="linkToNotification", description="Tautan dokumen notifikasi resmi WTO (docx/pdf).")
    notifieddocumentlink: str | None = Field(default=None, alias="notifiedDocumentLink", description="Tautan dokumen aturan dari negara penerbit; bisa lebih dari satu (dipisah baris baru).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
