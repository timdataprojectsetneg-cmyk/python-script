# Data Dictionary: Perubahan Tarif PMK 50-2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Perubahan Tarif PMK 50-2026`
- Publisher: Bea Cukai
- Data access: `pdf`
- Update frequency: Sesuai perubahan regulasi
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/beacukai/perubahan_tarif_pmk/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Peraturan | `peraturan` | String | - | Nomor regulasi yang menjadi dasar perubahan tarif. |
| Tanggal Berlaku | `tanggal_berlaku` | Date | Tanggal | Tanggal mulai berlaku regulasi. |
| Kode HS | `kode_hs` | String | HS 8 digit | Pos tarif sebagaimana Pasal II PMK 50/2026. |
| Komoditas | `komoditas` | String | - | Kelompok barang yang disebut dalam Pasal II. |
| Tarif Bea Masuk | `tarif_bea_masuk` | Decimal | Persen | Tarif bea masuk yang berlaku selama periode kebijakan. |
| Masa Berlaku Tarif | `masa_berlaku_tarif` | String | - | Durasi khusus yang ditetapkan regulasi. |
| Konteks Kebijakan | `konteks_kebijakan` | String | - | Tujuan kebijakan yang dijelaskan dalam pertimbangan regulasi. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Halaman bukti dalam PDF resmi. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class PerubahanTarifPmk502026Record(BaseModel):
    peraturan: str | None = Field(default=None, alias="Peraturan", description="Nomor regulasi yang menjadi dasar perubahan tarif.")
    tanggal_berlaku: date | None = Field(default=None, alias="Tanggal Berlaku", description="Tanggal mulai berlaku regulasi.")
    kode_hs: str | None = Field(default=None, alias="Kode HS", description="Pos tarif sebagaimana Pasal II PMK 50/2026.")
    komoditas: str | None = Field(default=None, alias="Komoditas", description="Kelompok barang yang disebut dalam Pasal II.")
    tarif_bea_masuk: float | None = Field(default=None, alias="Tarif Bea Masuk", description="Tarif bea masuk yang berlaku selama periode kebijakan.")
    masa_berlaku_tarif: str | None = Field(default=None, alias="Masa Berlaku Tarif", description="Durasi khusus yang ditetapkan regulasi.")
    konteks_kebijakan: str | None = Field(default=None, alias="Konteks Kebijakan", description="Tujuan kebijakan yang dijelaskan dalam pertimbangan regulasi.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Halaman bukti dalam PDF resmi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
