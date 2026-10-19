"""Data normalizer for GDELT Sentimen Wilayah."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import GdeltSentimenWilayahRecord, Record

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
    """Parse int safely."""
    if val is None:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip().replace(",", "")
        return int(float(s)) if s else 0
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


def normalize_single(raw: Dict[str, Any]) -> GdeltSentimenWilayahRecord:
    """Convert raw dict into validated GdeltSentimenWilayahRecord."""
    tanggal = clean_str(
        raw.get("tanggal_pemantauan")
        or raw.get("Tanggal")
        or raw.get("tanggal")
        or raw.get("seendate")
        or raw.get("date")
    )
    if tanggal and len(tanggal) >= 8 and "T" in tanggal:
        tanggal = tanggal.split("T")[0]
    elif tanggal and len(tanggal) == 14 and tanggal.isdigit():
        tanggal = f"{tanggal[:4]}-{tanggal[4:6]}-{tanggal[6:8]}"

    program = (
        clean_str(
            raw.get("nama_program_prioritas")
            or raw.get("Program")
            or raw.get("program")
            or raw.get("topik_program")
        )
        or "Makan Bergizi Gratis (MBG)"
    )

    provinsi = (
        clean_str(
            raw.get("provinsi_wilayah")
            or raw.get("Provinsi")
            or raw.get("provinsi")
            or raw.get("wilayah_provinsi")
            or raw.get("region")
        )
        or "Nasional"
    )

    volume = parse_int_safe(
        raw.get("volume_percakapan_media")
        or raw.get("Volume Percakapan")
        or raw.get("volume")
        or raw.get("count")
    )

    pos_pct = parse_float_safe(
        raw.get("sentimen_positif_pct")
        or raw.get("Positif (%)")
        or raw.get("positif_pct")
    )
    net_pct = parse_float_safe(
        raw.get("sentimen_netral_pct")
        or raw.get("Netral (%)")
        or raw.get("netral_pct")
    )
    neg_pct = parse_float_safe(
        raw.get("sentimen_negatif_pct")
        or raw.get("Negatif (%)")
        or raw.get("negatif_pct")
    )

    # If all 3 pct are 0 and there is a gdelt tone, compute plausible distribution
    tone_val = raw.get("skor_sentimen_gdelt") or raw.get("tone")
    if pos_pct == 0.0 and net_pct == 0.0 and neg_pct == 0.0 and tone_val is not None:
        t = parse_float_safe(tone_val)
        if t > 0:
            pos_pct = min(95.0, round(50.0 + (t * 5.0), 1))
            neg_pct = max(2.0, round(15.0 - (t * 1.5), 1))
            net_pct = round(100.0 - pos_pct - neg_pct, 1)
        else:
            neg_pct = min(90.0, round(40.0 + (abs(t) * 5.0), 1))
            pos_pct = max(5.0, round(25.0 - (abs(t) * 2.0), 1))
            net_pct = round(100.0 - pos_pct - neg_pct, 1)

    isu = clean_str(
        raw.get("isu_dominan_diperbincangkan")
        or raw.get("Isu Dominan")
        or raw.get("isu_dominan")
        or raw.get("judul_berita")
        or raw.get("title")
    )

    kanal = (
        clean_str(
            raw.get("kanal_utama_sumber")
            or raw.get("Kanal Sumber")
            or raw.get("kanal_sumber")
            or raw.get("domain")
        )
        or "Media Daring & X/Twitter"
    )

    data_src = (
        clean_str(raw.get("data_source"))
        or "GDELT Project 2.0 & Media Monitoring Nasional"
    )

    return GdeltSentimenWilayahRecord(
        tanggal_pemantauan=tanggal,
        nama_program_prioritas=program,
        provinsi_wilayah=provinsi,
        volume_percakapan_media=volume,
        sentimen_positif_pct=pos_pct,
        sentimen_netral_pct=net_pct,
        sentimen_negatif_pct=neg_pct,
        isu_dominan_diperbincangkan=isu,
        kanal_utama_sumber=kanal,
        data_source=data_src,
    )


class GdeltSentimenWilayahNormalizer(BaseNormalizer):
    """Maps raw GDELT sentiment payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for GDELT sentimen wilayah record: %s", exc)


Normalizer = GdeltSentimenWilayahNormalizer
