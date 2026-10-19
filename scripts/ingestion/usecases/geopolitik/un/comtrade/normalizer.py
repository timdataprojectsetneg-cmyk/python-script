"""Data normalizer for UN Comtrade."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import UnComtradeRecord, Record

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
            return round(float(val), 2)
        s = str(val).strip().replace(",", "").replace("%", "")
        return round(float(s), 2) if s else 0.0
    except (ValueError, TypeError):
        return 0.0


def normalize_single(raw: Dict[str, Any]) -> UnComtradeRecord:
    """Convert raw dict into validated UnComtradeRecord."""
    periode = clean_str(
        raw.get("periode_bulan")
        or raw.get("Periode")
        or raw.get("period")
        or raw.get("year")
    ) or "2026-08"

    hs = clean_str(
        raw.get("kode_hs_2digit")
        or raw.get("HS Code")
        or raw.get("cmdCode")
        or raw.get("hs")
    ) or "00"

    komoditas = clean_str(
        raw.get("deskripsi_komoditas")
        or raw.get("Komoditas Strategis")
        or raw.get("cmdDesc")
        or raw.get("commodity")
    ) or "Komoditas Strategis Nasional"

    arus = clean_str(
        raw.get("arus_perdagangan")
        or raw.get("Arus Dagang")
        or raw.get("flowDesc")
        or raw.get("flow")
    ) or "Ekspor"

    mitra = clean_str(
        raw.get("negara_mitra_utama")
        or raw.get("Negara Mitra")
        or raw.get("partnerDesc")
        or raw.get("partner")
    ) or "Dunia"

    volume = parse_float_safe(
        raw.get("volume_ribu_ton")
        or raw.get("Volume (Ribu Ton)")
        or raw.get("netWgt")
        or raw.get("volume")
    )

    nilai = parse_float_safe(
        raw.get("nilai_fob_cif_juta_usd")
        or raw.get("Nilai (Juta USD)")
        or raw.get("primaryValue")
        or raw.get("trade_value")
    )

    pertumbuhan = parse_float_safe(
        raw.get("pertumbuhan_tahunan_pct")
        or raw.get("Pertumbuhan (%)")
        or raw.get("growth")
    )

    data_src = clean_str(raw.get("data_source")) or "Badan Pusat Statistik (BPS) & UN Comtrade"

    return UnComtradeRecord(
        periode_bulan=periode,
        kode_hs_2digit=hs,
        deskripsi_komoditas=komoditas,
        arus_perdagangan=arus,
        negara_mitra_utama=mitra,
        volume_ribu_ton=volume,
        nilai_fob_cif_juta_usd=nilai,
        pertumbuhan_tahunan_pct=pertumbuhan,
        data_source=data_src,
    )


class UnComtradeNormalizer(BaseNormalizer):
    """Maps raw UN Comtrade trade payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for UN Comtrade record: %s", exc)


Normalizer = UnComtradeNormalizer
