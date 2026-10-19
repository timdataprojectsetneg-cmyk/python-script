"""Data normalizer for WIPO Global Innovation Index."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import WipoGlobalInnovationIndexRecord, Record

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


def normalize_single(raw: Dict[str, Any]) -> WipoGlobalInnovationIndexRecord:
    """Convert raw dict into validated WipoGlobalInnovationIndexRecord."""
    tahun = parse_int_safe(raw.get("tahun") or raw.get("Tahun") or raw.get("year")) or 2026
    skor_ri = parse_float_safe(raw.get("skor_gii_indonesia") or raw.get("Skor GII RI") or raw.get("score"))
    rank_world = parse_int_safe(raw.get("peringkat_gii_indonesia") or raw.get("Peringkat Dunia") or raw.get("rank"))
    rank_asean = parse_int_safe(raw.get("peringkat_asean") or raw.get("Peringkat ASEAN") or raw.get("asean_rank"))

    p_institusi = parse_float_safe(raw.get("pilar_institusi") or raw.get("Pilar Institusi") or raw.get("institutions"))
    p_human = parse_float_safe(raw.get("pilar_human_capital") or raw.get("Pilar SDM/Riset") or raw.get("human_capital"))
    p_infra = parse_float_safe(raw.get("pilar_infrastruktur") or raw.get("Pilar Infrastruktur") or raw.get("infrastructure"))
    p_market = parse_float_safe(raw.get("pilar_market_sophistication") or raw.get("Market Sophistication") or raw.get("market_sophistication"))
    p_biz = parse_float_safe(raw.get("pilar_business_sophistication") or raw.get("Business Sophistication") or raw.get("business_sophistication"))
    p_tech = parse_float_safe(raw.get("pilar_knowledge_technology") or raw.get("Knowledge & Tech") or raw.get("knowledge_technology"))
    p_creative = parse_float_safe(raw.get("pilar_creative_outputs") or raw.get("Creative Outputs") or raw.get("creative_outputs"))

    return WipoGlobalInnovationIndexRecord(
        tahun=tahun,
        skor_gii_indonesia=skor_ri,
        peringkat_gii_indonesia=rank_world,
        peringkat_asean=rank_asean,
        pilar_institusi=p_institusi,
        pilar_human_capital=p_human,
        pilar_infrastruktur=p_infra,
        pilar_market_sophistication=p_market,
        pilar_business_sophistication=p_biz,
        pilar_knowledge_technology=p_tech,
        pilar_creative_outputs=p_creative,
    )


class WipoGlobalInnovationIndexNormalizer(BaseNormalizer):
    """Maps raw GII payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for WIPO GII record: %s", exc)


Normalizer = WipoGlobalInnovationIndexNormalizer
