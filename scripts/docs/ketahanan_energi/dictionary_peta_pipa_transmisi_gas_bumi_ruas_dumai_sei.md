# Data Dictionary: Gambar 29 Peta Pipa Transmisi Gas Bumi Ruas Dumai Sei Mangkei Medan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Gambar 29 Peta Pipa Transmisi Gas Bumi Ruas Dumai Sei Mangkei Medan`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Peta DUSEM](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=qHKhJF&nav=MTVfezYyOTg5N0U3LTZGNEEtNDYwNi1CQUZCLTUxNjM0MzZERTIwNn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/peta_pipa_transmisi_gas_bumi_ruas_dumai_sei/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| nama_pipa | `nama_pipa` | Text | - | Nama pipa transmisi pada judul slide: Pipa Transmisi Gas Bumi Dumai–Sei Mangkei–Medan (DUSEM) |
| titik_rute | `titik_rute` | Text (list) | - | Lokasi yang diberi label pada peta di sepanjang rute pipa |
| panjang_pipa | `panjang_pipa` | Numeric (Decimal) | km | Panjang perkiraan pipa, tertulis dengan tanda ± pada kotak keterangan peta |
| sumber_pasokan | `sumber_pasokan` | Text (list) | - | Sumber gas yang akan dialirkan menurut teks slide |
| peruntukan | `peruntukan` | Text (list) | - | Kebutuhan yang dilayani menurut teks slide |
| manfaat | `manfaat` | Text (list) | - | Manfaat pembangunan pipa yang dicantumkan slide (poin a–d) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PetaPipaTransmisiGasBumiRuasDumaiSeiRecord(BaseModel):
    nama_pipa: str | None = Field(default=None, alias="nama_pipa", description="Nama pipa transmisi pada judul slide: Pipa Transmisi Gas Bumi Dumai–Sei Mangkei–Medan (DUSEM)")
    titik_rute: str | None = Field(default=None, alias="titik_rute", description="Lokasi yang diberi label pada peta di sepanjang rute pipa")
    panjang_pipa: str | None = Field(default=None, alias="panjang_pipa", description="Panjang perkiraan pipa, tertulis dengan tanda ± pada kotak keterangan peta")
    sumber_pasokan: str | None = Field(default=None, alias="sumber_pasokan", description="Sumber gas yang akan dialirkan menurut teks slide")
    peruntukan: str | None = Field(default=None, alias="peruntukan", description="Kebutuhan yang dilayani menurut teks slide")
    manfaat: str | None = Field(default=None, alias="manfaat", description="Manfaat pembangunan pipa yang dicantumkan slide (poin a–d)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
