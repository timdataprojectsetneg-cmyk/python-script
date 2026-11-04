# Data Dictionary: 2 Energy Balance Table

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `2 Energy Balance Table`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Energy Balance](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=VqSYJx&nav=MTVfe0QxNzA4MjdFLTY4QTQtNEQ4RC05Mjk3LUIwOUM0MEE5MTFFRn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_balance_table/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Integer | Tahun | Tahun pengamatan neraca energi. |
| Energy Type | `energy_type` | String | - | Jenis energi yang menjadi kolom dalam energy balance, antara lain Hydro Power, Geothermal, Solar PP & Solar PV, Wind PP, Other Renewables, Industrial Biomass, Solar Water Heater, Direct Use of Geothermal, Traditional Biomass, Coal, Briquette, Natural Gas, Crude Oil, Oil Fuel, Biofuel, Biogas, LPG, Electricity, dan LNG. |
| Primary Energy Supply | `primary_energy_supply` | Numerik | Thousand BOE | Total primary energy supply berdasarkan jenis energi. |
| Production | `production` | Numerik | Thousand BOE | Produksi energi yang masuk ke neraca primary energy supply. |
| Import | `import` | Numerik | Thousand BOE | Energi yang berasal dari impor. |
| Export | `export` | Numerik | Thousand BOE | Energi yang diekspor. |
| International Marine Bunker | `international_marine_bunker` | Numerik | Thousand BOE | Energi yang digunakan sebagai international marine bunker. |
| Stock Change | `stock_change` | Numerik | Thousand BOE | Perubahan stok energi yang diperhitungkan dalam neraca. |
| Energy Transformation | `energy_transformation` | Numerik | Thousand BOE | Energi yang masuk atau keluar dari proses transformasi energi. |
| Refinery | `refinery` | Numerik | Thousand BOE | Energi yang digunakan atau dihasilkan melalui proses refinery. |
| Gas Processing | `gas_processing` | Numerik | Thousand BOE | Energi yang terkait dengan proses pengolahan gas. |
| LNG Regasification | `lng_regasification` | Numerik | Thousand BOE | Energi yang terkait dengan proses LNG regasification. |
| Coal Processing Plant | `coal_processing_plant` | Numerik | Thousand BOE | Energi yang digunakan atau dihasilkan pada coal processing plant. |
| Biofuel Blending | `biofuel_blending` | Numerik | Thousand BOE | Energi yang terkait dengan proses pencampuran biofuel. |
| Power Plant | `power_plant` | Numerik | Thousand BOE | Energi yang digunakan atau dihasilkan dalam pembangkitan listrik. |
| State Own Utility (PLN) | `state_own_utility_pln` | Numerik | Thousand BOE | Komponen energi untuk pembangkit milik PLN. |
| IPP, Captive Power, and PPU (Non-PLN) | `ipp_captive_power_and_ppu_non_pln` | Numerik | Thousand BOE | Komponen energi untuk IPP, captive power, dan PPU non-PLN. |
| IUPTLS + PPU | `iuptls_ppu` | Numerik | Thousand BOE | Komponen energi untuk IUPTLS dan PPU. |
| Own Use and Losses | `own_use_and_losses` | Numerik | Thousand BOE | Energi yang digunakan sendiri dan energi yang hilang dalam proses energi. |
| During Transformation | `during_transformation` | Numerik | Thousand BOE | Own use atau losses yang terjadi selama transformasi energi. |
| Energy Use / Own Use | `energy_use_own_use` | Numerik | Thousand BOE | Energi yang digunakan untuk kebutuhan sendiri. |
| Transmission & Distribution | `transmission_distribution` | Numerik | Thousand BOE | Energi yang terkait dengan losses pada transmisi dan distribusi. |
| Final Energy Supply | `final_energy_supply` | Numerik | Thousand BOE | Total final energy yang tersedia setelah proses transformasi dan komponen neraca lainnya. |
| Statistic Discrepancy | `statistic_discrepancy` | Numerik | Thousand BOE | Selisih statistik yang muncul dalam penyusunan neraca. |
| Final Consumption | `final_consumption` | Numerik | Thousand BOE | Total final consumption sebelum pemisahan menjadi final energy consumption dan non-energy use. |
| Final Energy Consumption | `final_energy_consumption` | Numerik | Thousand BOE | Konsumsi energi final setelah non-energy use dikeluarkan. |
| Industry | `industry` | Numerik | Thousand BOE | Konsumsi energi final sektor industri. |
| Transportation | `transportation` | Numerik | Thousand BOE | Konsumsi energi final sektor transportasi. |
| Household | `household` | Numerik | Thousand BOE | Konsumsi energi final sektor rumah tangga. |
| Commercial | `commercial` | Numerik | Thousand BOE | Konsumsi energi final sektor komersial. |
| Other Sector | `other_sector` | Numerik | Thousand BOE | Konsumsi energi final sektor lainnya. |
| Non Energy Use | `non_energy_use` | Numerik | Thousand BOE | Pemanfaatan energi untuk penggunaan non-energi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EnergyBalanceTableRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun pengamatan neraca energi.")
    energy_type: str | None = Field(default=None, alias="Energy Type", description="Jenis energi yang menjadi kolom dalam energy balance, antara lain Hydro Power, Geothermal, Solar PP & Solar PV, Wind PP, Other Renewables, Industrial Biomass, Solar Water Heater, Direct Use of Geothermal, Traditional Biomass, Coal, Briquette, Natural Gas, Crude Oil, Oil Fuel, Biofuel, Biogas, LPG, Electricity, dan LNG.")
    primary_energy_supply: str | None = Field(default=None, alias="Primary Energy Supply", description="Total primary energy supply berdasarkan jenis energi.")
    production: str | None = Field(default=None, alias="Production", description="Produksi energi yang masuk ke neraca primary energy supply.")
    import: str | None = Field(default=None, alias="Import", description="Energi yang berasal dari impor.")
    export: str | None = Field(default=None, alias="Export", description="Energi yang diekspor.")
    international_marine_bunker: str | None = Field(default=None, alias="International Marine Bunker", description="Energi yang digunakan sebagai international marine bunker.")
    stock_change: str | None = Field(default=None, alias="Stock Change", description="Perubahan stok energi yang diperhitungkan dalam neraca.")
    energy_transformation: str | None = Field(default=None, alias="Energy Transformation", description="Energi yang masuk atau keluar dari proses transformasi energi.")
    refinery: str | None = Field(default=None, alias="Refinery", description="Energi yang digunakan atau dihasilkan melalui proses refinery.")
    gas_processing: str | None = Field(default=None, alias="Gas Processing", description="Energi yang terkait dengan proses pengolahan gas.")
    lng_regasification: str | None = Field(default=None, alias="LNG Regasification", description="Energi yang terkait dengan proses LNG regasification.")
    coal_processing_plant: str | None = Field(default=None, alias="Coal Processing Plant", description="Energi yang digunakan atau dihasilkan pada coal processing plant.")
    biofuel_blending: str | None = Field(default=None, alias="Biofuel Blending", description="Energi yang terkait dengan proses pencampuran biofuel.")
    power_plant: str | None = Field(default=None, alias="Power Plant", description="Energi yang digunakan atau dihasilkan dalam pembangkitan listrik.")
    state_own_utility_pln: str | None = Field(default=None, alias="State Own Utility (PLN)", description="Komponen energi untuk pembangkit milik PLN.")
    ipp_captive_power_and_ppu_non_pln: str | None = Field(default=None, alias="IPP, Captive Power, and PPU (Non-PLN)", description="Komponen energi untuk IPP, captive power, dan PPU non-PLN.")
    iuptls_ppu: str | None = Field(default=None, alias="IUPTLS + PPU", description="Komponen energi untuk IUPTLS dan PPU.")
    own_use_and_losses: str | None = Field(default=None, alias="Own Use and Losses", description="Energi yang digunakan sendiri dan energi yang hilang dalam proses energi.")
    during_transformation: str | None = Field(default=None, alias="During Transformation", description="Own use atau losses yang terjadi selama transformasi energi.")
    energy_use_own_use: str | None = Field(default=None, alias="Energy Use / Own Use", description="Energi yang digunakan untuk kebutuhan sendiri.")
    transmission_distribution: str | None = Field(default=None, alias="Transmission & Distribution", description="Energi yang terkait dengan losses pada transmisi dan distribusi.")
    final_energy_supply: str | None = Field(default=None, alias="Final Energy Supply", description="Total final energy yang tersedia setelah proses transformasi dan komponen neraca lainnya.")
    statistic_discrepancy: str | None = Field(default=None, alias="Statistic Discrepancy", description="Selisih statistik yang muncul dalam penyusunan neraca.")
    final_consumption: str | None = Field(default=None, alias="Final Consumption", description="Total final consumption sebelum pemisahan menjadi final energy consumption dan non-energy use.")
    final_energy_consumption: str | None = Field(default=None, alias="Final Energy Consumption", description="Konsumsi energi final setelah non-energy use dikeluarkan.")
    industry: str | None = Field(default=None, alias="Industry", description="Konsumsi energi final sektor industri.")
    transportation: str | None = Field(default=None, alias="Transportation", description="Konsumsi energi final sektor transportasi.")
    household: str | None = Field(default=None, alias="Household", description="Konsumsi energi final sektor rumah tangga.")
    commercial: str | None = Field(default=None, alias="Commercial", description="Konsumsi energi final sektor komersial.")
    other_sector: str | None = Field(default=None, alias="Other Sector", description="Konsumsi energi final sektor lainnya.")
    non_energy_use: str | None = Field(default=None, alias="Non Energy Use", description="Pemanfaatan energi untuk penggunaan non-energi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
