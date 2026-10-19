"""Data normalizer for UCDP Konflik Global (Peta Konflik Bersenjata Global)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import UcdpKonflikGlobalRecord, Record

logger = logging.getLogger(__name__)

TYPE_OF_VIOLENCE_MAP = {
    1: "State-based conflict (Pertempuran Terorganisir)",
    2: "Non-state conflict (Konflik Antar-Kelompok Bersenjata)",
    3: "One-sided violence (Kekerasan terhadap Sipil)",
    "1": "State-based conflict (Pertempuran Terorganisir)",
    "2": "Non-state conflict (Konflik Antar-Kelompok Bersenjata)",
    "3": "One-sided violence (Kekerasan terhadap Sipil)",
}


def parse_int_safe(val: Any) -> int:
    """Safely cast value to int."""
    if val is None:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "")
        return int(float(s)) if s else 0
    except (ValueError, TypeError):
        return 0


def parse_float_safe(val: Any) -> Optional[float]:
    """Safely cast value to float."""
    if val is None:
        return None
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(",", "")
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> UcdpKonflikGlobalRecord:
    """Convert raw UCDP GED dict into validated UcdpKonflikGlobalRecord."""
    id_konf = (
        clean_str(raw.get("id_konflik") or raw.get("ID Konflik") or raw.get("relid"))
        or (f"UCDP-{raw.get('id')}" if raw.get("id") else "UCDP-2026-000")
    )
    country = clean_str(raw.get("negara") or raw.get("Negara") or raw.get("country")) or "Global"
    region = clean_str(raw.get("kawasan") or raw.get("Kawasan") or raw.get("region")) or "Kawasan Konflik"

    # Actors
    aktor = clean_str(raw.get("aktor_terlibat") or raw.get("Aktor Bertikai") or raw.get("dyad_name"))
    if not aktor:
        side_a = clean_str(raw.get("side_a")) or "Pihak A"
        side_b = clean_str(raw.get("side_b")) or "Pihak B"
        aktor = f"{side_a} vs {side_b}"

    # Type of violence
    raw_type = raw.get("jenis_konflik") or raw.get("Jenis Konflik") or raw.get("type_of_violence")
    jenis = TYPE_OF_VIOLENCE_MAP.get(raw_type) or clean_str(raw_type) or "State-based conflict"

    # Date
    raw_date = raw.get("tanggal_kejadian") or raw.get("Tanggal") or raw.get("date_start")
    date_clean = None
    if raw_date:
        s_date = str(raw_date).strip()
        date_clean = s_date[:10] if len(s_date) >= 10 else s_date

    fatalities = parse_int_safe(
        raw.get("jumlah_korban_tewas")
        or raw.get("Korban Jiwa")
        or raw.get("best")
    )

    lat = parse_float_safe(raw.get("koordinat_lat") or raw.get("Lat") or raw.get("latitude"))
    lon = parse_float_safe(raw.get("koordinat_lon") or raw.get("Lon") or raw.get("longitude"))

    return UcdpKonflikGlobalRecord(
        id_konflik=id_konf,
        negara=country,
        kawasan=region,
        aktor_terlibat=aktor,
        jenis_konflik=jenis,
        tanggal_kejadian=date_clean,
        jumlah_korban_tewas=fatalities,
        koordinat_lat=lat,
        koordinat_lon=lon,
    )


class UcdpKonflikGlobalNormalizer(BaseNormalizer):
    """Maps raw UCDP GED payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for UCDP konflik global record: %s", exc)


Normalizer = UcdpKonflikGlobalNormalizer
