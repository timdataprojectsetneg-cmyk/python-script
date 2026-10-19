"""Data normalizer for CekFakta Klarifikasi Hoaks."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import CekfaktaKlarifikasiHoaksRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> CekfaktaKlarifikasiHoaksRecord:
    """Convert raw dict into validated CekfaktaKlarifikasiHoaksRecord."""
    id_nar = (
        clean_str(raw.get("id_narasi") or raw.get("ID Narasi") or raw.get("id"))
        or "NAR-2026-GEN-00"
    )
    isu = (
        clean_str(raw.get("isu_pemberitaan") or raw.get("Isu Pemberitaan") or raw.get("topic"))
        or "Isu Pemberitaan Internasional"
    )
    klaim = (
        clean_str(raw.get("klaim_narasi") or raw.get("Klaim Narasi") or raw.get("claim"))
        or "Klaim narasi pemberitaan publik"
    )
    media = clean_str(raw.get("asal_media_sumber") or raw.get("Media Asal") or raw.get("media"))
    sebaran = (
        clean_str(raw.get("tingkat_sebaran") or raw.get("Sebaran") or raw.get("virality"))
        or "Sedang"
    )
    verifikasi = (
        clean_str(raw.get("hasil_verifikasi_cek_fakta") or raw.get("Hasil Verifikasi Cek Fakta") or raw.get("verdict"))
        or "Konteks Dimanipulasi"
    )
    tanggapan = clean_str(raw.get("tanggapan_resmi_pemerintah") or raw.get("Tanggapan Klarifikasi Pemerintah") or raw.get("clarification"))
    instansi = (
        clean_str(raw.get("instansi_klarifikasi") or raw.get("Instansi Juru Bicara") or raw.get("spokesperson"))
        or "Kementerian Luar Negeri RI & Komdigi"
    )
    tanggal = clean_str(raw.get("tanggal_klarifikasi") or raw.get("Tanggal Klarifikasi") or raw.get("date"))

    return CekfaktaKlarifikasiHoaksRecord(
        id_narasi=id_nar,
        isu_pemberitaan=isu,
        klaim_narasi=klaim,
        asal_media_sumber=media,
        tingkat_sebaran=sebaran,
        hasil_verifikasi_cek_fakta=verifikasi,
        tanggapan_resmi_pemerintah=tanggapan,
        instansi_klarifikasi=instansi,
        tanggal_klarifikasi=tanggal,
    )


class CekfaktaKlarifikasiHoaksNormalizer(BaseNormalizer):
    """Maps raw fact-check payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for CekFakta record: %s", exc)


Normalizer = CekfaktaKlarifikasiHoaksNormalizer
