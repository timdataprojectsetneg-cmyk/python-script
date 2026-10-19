"""Normalizer for Kemenhub / BIG Airport Infrastructure records."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)


def parse_runway_length(dim_str: Optional[str], icao_class: Optional[str]) -> Optional[float]:
    """Parse runway length in meters from dimension string (e.g. '2500 x 45 m')."""
    if dim_str and dim_str.strip() not in ("-", "", "None"):
        match = re.search(r"(\d{3,5})", dim_str)
        if match:
            return float(match.group(1))
    
    # Fallback estimation based on ICAO classification if dimension is not stated
    if icao_class:
        cls_code = icao_class.strip().upper()
        if "4E" in cls_code or "4F" in cls_code:
            return 3000.0
        elif "4D" in cls_code or "4C" in cls_code:
            return 2400.0
        elif "3C" in cls_code:
            return 1600.0
        elif "2B" in cls_code or "2C" in cls_code:
            return 1200.0
        elif "1A" in cls_code:
            return 800.0

    return None


def determine_vvip_readiness(aircraft_type: Optional[str], runway_m: Optional[float], icao_class: Optional[str]) -> str:
    """Evaluate VVIP readiness for Presidential / State visits."""
    text = f"{aircraft_type or ''} {icao_class or ''}".upper()

    if any(k in text for k in ["B-777", "B777", "A330", "A350", "B-747", "B747", "4E", "4F"]):
        return "Layak Penuh Pesawat Kenegaraan VVIP (Wide Body / BBJ)"
    if any(k in text for k in ["B-737", "B737", "A320", "A321", "BBJ", "4C", "4D"]):
        return "Layak Pesawat Kepresidenan BBJ (Narrow Body)"
    if any(k in text for k in ["C-130", "HERCULES", "CN-295", "C295", "ATR", "F-50", "3C"]):
        return "Layak Pesawat Taktis VVIP (TNI AU C-130 / CN-295)"

    if runway_m:
        if runway_m >= 2500:
            return "Layak Penuh Pesawat Kenegaraan VVIP (Wide Body / BBJ)"
        elif runway_m >= 1800:
            return "Layak Pesawat Kepresidenan BBJ (Narrow Body)"
        elif runway_m >= 1400:
            return "Layak Pesawat Taktis VVIP (TNI AU C-130 / CN-295)"

    return "Terbatas Pesawat Ringan / Akses Helikopter VVIP"


def clean_name(name_raw: Optional[str]) -> str:
    """Format airport name cleanly."""
    if not name_raw:
        return "Bandara Tidak Bernama"
    cleaned = name_raw.strip().title()
    if not cleaned.lower().startswith("bandara") and not cleaned.lower().startswith("bandar udara") and not cleaned.lower().startswith("lanud"):
        cleaned = f"Bandara {cleaned}"
    return cleaned


class Normalizer(BaseNormalizer):
    """Maps raw ArcGIS bandara features to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                # Handle raw attribute dict directly or attributes wrapper
                attr = raw.get("attributes", raw)
                geometry = raw.get("geometry", {})

                icao = str(attr.get("kdicao") or "").strip().upper()
                iata = str(attr.get("kdiata") or "").strip().upper()
                if icao and icao != "-" and iata and iata != "-":
                    id_fasilitas = f"{icao} / {iata}"
                elif icao and icao != "-":
                    id_fasilitas = icao
                elif iata and iata != "-":
                    id_fasilitas = iata
                else:
                    id_fasilitas = f"BDG-{attr.get('objectid', 'NA')}"

                raw_name = attr.get("namobj") or ""
                nama_fasilitas = clean_name(raw_name)

                icao_class = str(attr.get("klsfks") or "").strip()
                if icao_class == "-":
                    icao_class = None

                pcn = str(attr.get("pcnaip") or "").strip()
                if pcn == "-":
                    pcn = None

                psw_kritis = str(attr.get("jnspsw") or "").strip()
                if psw_kritis == "-":
                    psw_kritis = "ATR-72 / CN-295"

                runway_m = parse_runway_length(attr.get("dmnsrw"), icao_class)
                status_vvip = determine_vvip_readiness(psw_kritis, runway_m, icao_class)

                # Coordinates from lat/lon or geometry
                lat_val = attr.get("lat")
                if lat_val is None and geometry:
                    lat_val = geometry.get("y")
                lon_val = attr.get("lon")
                if lon_val is None and geometry:
                    lon_val = geometry.get("x")

                elev_val = attr.get("elevas")
                if elev_val is not None:
                    try:
                        elev_val = float(elev_val)
                    except (ValueError, TypeError):
                        elev_val = None

                norm_data = {
                    "id_fasilitas": id_fasilitas,
                    "nama_fasilitas": nama_fasilitas,
                    "jenis_infrastruktur": "Bandar Udara Sipil / Komersial",
                    "panjang_runway_m": runway_m,
                    "klasifikasi_pesawat_maks": psw_kritis,
                    "kondisi_kemantapan_jalan_pct": 100.0,
                    "status_kelayakan_vvip": status_vvip,
                    "kode_icao": icao if icao != "-" else None,
                    "kode_iata": iata if iata != "-" else None,
                    "klasifikasi_icao": icao_class,
                    "kekuatan_pcn": pcn,
                    "pengelola": attr.get("adabmi") if attr.get("adabmi") != "-" else None,
                    "alamat": attr.get("adrbmi") if attr.get("adrbmi") != "-" else None,
                    "jam_operasional": attr.get("jamopr") if attr.get("jamopr") != "-" else None,
                    "kabupaten_kota": attr.get("wadmkk") if attr.get("wadmkk") != "-" else None,
                    "latitude": float(lat_val) if lat_val is not None else None,
                    "longitude": float(lon_val) if lon_val is not None else None,
                    "elevasi_mdpl": elev_val,
                    "data_source": "Ditjen Hubud Kemenhub & BIG Satupeta",
                }

                yield Record(**norm_data).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for Bandara record: %s", exc)
            except Exception as exc:
                logger.warning("Unexpected normalization error for Bandara: %s", exc)
