"""Data normalizer for Setpres Pertemuan Bilateral."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import SetpresPertemuanBilateralRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> SetpresPertemuanBilateralRecord:
    """Convert raw dict into validated SetpresPertemuanBilateralRecord."""
    id_pertemuan = (
        clean_str(raw.get("id_pertemuan") or raw.get("ID Pertemuan") or raw.get("id"))
        or "BIL-2026-GEN-00"
    )
    tanggal = clean_str(raw.get("tanggal_kegiatan") or raw.get("Tanggal") or raw.get("date"))
    negara = (
        clean_str(raw.get("negara_mitra") or raw.get("Negara Mitra") or raw.get("negara"))
        or "Negara Mitra"
    )
    lokasi = (
        clean_str(raw.get("lokasi_kota_negara") or raw.get("Lokasi") or raw.get("location"))
        or "Jakarta, Indonesia"
    )
    format_p = (
        clean_str(raw.get("format_pertemuan") or raw.get("Format") or raw.get("format"))
        or "Pertemuan Bilateral"
    )
    tokoh = (
        clean_str(raw.get("tokoh_pemimpin_mitra") or raw.get("Pemimpin Mitra") or raw.get("leader"))
        or "Kepala Negara / Pemerintahan Mitra"
    )
    isu = clean_str(raw.get("isu_utama_dibahas") or raw.get("Isu Utama") or raw.get("issues"))
    kesepakatan = clean_str(raw.get("kesepakatan_konkret") or raw.get("Hasil Kesepakatan") or raw.get("agreements"))

    return SetpresPertemuanBilateralRecord(
        id_pertemuan=id_pertemuan,
        tanggal_kegiatan=tanggal,
        negara_mitra=negara,
        lokasi_kota_negara=lokasi,
        format_pertemuan=format_p,
        tokoh_pemimpin_mitra=tokoh,
        isu_utama_dibahas=isu,
        kesepakatan_konkret=kesepakatan,
    )


class SetpresPertemuanBilateralNormalizer(BaseNormalizer):
    """Maps raw bilateral meeting payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for bilateral meeting record: %s", exc)


Normalizer = SetpresPertemuanBilateralNormalizer
