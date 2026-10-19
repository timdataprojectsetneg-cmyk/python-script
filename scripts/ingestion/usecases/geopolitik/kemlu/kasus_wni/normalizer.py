"""Data normalizer for Kemlu Rekapitulasi Kasus WNI."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemluKasusWniRecord, Record

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
        return 1
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "").replace(".", "")
        return int(s) if s else 1
    except (ValueError, TypeError):
        return 1


def normalize_single(raw: Dict[str, Any]) -> KemluKasusWniRecord:
    """Convert raw dict into validated KemluKasusWniRecord."""
    id_kas = clean_str(raw.get("id_kasus") or raw.get("ID Kasus")) or "PWNI-2026-GEN-00"
    neg = clean_str(raw.get("negara_kejadian") or raw.get("Negara") or raw.get("country")) or "Luar Negeri"
    kat = clean_str(raw.get("kategori_kasus") or raw.get("Kategori Kasus") or raw.get("category")) or "Pelindungan Hak WNI"

    korban = parse_int_safe(raw.get("jumlah_korban_terlibat") or raw.get("Korban (Jiwa)") or raw.get("korban"))

    raw_tgl = raw.get("tanggal_pengaduan") or raw.get("Tanggal Lapor") or raw.get("date")
    tgl = clean_str(raw_tgl)
    if tgl and len(tgl) >= 10:
        tgl = tgl[:10]

    status = clean_str(raw.get("status_penanganan") or raw.get("Status Penanganan") or raw.get("status")) or "Dalam Proses"
    bantuan = clean_str(raw.get("bantuan_hukum_diberikan") or raw.get("Bantuan Diberikan") or raw.get("bantuan"))

    return KemluKasusWniRecord(
        id_kasus=id_kas,
        negara_kejadian=neg,
        kategori_kasus=kat,
        jumlah_korban_terlibat=korban,
        tanggal_pengaduan=tgl,
        status_penanganan=status,
        bantuan_hukum_diberikan=bantuan,
    )


class KemluKasusWniNormalizer(BaseNormalizer):
    """Maps raw Kasus WNI payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemlu Kasus WNI record: %s", exc)


Normalizer = KemluKasusWniNormalizer
