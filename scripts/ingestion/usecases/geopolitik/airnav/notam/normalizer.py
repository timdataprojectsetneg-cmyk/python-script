"""Data normalizer for AirNav NOTAM & Kesiapan Evakuasi WNI."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import AirNavNotamRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def parse_int_safe(val: Any) -> int:
    """Parse int safely."""
    if val is None:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "")
        return int(float(s)) if s else 0
    except (ValueError, TypeError):
        return 0


def normalize_single(raw: Dict[str, Any]) -> AirNavNotamRecord:
    """Convert raw dict into validated AirNavNotamRecord."""
    id_wil = clean_str(raw.get("id_wilayah") or raw.get("ID Wilayah")) or "EVAC-2026-GEN-00"
    neg = clean_str(raw.get("negara") or raw.get("Negara") or raw.get("country")) or "Zona Kontinjensi"
    kaw = clean_str(raw.get("kawasan") or raw.get("Kawasan") or raw.get("region")) or "Kawasan Internasional"
    siaga = clean_str(raw.get("status_siaga_evakuasi") or raw.get("Status Siaga") or raw.get("status")) or "Siaga I"

    wni = parse_int_safe(raw.get("estimasi_wni_terdampak") or raw.get("WNI Terdampak") or raw.get("wni"))
    jalur = clean_str(raw.get("jalur_evakuasi_utama") or raw.get("Jalur Evakuasi"))
    titik = clean_str(raw.get("titik_kumpul_safe_haven") or raw.get("Titik Kumpul Safe Haven") or raw.get("safe_haven"))
    notam_status = clean_str(raw.get("status_ruang_udara_notam") or raw.get("Status Udara (NOTAM)") or raw.get("notam")) or "Restricted"
    bandara = clean_str(raw.get("kesiapan_bandara_pelabuhan") or raw.get("Kesiapan Bandara"))
    satgas = clean_str(raw.get("koordinasi_satgas_tni_kemlu") or raw.get("Koordinasi Satgas TNI/Kemlu") or raw.get("satgas"))

    return AirNavNotamRecord(
        id_wilayah=id_wil,
        negara=neg,
        kawasan=kaw,
        status_siaga_evakuasi=siaga,
        estimasi_wni_terdampak=wni,
        jalur_evakuasi_utama=jalur,
        titik_kumpul_safe_haven=titik,
        status_ruang_udara_notam=notam_status,
        kesiapan_bandara_pelabuhan=bandara,
        koordinasi_satgas_tni_kemlu=satgas,
    )


class AirNavNotamNormalizer(BaseNormalizer):
    """Maps raw NOTAM payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for AirNav NOTAM record: %s", exc)


Normalizer = AirNavNotamNormalizer
