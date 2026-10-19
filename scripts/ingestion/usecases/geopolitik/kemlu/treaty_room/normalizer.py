"""Data normalizer for Kemlu Treaty Room (Perjanjian Internasional RI)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemluTreatyRoomRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> KemluTreatyRoomRecord:
    """Convert raw dict into validated KemluTreatyRoomRecord."""
    id_per = clean_str(raw.get("id_perjanjian") or raw.get("ID Perjanjian")) or "TR-2026-GEN-00"
    mitra = clean_str(raw.get("negara_mitra") or raw.get("Negara Mitra") or raw.get("partner_country")) or "Negara Mitra"
    judul = clean_str(raw.get("judul_perjanjian") or raw.get("Judul Perjanjian") or raw.get("title")) or "Perjanjian Kerja Sama Bilateral RI"

    bidang = clean_str(raw.get("bidang_kerja_sama") or raw.get("Bidang") or raw.get("sector")) or "Kerja Sama Bilateral"
    tahap = clean_str(raw.get("tahapan") or raw.get("Tahapan") or raw.get("status")) or "Ditandatangani"

    raw_tgl = raw.get("tanggal_penandatanganan") or raw.get("Tanggal TTD") or raw.get("date")
    tgl = clean_str(raw_tgl)
    if tgl and len(tgl) >= 10:
        tgl = tgl[:10]

    dasar = clean_str(raw.get("dasar_pengesahan_uu_perpres") or raw.get("Dasar Pengesahan") or raw.get("legal_basis"))
    instansi = clean_str(raw.get("instansi_penanggung_jawab_kl") or raw.get("Instansi PJ") or raw.get("pic"))

    return KemluTreatyRoomRecord(
        id_perjanjian=id_per,
        negara_mitra=mitra,
        judul_perjanjian=judul,
        bidang_kerja_sama=bidang,
        tahapan=tahap,
        tanggal_penandatanganan=tgl,
        dasar_pengesahan_uu_perpres=dasar,
        instansi_penanggung_jawab_kl=instansi,
    )


class KemluTreatyRoomNormalizer(BaseNormalizer):
    """Maps raw Treaty Room payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemlu Treaty Room record: %s", exc)


Normalizer = KemluTreatyRoomNormalizer
