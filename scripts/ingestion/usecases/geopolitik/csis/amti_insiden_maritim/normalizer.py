"""Data normalizer for CSIS AMTI Insiden Maritim Indo-Pasifik."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import CsisAmtiInsidenMaritimRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def parse_float_safe(val: Any) -> float:
    """Parse float safely."""
    if val is None:
        return 0.0
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(",", "")
        return float(s) if s else 0.0
    except (ValueError, TypeError):
        return 0.0


def normalize_single(raw: Dict[str, Any]) -> CsisAmtiInsidenMaritimRecord:
    """Convert raw dict into validated CsisAmtiInsidenMaritimRecord."""
    id_insiden = (
        clean_str(raw.get("id_insiden") or raw.get("ID Insiden") or raw.get("id"))
        or "INS-AMTI-GEN-00"
    )
    tanggal = clean_str(raw.get("tanggal_kejadian") or raw.get("Tanggal") or raw.get("date"))
    wilayah = (
        clean_str(raw.get("wilayah_perairan") or raw.get("Wilayah Perairan") or raw.get("location"))
        or "Laut China Selatan"
    )
    jenis = (
        clean_str(raw.get("jenis_kejadian") or raw.get("Jenis Kejadian") or raw.get("incident_type"))
        or "Insiden Maritim"
    )
    pihak = (
        clean_str(raw.get("pihak_terlibat") or raw.get("Pihak Terlibat") or raw.get("parties"))
        or "Pihak Regional"
    )
    lat = parse_float_safe(raw.get("koordinat_lat") or raw.get("Lat") or raw.get("latitude"))
    lon = parse_float_safe(raw.get("koordinat_lon") or raw.get("Lon") or raw.get("longitude"))
    eskalasi = (
        clean_str(raw.get("tingkat_eskalasi") or raw.get("Eskalasi") or raw.get("severity"))
        or "Sedang"
    )
    catatan = clean_str(raw.get("catatan_analisis") or raw.get("Catatan Analisis") or raw.get("description"))

    return CsisAmtiInsidenMaritimRecord(
        id_insiden=id_insiden,
        tanggal_kejadian=tanggal,
        wilayah_perairan=wilayah,
        jenis_kejadian=jenis,
        pihak_terlibat=pihak,
        koordinat_lat=lat,
        koordinat_lon=lon,
        tingkat_eskalasi=eskalasi,
        catatan_analisis=catatan,
    )


class CsisAmtiInsidenMaritimNormalizer(BaseNormalizer):
    """Maps raw AMTI payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for CSIS AMTI record: %s", exc)


Normalizer = CsisAmtiInsidenMaritimNormalizer
