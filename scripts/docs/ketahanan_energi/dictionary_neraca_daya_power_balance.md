# Data Dictionary: PLN - Statistik PLN 2025 - Table 1 : Neraca Daya / Power Balance

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PLN - Statistik PLN 2025 - Table 1 : Neraca Daya / Power Balance`
- Publisher: pln
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Daya Mampu vs Beban Puncak](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=d9b09E&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wNDAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/neraca_daya_power_balance/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Infrastruktur | `infrastruktur` | String | - | Kelompok infrastruktur: Pembangkit, Transmisi, Gardu Induk, atau Distribusi |
| Jenis | `jenis` | String | - | Sub-jenis infrastruktur, misalnya PLTU, PLTS, 500 kV, 150/115/70/20 kV, atau JTM |
| RUPTL_Sebelumnya | `ruptl_sebelumnya` | Numeric | MW / kms / MVA (sesuai kolom Satuan) | Kapasitas pada RUPTL 2021-2030 |
| Usulan_Perubahan | `usulan_perubahan` | Numeric | MW / kms / MVA (sesuai kolom Satuan) | Kapasitas pada RUPTL 2025-2034 skenario ARED, dipakai sebagai target kapasitas |
| Selisih | `selisih` | Numeric | MW / kms / MVA (sesuai kolom Satuan) | Usulan_Perubahan dikurangi RUPTL_Sebelumnya. Nilai negatif berarti kapasitas direncanakan turun |
| Satuan | `satuan` | String | - | MW (pembangkit), kms (transmisi), MVA (gardu induk). Distribusi: kms untuk JTM dan JTR, MVA untuk trafo distribusi (perlu diverifikasi ke teks bab) |
| Skenario | `skenario` | String | - | Skenario perencanaan sumber data (ARED) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class NeracaDayaPowerBalanceRecord(BaseModel):
    infrastruktur: str | None = Field(default=None, alias="Infrastruktur", description="Kelompok infrastruktur: Pembangkit, Transmisi, Gardu Induk, atau Distribusi")
    jenis: str | None = Field(default=None, alias="Jenis", description="Sub-jenis infrastruktur, misalnya PLTU, PLTS, 500 kV, 150/115/70/20 kV, atau JTM")
    ruptl_sebelumnya: str | None = Field(default=None, alias="RUPTL_Sebelumnya", description="Kapasitas pada RUPTL 2021-2030")
    usulan_perubahan: str | None = Field(default=None, alias="Usulan_Perubahan", description="Kapasitas pada RUPTL 2025-2034 skenario ARED, dipakai sebagai target kapasitas")
    selisih: str | None = Field(default=None, alias="Selisih", description="Usulan_Perubahan dikurangi RUPTL_Sebelumnya. Nilai negatif berarti kapasitas direncanakan turun")
    satuan: str | None = Field(default=None, alias="Satuan", description="MW (pembangkit), kms (transmisi), MVA (gardu induk). Distribusi: kms untuk JTM dan JTR, MVA untuk trafo distribusi (perlu diverifikasi ke teks bab)")
    skenario: str | None = Field(default=None, alias="Skenario", description="Skenario perencanaan sumber data (ARED)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
