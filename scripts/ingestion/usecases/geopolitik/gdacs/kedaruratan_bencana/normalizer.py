"""Normalizer for GDACS Global Disaster Emergency Alerts."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
import logging
import re
from typing import Any, Dict, Iterator, Optional, Tuple
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)

EVENT_TYPE_MAP = {
    "EQ": "Gempa Bumi",
    "TC": "Siklon Tropis / Badai",
    "TS": "Tsunami & Gempa Laut",
    "FL": "Banjir Bandang",
    "VO": "Letusan Gunung Berapi",
    "WF": "Kebakaran Hutan & Lahan",
    "DR": "Kekeringan Ekstrem",
}


def parse_rfc_date(date_str: Optional[str]) -> str:
    """Parse RFC 822 date string to ISO YYYY-MM-DD."""
    if not date_str:
        return ""
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        # Fallback date extraction via regex YYYY-MM-DD or DD/MM/YYYY
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        if m:
            return m.group(0)
        return date_str[:10]


def parse_coordinates(point_str: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """Parse 'lat lon' coordinate string."""
    if not point_str:
        return (None, None)
    parts = point_str.strip().split()
    if len(parts) >= 2:
        try:
            return (float(parts[0]), float(parts[1]))
        except ValueError:
            pass
    return (None, None)


def parse_population(pop_str: Optional[str]) -> Optional[int]:
    """Parse human readable population strings (e.g. '0.823 million', '4 thousand')."""
    if not pop_str or pop_str.lower() in ("none", "[unknown]", "-"):
        return None
    # Check millions
    m_mil = re.search(r"([\d\.]+)\s*million", pop_str, re.IGNORECASE)
    if m_mil:
        return int(float(m_mil.group(1)) * 1_000_000)
    # Check thousands
    m_thou = re.search(r"([\d\.]+)\s*thousand", pop_str, re.IGNORECASE)
    if m_thou:
        return int(float(m_thou.group(1)) * 1_000)
    # Check raw digits
    m_dig = re.search(r"\b(\d+)\b", pop_str)
    if m_dig:
        return int(m_dig.group(1))
    return None


def evaluate_impact_on_indonesia(country: str, event_type: str, alert_level: str) -> str:
    """Analyze strategic impact and risks to Indonesian national interests."""
    c_lower = country.lower()
    t_upper = event_type.upper()
    a_lower = alert_level.lower()

    if any(k in c_lower for k in ["indonesia", "papua new guinea", "malaysia", "philippines", "timor"]):
        return "Kawasan Ring 1 Terdekat - Potensi imbas langsung gelombang seismik/cuaca ekstrem dan evakuasi WNI perbatasan"
    if t_upper in ("TC", "TS") and any(k in c_lower for k in ["indian ocean", "pacific", "south china sea", "vietnam"]):
        return "Potensi gelombang tinggi pada rute pelayaran kargo logistik ALKI / Selat Malaka dan keselamatan pelaut WNI"
    if "red" in a_lower:
        return "Kedaruratan Bencana Parah (Red Alert) - Prioritas pemantauan keselamatan WNI di wilayah terdampak & kesiapan misi kemanusiaan"
    return "Pemantauan rutin pusat situasi geopolitik dan kemanusiaan internasional"


class Normalizer(BaseNormalizer):
    """Maps raw GDACS RSS XML items to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                guid = str(raw.get("guid") or "").strip()
                title = str(raw.get("title") or "Peringatan Bencana Global").strip()
                ev_code = str(raw.get("eventtype") or "").strip().upper()
                cname = str(raw.get("country") or "Global").strip()
                raw_alert = str(raw.get("alertlevel") or "Green").strip().title()

                jenis = EVENT_TYPE_MAP.get(ev_code, f"Kedaruratan {ev_code}" if ev_code else "Kedaruratan Multi-Bahaya")
                level_waspada = f"{raw_alert} Alert"
                tgl = parse_rfc_date(raw.get("pubDate"))
                lat, lon = parse_coordinates(raw.get("point"))
                pop = parse_population(raw.get("population"))
                imbas = evaluate_impact_on_indonesia(cname, ev_code, raw_alert)

                norm_data = {
                    "id_peringatan": f"GDACS-{guid}" if not guid.startswith("GDACS") else guid,
                    "nama_kejadian": title,
                    "negara_kawasan": cname,
                    "jenis_kedaruratan": jenis,
                    "level_waspada": level_waspada,
                    "tanggal_kejadian": tgl if tgl else "2026-10-14",
                    "estimasi_korban_terdampak": pop,
                    "potensi_imbas_ke_indonesia": imbas,
                    "latitude": lat,
                    "longitude": lon,
                    "severity": raw.get("severity"),
                    "kode_event": ev_code,
                    "deskripsi": raw.get("description"),
                    "link_detail": raw.get("link"),
                    "data_source": "Global Disaster Alert and Coordination System (GDACS)",
                }

                yield Record(**norm_data).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for GDACS record: %s", exc)
            except Exception as exc:
                logger.warning("Unexpected normalization error for GDACS: %s", exc)
