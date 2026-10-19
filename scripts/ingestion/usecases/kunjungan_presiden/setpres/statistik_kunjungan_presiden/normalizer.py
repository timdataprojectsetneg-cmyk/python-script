"""Data normalizer for Setpres Statistik Kunjungan Kerja Presiden."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import SetpresStatistikKunjunganRecord, Record

logger = logging.getLogger(__name__)


def parse_int_safe(val: Any) -> Optional[int]:
    """Parse integer safely."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def clean_text(val: Any) -> Optional[str]:
    """Clean string text and citations."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["-", ".."]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> SetpresStatistikKunjunganRecord:
    """Convert raw scraped dict into validated SetpresStatistikKunjunganRecord."""
    prov = clean_text(raw.get("provinsi") or raw.get("Provinsi")) or "Indonesia"
    kab = clean_text(raw.get("kabupaten_kota") or raw.get("Kabupaten/Kota")) or "Wilayah Kunjungan"

    freq = parse_int_safe(
        raw.get("frekuensi_kunjungan_total")
        or raw.get("frekuensi_kunjungan")
        or raw.get("Frekuensi Kunjungan")
        or raw.get("total_kunjungan")
        or 1
    )
    if freq is None or freq < 1:
        freq = 1

    tgl = clean_text(raw.get("kunjungan_terakhir") or raw.get("Kunjungan Terakhir") or raw.get("tanggal"))
    agenda = clean_text(raw.get("agenda_utama") or raw.get("Agenda Utama") or raw.get("rincian"))
    durasi = parse_int_safe(raw.get("durasi_kunjungan_hari") or raw.get("Durasi (Hari)") or raw.get("durasi") or 1) or 1
    pejabat = clean_text(raw.get("pejabat_pendamping_utama") or raw.get("Pejabat Pendamping") or raw.get("pendamping"))

    return SetpresStatistikKunjunganRecord(
        provinsi=prov,
        kabupaten_kota=kab,
        frekuensi_kunjungan_total=freq,
        kunjungan_terakhir=tgl,
        agenda_utama=agenda,
        durasi_kunjungan_hari=durasi,
        pejabat_pendamping_utama=pejabat,
    )


class SetpresStatistikKunjunganNormalizer(BaseNormalizer):
    """Maps raw Setpres kunker payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Setpres kunker record: %s", exc)


Normalizer = SetpresStatistikKunjunganNormalizer
