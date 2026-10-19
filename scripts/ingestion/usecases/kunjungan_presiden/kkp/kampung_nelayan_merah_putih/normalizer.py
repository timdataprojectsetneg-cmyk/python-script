"""Data normalizer for KKP Kampung Nelayan Merah Putih (KNMP)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KkpKampungNelayanRecord, Record

logger = logging.getLogger(__name__)


def parse_float_safe(val: Any) -> Optional[float]:
    """Parse float safely, handling Indonesian commas and numeric strings."""
    if val is None:
        return None
    s = str(val).strip().replace(",", ".")
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
    s = str(val).strip().replace(",", "").replace(".", "")
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def clean_wilayah(name: Optional[str]) -> str:
    """Clean and standardize region names."""
    if not name:
        return "Indonesia"
    s = str(name).strip()
    return s


def normalize_single(raw: Dict[str, Any]) -> KkpKampungNelayanRecord:
    """Convert raw payload dict into validated KkpKampungNelayanRecord."""
    id_knmp = str(raw.get("id_knmp") or raw.get("ID KNMP") or raw.get("id") or "").strip()
    if not id_knmp:
        id_knmp = "KNMP-0000"

    nama = str(
        raw.get("nama_desa_nelayan")
        or raw.get("Nama Sentra Nelayan")
        or raw.get("nama")
        or raw.get("nama_pelabuhan")
        or "Sentra Nelayan"
    ).strip()

    prov = clean_wilayah(raw.get("provinsi") or raw.get("Provinsi"))
    kab = clean_wilayah(raw.get("kabupaten_kota") or raw.get("Kabupaten/Kota") or raw.get("Kabupatan / Kota"))

    nelayan = parse_int_safe(raw.get("jumlah_nelayan") or raw.get("Nelayan") or raw.get("nelayan"))
    cold = parse_float_safe(raw.get("kapasitas_cold_storage_ton") or raw.get("Cold Storage (Ton)") or raw.get("cold_storage"))
    es = parse_float_safe(raw.get("produksi_es_ton_hari") or raw.get("Pabrik Es (Ton/Hari)") or raw.get("pabrik_es"))
    status = str(raw.get("status_operasional") or raw.get("Status") or "Beroperasi").strip()

    lat = parse_float_safe(raw.get("latitude") or raw.get("Lat") or raw.get("lat"))
    lon = parse_float_safe(raw.get("longitude") or raw.get("Lon") or raw.get("lon"))

    return KkpKampungNelayanRecord(
        id_knmp=id_knmp,
        nama_desa_nelayan=nama,
        provinsi=prov,
        kabupaten_kota=kab,
        jumlah_nelayan=nelayan,
        kapasitas_cold_storage_ton=cold,
        produksi_es_ton_hari=es,
        status_operasional=status,
        latitude=lat,
        longitude=lon,
    )


class KkpKampungNelayanNormalizer(BaseNormalizer):
    """Maps raw KKP payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for KKP KNMP record: %s", exc)


Normalizer = KkpKampungNelayanNormalizer
