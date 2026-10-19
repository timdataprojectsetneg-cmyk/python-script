"""Data normalizer for Kemendagri Susunan Pemerintahan Daerah."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemendagriSusunanPemdaRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A", "-"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> KemendagriSusunanPemdaRecord:
    """Convert raw dict into validated KemendagriSusunanPemdaRecord."""
    kode = clean_str(
        raw.get("kode_daerah") or raw.get("Kode Daerah") or raw.get("kode")
    ) or "00.00"

    prov = clean_str(
        raw.get("provinsi") or raw.get("Provinsi") or raw.get("province")
    ) or "Indonesia"

    kab = clean_str(
        raw.get("kabupaten_kota") or raw.get("Kabupaten/Kota") or raw.get("daerah")
    ) or "Wilayah Administratif"

    kepala = clean_str(
        raw.get("nama_kepala_daerah")
        or raw.get("Kepala Daerah")
        or raw.get("nama_bupati")
        or raw.get("nama_walikota")
    ) or "Penjabat Kepala Daerah"

    status = clean_str(
        raw.get("status_jabatan") or raw.get("Status")
    ) or "Definitif"

    partai = clean_str(
        raw.get("partai_pengusung_koalisi") or raw.get("Koalisi Pengusung")
    )
    ketua_dprd = clean_str(
        raw.get("nama_ketua_dprd") or raw.get("Ketua DPRD")
    )
    partai_dprd = clean_str(
        raw.get("partai_ketua_dprd") or raw.get("Partai DPRD")
    )
    komposisi = clean_str(
        raw.get("komposisi_kursi_dprd") or raw.get("Komposisi Kursi")
    )

    return KemendagriSusunanPemdaRecord(
        kode_daerah=kode,
        provinsi=prov,
        kabupaten_kota=kab,
        nama_kepala_daerah=kepala,
        status_jabatan=status,
        partai_pengusung_koalisi=partai,
        nama_ketua_dprd=ketua_dprd,
        partai_ketua_dprd=partai_dprd,
        komposisi_kursi_dprd=komposisi,
    )


class KemendagriSusunanPemdaNormalizer(BaseNormalizer):
    """Maps raw Kemendagri payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemendagri susunan pemda record: %s", exc)


Normalizer = KemendagriSusunanPemdaNormalizer
