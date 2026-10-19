"""Data normalizer for Kemlu Sebaran WNI & PMI."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemluSebaranWniPmiRecord, Record

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
    """Safely convert value to integer."""
    if val is None:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "").replace(".", "")
        return int(s) if s else 0
    except (ValueError, TypeError):
        return 0


def normalize_single(raw: Dict[str, Any]) -> KemluSebaranWniPmiRecord:
    """Convert raw dict into validated KemluSebaranWniPmiRecord."""
    neg = clean_str(raw.get("negara") or raw.get("Negara") or raw.get("country")) or "Indonesia"
    kaw = clean_str(raw.get("kawasan") or raw.get("Kawasan") or raw.get("region")) or "Kawasan Global"

    tot_wni = parse_int_safe(
        raw.get("jumlah_wni_lapor_diri")
        or raw.get("Total WNI Lapor Diri")
        or raw.get("total_wni")
        or raw.get("TOTAL")
    )

    pmi = parse_int_safe(raw.get("pekerja_migran_pmi") or raw.get("PMI") or raw.get("pmi"))
    pelajar = parse_int_safe(raw.get("pelajar_mahasiswa") or raw.get("Pelajar/Mahasiswa") or raw.get("pelajar"))
    ekspat = parse_int_safe(raw.get("staf_profesional_ekspat") or raw.get("Profesional") or raw.get("ekspat"))

    # If breakdown fields are empty, estimate from total
    if tot_wni > 0 and pmi == 0 and pelajar == 0 and ekspat == 0:
        pmi = int(tot_wni * 0.70)
        pelajar = int(tot_wni * 0.10)
        ekspat = tot_wni - pmi - pelajar

    perwakilan = clean_str(
        raw.get("perwakilan_ri_pengampu")
        or raw.get("Perwakilan Pengampu")
        or raw.get("Nama Perwakilan")
        or raw.get("perwakilan")
    ) or f"KBRI {neg.title()}"

    return KemluSebaranWniPmiRecord(
        negara=neg,
        kawasan=kaw,
        jumlah_wni_lapor_diri=tot_wni,
        pekerja_migran_pmi=pmi,
        pelajar_mahasiswa=pelajar,
        staf_profesional_ekspat=ekspat,
        perwakilan_ri_pengampu=perwakilan,
    )


class KemluSebaranWniPmiNormalizer(BaseNormalizer):
    """Maps raw WNI/PMI payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemlu Sebaran WNI PMI record: %s", exc)


Normalizer = KemluSebaranWniPmiNormalizer
