# Data Dictionary: Gambar 25 Peta Rencana Induk Jaringan Transmisi dan Distribusi gas Bumi 
Nasional (RIJTDGBN) 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Gambar 25 Peta Rencana Induk Jaringan Transmisi dan Distribusi gas Bumi 
Nasional (RIJTDGBN) `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Peta RIJTDGBN](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=3BI1kc&nav=MTVfe0U1NkJEMkM3LTcyMjMtNDU4Mi05N0QwLTAxNTRFQjIzOTA4NX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/peta_rencana_induk_jaringan_transmisi_dan_distribusi_gas_bumi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| kategori_infrastruktur | `kategori_infrastruktur` | Categorical | - | Jenis infrastruktur pada legenda: Pipa Transmisi, Pipa Distribusi, Pipa Kepentingan Sendiri, FSRU/FRU/FSU, Kilang LNG, Fasilitas CNG, Terminal Penerima LNG Onshore, Wilayah Jaringan Distribusi, Jargas Rumah Tangga |
| status_pembangunan | `status_pembangunan` | Categorical | - | Eksisting / Ongoing / Rencana, sesuai warna dan gaya garis pada legenda. Wilayah Jaringan Distribusi tidak punya status pada legenda |
| tipe_geometri | `tipe_geometri` | Categorical | - | Garis (pipa), Titik (fasilitas, terminal, kilang, FSRU, CNG), atau Poligon (wilayah jaringan, jargas). Diturunkan dari simbol legenda, jadi perlu dicek ke data GIS asli |
| simbol_legenda | `simbol_legenda` | Text | - | Deskripsi tampilan simbol pada legenda (warna, gaya garis/ikon) untuk tiap kategori dan status |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PetaRencanaIndukJaringanTransmisiDanDistribusiGasBumiRecord(BaseModel):
    kategori_infrastruktur: str | None = Field(default=None, alias="kategori_infrastruktur", description="Jenis infrastruktur pada legenda: Pipa Transmisi, Pipa Distribusi, Pipa Kepentingan Sendiri, FSRU/FRU/FSU, Kilang LNG, Fasilitas CNG, Terminal Penerima LNG Onshore, Wilayah Jaringan Distribusi, Jargas Rumah Tangga")
    status_pembangunan: str | None = Field(default=None, alias="status_pembangunan", description="Eksisting / Ongoing / Rencana, sesuai warna dan gaya garis pada legenda. Wilayah Jaringan Distribusi tidak punya status pada legenda")
    tipe_geometri: str | None = Field(default=None, alias="tipe_geometri", description="Garis (pipa), Titik (fasilitas, terminal, kilang, FSRU, CNG), atau Poligon (wilayah jaringan, jargas). Diturunkan dari simbol legenda, jadi perlu dicek ke data GIS asli")
    simbol_legenda: str | None = Field(default=None, alias="simbol_legenda", description="Deskripsi tampilan simbol pada legenda (warna, gaya garis/ikon) untuk tiap kategori dan status")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
