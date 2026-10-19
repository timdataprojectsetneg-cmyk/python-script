"""Data normalizer for Kemlu Iuran Organisasi Internasional."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemluIuranOrganisasiInternasionalRecord, Record

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
            return float(val)
        s = str(val).strip().replace(",", "")
        return float(s) if s else 0.0
    except (ValueError, TypeError):
        return 0.0


def normalize_single(raw: Dict[str, Any]) -> KemluIuranOrganisasiInternasionalRecord:
    """Convert raw dict into validated KemluIuranOrganisasiInternasionalRecord."""
    id_oi = (
        clean_str(raw.get("id_organisasi") or raw.get("ID OI") or raw.get("id"))
        or "OI-GEN-00"
    )
    nama = (
        clean_str(raw.get("nama_organisasi_internasional") or raw.get("Nama Organisasi") or raw.get("nama"))
        or "Organisasi Internasional"
    )
    kategori = (
        clean_str(raw.get("kategori_oi") or raw.get("Kategori") or raw.get("category"))
        or "PBB & Badan Khusus"
    )
    dasar = clean_str(raw.get("dasar_hukum_keanggotaan") or raw.get("Dasar Hukum") or raw.get("legal_basis"))
    focal = (
        clean_str(raw.get("kl_focal_point") or raw.get("KL Focal Point") or raw.get("focal_point"))
        or "Kemenlu RI"
    )
    iuran_valas = parse_float_safe(raw.get("besaran_iuran_tahunan_valas") or raw.get("Iuran (Valas)") or raw.get("fee"))
    mata_uang = (
        clean_str(raw.get("mata_uang") or raw.get("Mata Uang") or raw.get("currency"))
        or "USD"
    )
    ekuivalen = parse_float_safe(raw.get("ekuivalen_rupiah_miliar") or raw.get("Ekuivalen (Miliar Rp)") or raw.get("idr_billion"))
    evaluasi = (
        clean_str(raw.get("evaluasi_kemanfaatan") or raw.get("Evaluasi Kemanfaatan") or raw.get("evaluation"))
        or "Tinggi / Strategis"
    )
    status = (
        clean_str(raw.get("status_iuran_terakhir") or raw.get("Status Iuran") or raw.get("status"))
        or "Lunas"
    )

    return KemluIuranOrganisasiInternasionalRecord(
        id_organisasi=id_oi,
        nama_organisasi_internasional=nama,
        kategori_oi=kategori,
        dasar_hukum_keanggotaan=dasar,
        kl_focal_point=focal,
        besaran_iuran_tahunan_valas=iuran_valas,
        mata_uang=mata_uang,
        ekuivalen_rupiah_miliar=ekuivalen,
        evaluasi_kemanfaatan=evaluasi,
        status_iuran_terakhir=status,
    )


class KemluIuranOrganisasiInternasionalNormalizer(BaseNormalizer):
    """Maps raw OI membership fee payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemlu OI record: %s", exc)


Normalizer = KemluIuranOrganisasiInternasionalNormalizer
