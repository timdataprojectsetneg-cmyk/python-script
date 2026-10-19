"""Data normalizer for Kemenkes SATUSEHAT CKG."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemenkesSatusehatCkgRecord, Record

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


def normalize_single(raw: Dict[str, Any]) -> KemenkesSatusehatCkgRecord:
    """Convert raw dict into validated KemenkesSatusehatCkgRecord."""
    id_faskes = clean_str(
        raw.get("id_fasyankes")
        or raw.get("ID Fasyankes")
        or raw.get("kode_faskes")
        or raw.get("id")
    ) or "P00000000"

    nama = clean_str(
        raw.get("nama_puskesmas_klinik")
        or raw.get("Nama Puskesmas/Klinik")
        or raw.get("nama_faskes")
        or raw.get("nama")
    ) or "Puskesmas / Klinik Pelaksana CKG"

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

    balita = parse_int_safe(
        raw.get("jumlah_skrining_balita")
        or raw.get("Skrining Balita")
        or raw.get("skrining_balita")
    )

    dewasa = parse_int_safe(
        raw.get("jumlah_skrining_dewasa")
        or raw.get("Skrining Dewasa")
        or raw.get("skrining_dewasa")
    )

    lansia = parse_int_safe(
        raw.get("jumlah_skrining_lansia")
        or raw.get("Skrining Lansia")
        or raw.get("skrining_lansia")
    )

    stunting = parse_int_safe(
        raw.get("kasus_terindikasi_stunting")
        or raw.get("Indikasi Stunting")
        or raw.get("stunting")
    )

    rujukan = parse_int_safe(
        raw.get("kasus_dirujuk_ke_rs")
        or raw.get("Rujukan RS")
        or raw.get("rujukan_rs")
    )

    data_src = clean_str(raw.get("data_source")) or "Kementerian Kesehatan RI (SATUSEHAT & Ditjen Kesmas)"

    return KemenkesSatusehatCkgRecord(
        id_fasyankes=id_faskes,
        nama_puskesmas_klinik=nama,
        provinsi=provinsi,
        kabupaten_kota=kab_kota,
        jumlah_skrining_balita=balita,
        jumlah_skrining_dewasa=dewasa,
        jumlah_skrining_lansia=lansia,
        kasus_terindikasi_stunting=stunting,
        kasus_dirujuk_ke_rs=rujukan,
        data_source=data_src,
    )


class KemenkesSatusehatCkgNormalizer(BaseNormalizer):
    """Maps raw SATUSEHAT CKG payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for SATUSEHAT CKG record: %s", exc)


Normalizer = KemenkesSatusehatCkgNormalizer
