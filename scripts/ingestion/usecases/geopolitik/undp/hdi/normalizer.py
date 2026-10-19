"""Data normalizer for UNDP Human Development Index (HDI) time series."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import UndpHdiRecord, Record

logger = logging.getLogger(__name__)


def classify_hdi_tier(skor: float) -> str:
    """Classify country according to UNDP standard thresholds."""
    if skor >= 0.800:
        return "Very High Human Development"
    elif skor >= 0.700:
        return "High Human Development"
    elif skor >= 0.550:
        return "Medium Human Development"
    else:
        return "Low Human Development"


def parse_float_safe(val: Any) -> Optional[float]:
    """Parse float safely, handling empty strings and non-numeric values."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    try:
        return round(float(s), 4)
    except (ValueError, TypeError):
        return None


def parse_int_safe(val: Any) -> Optional[int]:
    """Parse integer safely."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def normalize_single(raw: Dict[str, Any]) -> UndpHdiRecord:
    """Convert raw UNDP CSV observation into a validated UndpHdiRecord."""
    negara = str(raw.get("negara") or raw.get("country") or "Unknown Country").strip()
    iso3 = str(raw.get("iso3") or "").strip().upper() or None
    tahun = parse_int_safe(raw.get("tahun") or raw.get("year")) or 2023

    skor = parse_float_safe(raw.get("skor_hdi") or raw.get("hdi")) or 0.0
    rank = parse_int_safe(raw.get("peringkat_hdi_dunia") or raw.get("hdi_rank") or raw.get("hdi_rank_2023"))
    le = parse_float_safe(raw.get("angka_harapan_hidup_tahun") or raw.get("le"))
    eys = parse_float_safe(raw.get("harapan_lama_sekolah_tahun") or raw.get("eys"))
    mys = parse_float_safe(raw.get("rata_rata_lama_sekolah_tahun") or raw.get("mys"))
    gni = parse_float_safe(raw.get("gni_per_kapita_ppp_usd") or raw.get("gnipc"))
    tier = raw.get("kategori_hdi") or classify_hdi_tier(skor)

    return UndpHdiRecord(
        tahun=tahun,
        negara=negara,
        iso3=iso3,
        skor_hdi=skor,
        peringkat_hdi_dunia=rank,
        angka_harapan_hidup_tahun=le,
        harapan_lama_sekolah_tahun=eys,
        rata_rata_lama_sekolah_tahun=mys,
        gni_per_kapita_ppp_usd=gni,
        kategori_hdi=tier,
    )


class UndpHdiNormalizer(BaseNormalizer):
    """Maps raw UNDP payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for UNDP HDI record: %s", exc)


Normalizer = UndpHdiNormalizer
