"""Pydantic schema mirroring the Data Dictionary for Airport Infrastructure."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HubudBandaraRecord(BaseModel):
    id_fasilitas: str = Field(
        description="Kode ICAO/IATA bandar udara atau ID fasilitas (misal: WIHH / HLP)."
    )
    nama_fasilitas: str = Field(
        description="Nama resmi bandar udara atau pangkalan udara."
    )
    jenis_infrastruktur: str = Field(
        default="Bandar Udara Sipil / Komersial",
        description="Klasifikasi jenis bandara (Komersial, Militer/Pangkalan TNI AU, Enclave Sipil)."
    )
    panjang_runway_m: Optional[float] = Field(
        default=None,
        description="Panjang landasan pacu utama bandara dalam satuan meter."
    )
    klasifikasi_pesawat_maks: Optional[str] = Field(
        default="ATR-72 / CN-295",
        description="Tipe pesawat terbesar/kritis yang dapat dilayani landasan pacu."
    )
    kondisi_kemantapan_jalan_pct: Optional[float] = Field(
        default=100.0,
        description="Tingkat kemantapan dan kesiapan operasional perkerasan landasan (%)"
    )
    status_kelayakan_vvip: str = Field(
        default="Layak Operasional",
        description="Rekomendasi teknis kesiapan protokoler/VVIP kepresidenan."
    )
    kode_icao: Optional[str] = Field(
        default=None,
        description="Kode 4 huruf International Civil Aviation Organization."
    )
    kode_iata: Optional[str] = Field(
        default=None,
        description="Kode 3 huruf International Air Transport Association."
    )
    klasifikasi_icao: Optional[str] = Field(
        default=None,
        description="Klasifikasi Aerodrome Reference Code ICAO (misal: 3C, 4D, 4E, 4F)."
    )
    kekuatan_pcn: Optional[str] = Field(
        default=None,
        description="Pavement Classification Number (PCN) kekuatan perkerasan landasan."
    )
    pengelola: Optional[str] = Field(
        default=None,
        description="Instansi / BUMN pengelola bandara (UPBU Kemenhub, PT Angkasa Pura, TNI AU)."
    )
    alamat: Optional[str] = Field(
        default=None,
        description="Alamat fisik lokasi bandara."
    )
    jam_operasional: Optional[str] = Field(
        default=None,
        description="Jam operasional penerbangan (misal: 24 Jam, 06.00-18.00 LT)."
    )
    kabupaten_kota: Optional[str] = Field(
        default=None,
        description="Wilayah administratif kabupaten/kota kedudukan bandara."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Koordinat lintang geografis."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Koordinat bujur geografis."
    )
    elevasi_mdpl: Optional[float] = Field(
        default=None,
        description="Ketinggian bandara di atas permukaan laut (meter)."
    )
    data_source: str = Field(
        default="Ditjen Hubud Kemenhub & BIG Satupeta",
        description="Sumber data resmi."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = HubudBandaraRecord
