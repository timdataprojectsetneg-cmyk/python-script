"""Data normalizer for Kemenkop SIMKOPDES (Koperasi Desa Merah Putih)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemenkopSimkopdesKdmpRecord, Record

logger = logging.getLogger(__name__)


def parse_int_safe(val: Any) -> int:
    """Convert value to int safely, defaulting to 0."""
    if val is None:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "").replace(".", "")
        return int(s) if s else 0
    except (ValueError, TypeError):
        return 0


def parse_float_safe(val: Any) -> Optional[float]:
    """Convert value to float safely."""
    if val is None:
        return None
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(",", "")
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def clean_text(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> KemenkopSimkopdesKdmpRecord:
    """Convert raw payload into validated KemenkopSimkopdesKdmpRecord."""
    prov = clean_text(raw.get("provinsi") or raw.get("Provinsi") or raw.get("province_name")) or "INDONESIA"
    prov_id = parse_int_safe(raw.get("provinsi_id") or raw.get("ID Prov") or raw.get("province_id")) or None

    kab = clean_text(
        raw.get("kabupaten_kota")
        or raw.get("Kabupaten/Kota")
        or raw.get("city_name")
        or raw.get("kabupaten")
    ) or "Wilayah Sentra Koperasi"

    tot_kop = parse_int_safe(raw.get("total_koperasi") or raw.get("Total Koperasi") or raw.get("total_cooperatives"))
    sehat = parse_int_safe(raw.get("koperasi_sehat") or raw.get("Sehat"))
    cukup = parse_int_safe(raw.get("koperasi_cukup_sehat") or raw.get("Cukup Sehat"))
    tdk_sehat = parse_int_safe(raw.get("koperasi_tidak_sehat") or raw.get("Tidak Sehat"))

    anggota = parse_int_safe(raw.get("total_anggota") or raw.get("Anggota") or raw.get("total_members"))
    omzet = parse_float_safe(raw.get("omzet_pendapatan") or raw.get("Omzet (Rp)") or raw.get("total_transaction")) or 0.0

    lat = parse_float_safe(raw.get("latitude") or raw.get("Lat") or raw.get("lat"))
    lon = parse_float_safe(raw.get("longitude") or raw.get("Lon") or raw.get("lon"))

    return KemenkopSimkopdesKdmpRecord(
        provinsi=prov,
        provinsi_id=prov_id,
        kabupaten_kota=kab,
        total_koperasi=tot_kop,
        koperasi_sehat=sehat,
        koperasi_cukup_sehat=cukup,
        koperasi_tidak_sehat=tdk_sehat,
        total_anggota=anggota,
        omzet_pendapatan=omzet,
        latitude=lat,
        longitude=lon,
    )


class KemenkopSimkopdesKdmpNormalizer(BaseNormalizer):
    """Maps raw SIMKOPDES payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for SIMKOPDES KDMP record: %s", exc)


Normalizer = KemenkopSimkopdesKdmpNormalizer
