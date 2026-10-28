"""Pydantic schema mirroring the Data Dictionary for UKMTO Insiden Pelayaran."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UkmtoInsidenPelayaranRecord(BaseModel):
    incidentissuer: Optional[str] = Field(default=None, alias="incidentIssuer", description="Penerbit laporan (UKMTO).")
    incidentnumber: Optional[int] = Field(default=None, alias="incidentNumber", description="Nomor insiden tahunan.")
    sitecoreid: str = Field(alias="sitecoreId", description="ID unik record di CMS UKMTO (kunci dedup/upsert).")
    utcdatecreated: Optional[dt.datetime] = Field(default=None, alias="utcDateCreated", description="Waktu laporan dibuat (UTC).")
    utcdateofincident: Optional[dt.datetime] = Field(default=None, alias="utcDateOfIncident", description="Waktu kejadian (UTC).")
    pincolour: Optional[str] = Field(default=None, alias="pinColour", description="Warna penanda peta (Red / Yellow).")
    incidenttypename: Optional[str] = Field(default=None, alias="incidentTypeName", description="Jenis insiden (Attack, Suspicious Activity, Advisory, ...).")
    incidenttypelevel: Optional[int] = Field(default=None, alias="incidentTypeLevel", description="Kode numerik jenis insiden.")
    locationlatitude: Optional[float] = Field(default=None, alias="locationLatitude", description="Lintang kejadian (derajat desimal).")
    locationlongitude: Optional[float] = Field(default=None, alias="locationLongitude", description="Bujur kejadian (derajat desimal).")
    locationlatitudedddmmss: Optional[str] = Field(default=None, alias="locationLatitudeDDDMMSS", description="Lintang format DDMMSS + N/S.")
    locationlongitudedddmmss: Optional[str] = Field(default=None, alias="locationLongitudeDDDMMSS", description="Bujur format DDDMMSS + E/W.")
    region: Optional[str] = Field(default=None, alias="region", description="Kode wilayah UKMTO (IO = Indian Ocean).")
    place: Optional[str] = Field(default=None, alias="place", description="Nama perairan (Strait of Hormuz, Bab el Mandeb, dll).")
    vesselname: Optional[str] = Field(default=None, alias="vesselName", description="Nama kapal (umumnya disamarkan).")
    vesseltype: Optional[str] = Field(default=None, alias="vesselType", description="Jenis kapal (Tanker, Cargo, Tug, dll).")
    vesselunderpiratecontrol: Optional[bool] = Field(default=None, alias="vesselUnderPirateControl", description="True bila kapal dikuasai perompak.")
    datevesseltaken: Optional[dt.datetime] = Field(default=None, alias="dateVesselTaken", description="Tanggal kapal dikuasai (UTC), bila ada.")
    crewheld: Optional[int] = Field(default=None, alias="crewHeld", description="Jumlah awak yang ditahan.")
    otherdetails: Optional[str] = Field(default=None, alias="otherDetails", description="Narasi laporan insiden.")
    hidefromticker: Optional[bool] = Field(default=None, alias="hideFromTicker", description="Flag tampilan ticker situs UKMTO.")
    extendtickertime: Optional[bool] = Field(default=None, alias="extendTickerTime", description="Flag tampilan ticker situs UKMTO.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UkmtoInsidenPelayaranRecord
