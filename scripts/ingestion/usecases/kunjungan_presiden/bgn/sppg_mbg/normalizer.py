"""Data normalizer for BGN SPPG MBG."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import BgnSppgMbgRecord, Record

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
    """Parse integer safely."""
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
    """Parse float safely."""
    if val is None:
        return None
    try:
        if isinstance(val, (int, float)):
            return round(float(val), 6)
        s = str(val).strip().replace(",", "")
        return round(float(s), 6) if s else None
    except (ValueError, TypeError):
        return None


def normalize_single(raw: Dict[str, Any]) -> BgnSppgMbgRecord:
    """Convert raw dict into validated BgnSppgMbgRecord."""
    id_sppg = clean_str(
        raw.get("id_sppg")
        or raw.get("ID SPPG")
        or raw.get("id")
        or raw.get("kode_sppg")
    ) or "SPPG-0000-000"

    nama = clean_str(
        raw.get("nama_sppg")
        or raw.get("Nama SPPG")
        or raw.get("nama_dapur")
        or raw.get("nama")
    ) or "Unit Dapur SPPG MBG"

    provinsi = clean_str(
        raw.get("provinsi")
        or raw.get("Provinsi")
        or raw.get("nama_provinsi")
    ) or "Indonesia"

    kab_kota = clean_str(
        raw.get("kabupaten_kota")
        or raw.get("Kabupaten/Kota")
        or raw.get("kabupaten")
        or raw.get("kota")
    ) or provinsi

    kecamatan = clean_str(
        raw.get("kecamatan")
        or raw.get("Kecamatan")
    ) or kab_kota

    kapasitas = parse_int_safe(
        raw.get("kapasitas_porsi_harian")
        or raw.get("Kapasitas (Porsi)")
        or raw.get("kapasitas")
        or raw.get("porsi")
    )

    penerima = parse_int_safe(
        raw.get("jumlah_penerima_manfaat")
        or raw.get("Penerima")
        or raw.get("penerima_manfaat")
        or raw.get("sasaran")
    )

    status = clean_str(
        raw.get("status_operasional")
        or raw.get("Status")
        or raw.get("status")
    ) or "Aktif"

    lat = parse_float_safe(
        raw.get("latitude")
        or raw.get("Lat")
        or raw.get("lat")
    )

    lon = parse_float_safe(
        raw.get("longitude")
        or raw.get("Lon")
        or raw.get("long")
        or raw.get("lon")
    )

    data_src = clean_str(raw.get("data_source")) or "Badan Gizi Nasional (BGN)"

    return BgnSppgMbgRecord(
        id_sppg=id_sppg,
        nama_sppg=nama,
        provinsi=provinsi,
        kabupaten_kota=kab_kota,
        kecamatan=kecamatan,
        kapasitas_porsi_harian=kapasitas,
        jumlah_penerima_manfaat=penerima,
        status_operasional=status,
        latitude=lat,
        longitude=lon,
        data_source=data_src,
    )


class BgnSppgMbgNormalizer(BaseNormalizer):
    """Maps raw BGN SPPG payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for BGN SPPG record: %s", exc)


Normalizer = BgnSppgMbgNormalizer
