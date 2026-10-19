"""Data normalizer for Setkab Tracking Arahan Lapangan."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import SetkabTrackingArahanLapanganRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> SetkabTrackingArahanLapanganRecord:
    """Convert raw dict into validated SetkabTrackingArahanLapanganRecord."""
    id_arh = (
        clean_str(raw.get("id_arahan") or raw.get("ID Arahan") or raw.get("id"))
        or "ARH-2026-GEN-00"
    )
    tgl = clean_str(raw.get("tanggal_arahan") or raw.get("Tanggal Arahan") or raw.get("tanggal") or raw.get("date"))
    lokasi = (
        clean_str(raw.get("lokasi_kunjungan") or raw.get("Lokasi") or raw.get("location"))
        or "Wilayah Kunker Lapangan"
    )
    isi = (
        clean_str(raw.get("isi_arahan_presiden") or raw.get("Isi Arahan Presiden") or raw.get("arahan") or raw.get("instruction"))
        or "Instruksi dan arahan Presiden saat kunjungan kerja lapangan"
    )
    instansi = (
        clean_str(raw.get("instansi_pelaksana") or raw.get("Instansi Pelaksana") or raw.get("instansi") or raw.get("agency"))
        or "Kementerian / Lembaga Terkait"
    )
    dok = clean_str(raw.get("dokumen_dasar_tindak_lanjut") or raw.get("Dasar Dokumen") or raw.get("dokumen") or raw.get("regulation"))
    status = (
        clean_str(raw.get("status_tindak_lanjut") or raw.get("Status Tindak Lanjut") or raw.get("Status") or raw.get("status"))
        or "Sedang Berjalan"
    )

    return SetkabTrackingArahanLapanganRecord(
        id_arahan=id_arh,
        tanggal_arahan=tgl,
        lokasi_kunjungan=lokasi,
        isi_arahan_presiden=isi,
        instansi_pelaksana=instansi,
        dokumen_dasar_tindak_lanjut=dok,
        status_tindak_lanjut=status,
    )


class SetkabTrackingArahanLapanganNormalizer(BaseNormalizer):
    """Maps raw presidential directives into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Setkab arahan record: %s", exc)


Normalizer = SetkabTrackingArahanLapanganNormalizer
