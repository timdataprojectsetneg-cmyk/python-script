"""Data normalizer for GDELT Media Asing."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import GdeltMediaAsingRecord, Record

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


def normalize_single(raw: Dict[str, Any]) -> GdeltMediaAsingRecord:
    """Convert raw dict into validated GdeltMediaAsingRecord."""
    tanggal = clean_str(raw.get("tanggal_artikel") or raw.get("Tanggal") or raw.get("seendate") or raw.get("date"))
    if tanggal and len(tanggal) >= 8 and "T" in tanggal:
        tanggal = tanggal.split("T")[0]
    elif tanggal and len(tanggal) == 14 and tanggal.isdigit():
        # format YYYYMMDDHHMMSS
        tanggal = f"{tanggal[:4]}-{tanggal[4:6]}-{tanggal[6:8]}"

    judul = (
        clean_str(raw.get("judul_berita") or raw.get("Judul Berita") or raw.get("title"))
        or "Pemberitaan Media Asing tentang Indonesia"
    )
    media = (
        clean_str(raw.get("nama_media_sumber") or raw.get("Media Sumber") or raw.get("domain") or raw.get("source"))
        or "Media Internasional"
    )
    negara = clean_str(raw.get("negara_asal_media") or raw.get("Negara Media") or raw.get("sourcecountry") or raw.get("country"))
    kawasan = clean_str(raw.get("kawasan_media") or raw.get("Kawasan") or raw.get("region"))
    topik = (
        clean_str(raw.get("topik_utama") or raw.get("Topik Utama") or raw.get("topic"))
        or "Diplomasi & Geopolitik"
    )
    skor = parse_float_safe(raw.get("skor_sentimen_gdelt") or raw.get("Skor Sentimen") or raw.get("tone") or raw.get("sentiment"))
    url = clean_str(raw.get("url_artikel") or raw.get("URL Artikel") or raw.get("url"))

    return GdeltMediaAsingRecord(
        tanggal_artikel=tanggal,
        judul_berita=judul,
        nama_media_sumber=media,
        negara_asal_media=negara,
        kawasan_media=kawasan,
        topik_utama=topik,
        skor_sentimen_gdelt=skor,
        url_artikel=url,
    )


class GdeltMediaAsingNormalizer(BaseNormalizer):
    """Maps raw GDELT news payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for GDELT media record: %s", exc)


Normalizer = GdeltMediaAsingNormalizer
