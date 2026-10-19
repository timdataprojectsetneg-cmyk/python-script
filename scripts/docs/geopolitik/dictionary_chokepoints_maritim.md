# Data Dictionary: IMF PortWatch Daily Chokepoints

> Generated from Data Dictionary - Geopolitik - Situasi Global dan Kawasan.xlsx (sheet Lalu Lintas Chokepoint). Reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Publisher: `imf`
- Source: `chokepoints_maritim`
- Data access: `api`
- Update frequency: Harian
- Eligible: `True`
- Endpoint URL: `https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query`
- Target module: `ingestion/usecases/geopolitik/imf/chokepoints_maritim/models.py`
- Target schema / table: `raw_geopolitik.raw_imf_chokepoints`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| date | `date` | Date / String | Tanggal | Tanggal observasi harian lalu lintas titik sempit (format YYYY-MM-DD). |
| year | `year` | Integer | Tahun | Tahun observasi kalender. |
| month | `month` | Integer | Bulan | Bulan observasi kalender (1-12). |
| day | `day` | Integer | Hari | Hari observasi kalender (1-31). |
| portid | `portid` | String | ID | Identifier unik chokepoint PortWatch (misal: chokepoint1, chokepoint5). |
| portname | `portname` | String | - | Nama resmi chokepoint (misal: Suez Canal, Malacca Strait, Bab el-Mandeb). |
| n_container | `n_container` | Integer | Lintasan kapal | Jumlah lintasan kapal pengangkut kontainer. |
| n_dry_bulk | `n_dry_bulk` | Integer | Lintasan kapal | Jumlah lintasan kapal pembawa muatan curah kering (batu bara, bijih, gandum). |
| n_general_cargo | `n_general_cargo` | Integer | Lintasan kapal | Jumlah lintasan kapal kargo umum. |
| n_roro | `n_roro` | Integer | Lintasan kapal | Jumlah lintasan kapal roll-on/roll-off (kendaraan). |
| n_tanker | `n_tanker` | Integer | Lintasan kapal | Jumlah lintasan kapal tangki pengangkut minyak mentah, BBM, dan LNG/LPG. |
| n_cargo | `n_cargo` | Integer | Lintasan kapal | Akumulasi seluruh kategori kapal pengangkut kargo barang. |
| n_total | `n_total` | Integer | Lintasan kapal | Total seluruh lintasan kapal komersial yang melewati chokepoint pada hari tersebut. |
| capacity_container | `capacity_container` | Float | TEU | Total kapasitas muatan kontainer kapal yang melintas (Twenty-foot Equivalent Unit). |
| capacity_dry_bulk | `capacity_dry_bulk` | Float | DWT | Total kapasitas tonase muatan curah kering (Deadweight Tonnage). |
| capacity_general_cargo | `capacity_general_cargo` | Float | DWT | Total kapasitas tonase muatan kargo umum. |
| capacity_roro | `capacity_roro` | Float | DWT | Total kapasitas tonase kapal ro-ro. |
| capacity_tanker | `capacity_tanker` | Float | DWT | Total kapasitas tonase minyak/gas tanker yang melintas. |
| capacity_cargo | `capacity_cargo` | Float | DWT | Akumulasi kapasitas tonase seluruh kapal kargo. |
| capacity | `capacity` | Float | DWT | Total akumulasi kapasitas muatan seluruh kapal yang melintas. |
| ObjectId | `object_id` | Integer | ID | Identifier internal objek unik pada FeatureServer ArcGIS. |

## Pydantic Model

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ChokepointsMaritimRecord(BaseModel):
    date: str = Field(description="Tanggal observasi harian (format YYYY-MM-DD).")
    year: Optional[int] = Field(default=None, description="Tahun observasi.")
    month: Optional[int] = Field(default=None, description="Bulan observasi.")
    day: Optional[int] = Field(default=None, description="Hari observasi.")
    portid: str = Field(description="ID unik chokepoint PortWatch.")
    portname: str = Field(description="Nama chokepoint.")
    n_container: Optional[int] = Field(default=0, description="Jumlah lintasan kapal kontainer.")
    n_dry_bulk: Optional[int] = Field(default=0, description="Jumlah lintasan kapal dry bulk.")
    n_general_cargo: Optional[int] = Field(default=0, description="Jumlah lintasan kapal general cargo.")
    n_roro: Optional[int] = Field(default=0, description="Jumlah lintasan kapal ro-ro.")
    n_tanker: Optional[int] = Field(default=0, description="Jumlah lintasan kapal tanker minyak/gas.")
    n_cargo: Optional[int] = Field(default=0, description="Jumlah lintasan seluruh kapal kargo.")
    n_total: Optional[int] = Field(default=0, description="Total seluruh lintasan kapal.")
    capacity_container: Optional[float] = Field(default=None, description="Kapasitas kontainer (TEU).")
    capacity_dry_bulk: Optional[float] = Field(default=None, description="Kapasitas dry bulk (DWT).")
    capacity_general_cargo: Optional[float] = Field(default=None, description="Kapasitas general cargo (DWT).")
    capacity_roro: Optional[float] = Field(default=None, description="Kapasitas ro-ro.")
    capacity_tanker: Optional[float] = Field(default=None, description="Kapasitas tanker (DWT).")
    capacity_cargo: Optional[float] = Field(default=None, description="Kapasitas kargo total.")
    capacity: Optional[float] = Field(default=None, description="Kapasitas total.")
    object_id: Optional[int] = Field(default=None, alias="ObjectId", description="ID internal objek ArcGIS.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

Record = ChokepointsMaritimRecord
```
