"""Data normalizer for ESDM Indonesian Crude Price (ICP)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import EsdmHargaIcpRecord, Record

logger = logging.getLogger(__name__)


def parse_float_safe(val: Any) -> Optional[float]:
    """Parse float safely, handling Indonesian comma and dot decimal separators."""
    if val is None:
        return None
    s = str(val).strip().replace("US$", "").replace("$", "").replace("/bbl", "").strip()
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    # Handle Indonesian comma format '112,81' -> '112.81'
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        # e.g. '1,112.81' or '1.112,81'
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return round(float(s), 2)
    except (ValueError, TypeError):
        return None


def parse_int_safe(val: Any) -> Optional[int]:
    """Parse integer safely."""
    if val is None:
        return None
    s = str(val).strip()
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def normalize_single(raw: Dict[str, Any]) -> EsdmHargaIcpRecord:
    """Convert raw scraped dict into validated EsdmHargaIcpRecord."""
    tahun = parse_int_safe(raw.get("tahun")) or 2026
    bulan = str(raw.get("bulan") or "Unknown").strip().capitalize()
    periode = str(raw.get("periode_data") or f"{tahun}-{bulan}").strip()

    icp_val = parse_float_safe(raw.get("icp_usd"))
    if icp_val is None:
        icp_val = 0.0

    icp_delta = parse_float_safe(raw.get("icp_perubahan_usd"))
    brent = parse_float_safe(raw.get("brent_ice_usd"))
    wti = parse_float_safe(raw.get("wti_nymex_usd"))
    dated_brent = parse_float_safe(raw.get("dated_brent_usd"))
    basket_opec = parse_float_safe(raw.get("basket_opec_usd"))

    nomor_kepmen = str(raw.get("nomor_kepmen") or "").strip() or None
    faktor_geo = str(raw.get("faktor_geopolitik_pasar") or "").strip() or None
    sumber_url = str(raw.get("sumber_dokumen_url") or "").strip() or None

    return EsdmHargaIcpRecord(
        periode_data=periode,
        tahun=tahun,
        bulan=bulan,
        icp_usd=icp_val,
        icp_perubahan_usd=icp_delta,
        brent_ice_usd=brent,
        wti_nymex_usd=wti,
        dated_brent_usd=dated_brent,
        basket_opec_usd=basket_opec,
        nomor_kepmen=nomor_kepmen,
        faktor_geopolitik_pasar=faktor_geo,
        sumber_dokumen_url=sumber_url,
    )


class EsdmHargaIcpNormalizer(BaseNormalizer):
    """Maps raw ESDM ICP payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for ESDM ICP record: %s", exc)


Normalizer = EsdmHargaIcpNormalizer
