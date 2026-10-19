"""Data normalizer for BPS Profil Sosioekonomi."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import BpsProfilSosioekonomiRecord, Record

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


def parse_float_safe(val: Any) -> float:
    """Parse float safely."""
    if val is None:
        return 0.0
    try:
        if isinstance(val, (int, float)):
            return round(float(val), 2)
        s = str(val).strip().replace(",", "").replace("%", "")
        return round(float(s), 2) if s else 0.0
    except (ValueError, TypeError):
        return 0.0


def normalize_single(raw: Dict[str, Any]) -> BpsProfilSosioekonomiRecord:
    """Convert raw dict into validated BpsProfilSosioekonomiRecord."""
    kode = clean_str(
        raw.get("kode_wilayah_kemendagri")
        or raw.get("Kode Wilayah")
        or raw.get("kode_wilayah")
        or raw.get("kode")
        or raw.get("id_wilayah")
    ) or "00.00"

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

    penduduk = parse_int_safe(
        raw.get("jumlah_penduduk_jiwa")
        or raw.get("Penduduk (Jiwa)")
        or raw.get("penduduk")
        or raw.get("jumlah_penduduk")
    )

    kepadatan = parse_float_safe(
        raw.get("kepadatan_penduduk_km2")
        or raw.get("Kepadatan (/km2)")
        or raw.get("kepadatan")
    )

    kemiskinan = parse_float_safe(
        raw.get("persentase_penduduk_miskin")
        or raw.get("Kemiskinan (%)")
        or raw.get("persentase_miskin")
        or raw.get("kemiskinan")
    )

    tpt = parse_float_safe(
        raw.get("tingkat_pengangguran_terbuka_tpt")
        or raw.get("TPT (%)")
        or raw.get("tpt")
        or raw.get("pengangguran")
    )

    ipm = parse_float_safe(
        raw.get("indeks_pembangunan_manusia_ipm")
        or raw.get("IPM")
        or raw.get("ipm")
    )

    pdrb_pct = parse_float_safe(
        raw.get("pertumbuhan_ekonomi_pdrb_pct")
        or raw.get("PDRB (%)")
        or raw.get("pertumbuhan_pdrb")
    )

    pdrb_nominal = parse_float_safe(
        raw.get("pdrb_harga_berlaku_juta_rp")
        or raw.get("PDRB Berlaku (Juta Rp)")
        or raw.get("pdrb_nominal")
        or raw.get("pdrb")
    )

    data_src = clean_str(raw.get("data_source")) or "Badan Pusat Statistik (BPS)"

    return BpsProfilSosioekonomiRecord(
        kode_wilayah_kemendagri=kode,
        provinsi=provinsi,
        kabupaten_kota=kab_kota,
        jumlah_penduduk_jiwa=penduduk,
        kepadatan_penduduk_km2=kepadatan,
        persentase_penduduk_miskin=kemiskinan,
        tingkat_pengangguran_terbuka_tpt=tpt,
        indeks_pembangunan_manusia_ipm=ipm,
        pertumbuhan_ekonomi_pdrb_pct=pdrb_pct,
        pdrb_harga_berlaku_juta_rp=pdrb_nominal,
        data_source=data_src,
    )


class BpsProfilSosioekonomiNormalizer(BaseNormalizer):
    """Maps raw BPS socio-economic data payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for BPS profil sosioekonomi record: %s", exc)


Normalizer = BpsProfilSosioekonomiNormalizer
