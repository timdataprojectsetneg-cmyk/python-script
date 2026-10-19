"""Data normalizer for Setkab Matriks Janji & Arahan Presiden."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import SetkabMatriksJanjiRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values, returning None if empty or invalid."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> SetkabMatriksJanjiRecord:
    """Convert raw scraped dict into validated SetkabMatriksJanjiRecord."""
    id_kom = clean_str(raw.get("id_komitmen") or raw.get("ID Komitmen") or raw.get("id")) or "JNJ-2026-000"
    program = clean_str(
        raw.get("program_strategis")
        or raw.get("Program Strategis")
        or raw.get("Komitmen")
        or raw.get("Arahan")
        or "Program Strategis Nasional"
    ) or "Program Prioritas Presiden"

    substansi = clean_str(
        raw.get("substansi_komitmen")
        or raw.get("Substansi Komitmen")
        or raw.get("Isi Komitmen")
        or raw.get("Isi arahan")
        or raw.get("substansi")
    ) or "Komitmen kerja dan arahan strategis Presiden RI."

    tgl = clean_str(raw.get("tanggal_penyampaian") or raw.get("Tanggal") or raw.get("tanggal"))
    forum = clean_str(
        raw.get("forum_agenda")
        or raw.get("Forum/Agenda")
        or raw.get("Dasar Penyampaian")
        or raw.get("forum")
    )

    prov = clean_str(raw.get("provinsi") or raw.get("Provinsi"))
    kab = clean_str(raw.get("kabupaten_kota") or raw.get("Kabupaten/Kota") or raw.get("Target (Daerah Terdampak)"))
    desa = clean_str(raw.get("desa_lokasi") or raw.get("Desa/Lokasi") or raw.get("Lokasi (Acara)") or raw.get("Lokasi Arahan"))

    pic = clean_str(raw.get("kl_penanggung_jawab") or raw.get("K/L PIC") or raw.get("Instansi Penanggung Jawab") or raw.get("kl_pic"))
    status = clean_str(raw.get("status_pemenuhan") or raw.get("Status") or raw.get("status")) or "On Progress"
    catatan = clean_str(raw.get("catatan_progres_sekdukkab") or raw.get("Catatan Progres") or raw.get("Progres"))
    kemenko = clean_str(raw.get("koordinasi_kemenko") or raw.get("Kemenko Pengampu") or raw.get("kemenko"))

    return SetkabMatriksJanjiRecord(
        id_komitmen=id_kom,
        program_strategis=program,
        substansi_komitmen=substansi,
        tanggal_penyampaian=tgl,
        forum_agenda=forum,
        provinsi=prov,
        kabupaten_kota=kab,
        desa_lokasi=desa,
        kl_penanggung_jawab=pic,
        status_pemenuhan=status,
        catatan_progres_sekdukkab=catatan,
        koordinasi_kemenko=kemenko,
    )


class SetkabMatriksJanjiNormalizer(BaseNormalizer):
    """Maps raw Setkab payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Setkab matriks janji record: %s", exc)


Normalizer = SetkabMatriksJanjiNormalizer
