# Data Dictionary: PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Perubahan RUPTL 2025 – 2034 Skenario ARED](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=frjGAS&nav=MTVfe0UyOEY1NENGLTdEOTEtNDcxRC1BNkIwLUVDNTExRDI4NkNERn0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/skenario_ared_terhadap_ruptl_2021_2030_indonesia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| no | `no` | integer | - | Nomor urut baris |
| kategori | `kategori` | string | - | Kategori infrastruktur: Pembangkit, Transmisi, Gardu Induk, atau Distribusi |
| jenis | `jenis` | string | - | Jenis pembangkit (PLTU, PLTP, BESS, dll.), level tegangan transmisi atau gardu induk, atau jenis distribusi (JTM, JTR, Trafo Distribusi) |
| satuan | `satuan` | string | - | Satuan: MW (Pembangkit), kms (Transmisi, JTM, JTR), MVA (Gardu Induk, Trafo Distribusi) |
| ruptl_sebelumnya | `ruptl_sebelumnya` | integer | Sesuai kolom satuan | Nilai pada RUPTL 2021-2030. Null jika di sumber tertulis "-" |
| usulan_perubahan | `usulan_perubahan` | integer | Sesuai kolom satuan | Nilai usulan perubahan pada RUPTL 2025-2034 Skenario ARED. Null jika "-" |
| selisih | `selisih` | integer | Sesuai kolom satuan | Selisih usulan perubahan terhadap RUPTL sebelumnya. Negatif untuk nilai berkurung. Null jika "-" |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class SkenarioAredTerhadapRuptl20212030IndonesiaRecord(BaseModel):
    no: int | None = Field(default=None, alias="no", description="Nomor urut baris")
    kategori: str | None = Field(default=None, alias="kategori", description="Kategori infrastruktur: Pembangkit, Transmisi, Gardu Induk, atau Distribusi")
    jenis: str | None = Field(default=None, alias="jenis", description="Jenis pembangkit (PLTU, PLTP, BESS, dll.), level tegangan transmisi atau gardu induk, atau jenis distribusi (JTM, JTR, Trafo Distribusi)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan: MW (Pembangkit), kms (Transmisi, JTM, JTR), MVA (Gardu Induk, Trafo Distribusi)")
    ruptl_sebelumnya: int | None = Field(default=None, alias="ruptl_sebelumnya", description="Nilai pada RUPTL 2021-2030. Null jika di sumber tertulis \"-\"")
    usulan_perubahan: int | None = Field(default=None, alias="usulan_perubahan", description="Nilai usulan perubahan pada RUPTL 2025-2034 Skenario ARED. Null jika \"-\"")
    selisih: int | None = Field(default=None, alias="selisih", description="Selisih usulan perubahan terhadap RUPTL sebelumnya. Negatif untuk nilai berkurung. Null jika \"-\"")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
