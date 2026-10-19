"""Data normalizer for Setpres Matriks Risiko Kunjungan."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import SetpresMatriksRisikoKunjunganRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> SetpresMatriksRisikoKunjunganRecord:
    """Convert raw dict into validated SetpresMatriksRisikoKunjunganRecord."""
    id_rsk = (
        clean_str(raw.get("id_risiko") or raw.get("ID Risiko") or raw.get("id"))
        or "RSK-2026-GEN-00"
    )
    kategori = (
        clean_str(raw.get("kategori_risiko") or raw.get("Kategori") or raw.get("category"))
        or "Protokoler"
    )
    ancaman = (
        clean_str(raw.get("deskripsi_ancaman") or raw.get("Deskripsi Ancaman") or raw.get("description"))
        or "Potensi kendala kelancaran acara kepresidenan"
    )
    probabilitas = (
        clean_str(raw.get("tingkat_probabilitas") or raw.get("Probabilitas") or raw.get("probability"))
        or "Sedang"
    )
    dampak = (
        clean_str(raw.get("tingkat_dampak") or raw.get("Dampak") or raw.get("impact"))
        or "Signifikan"
    )
    mitigasi = clean_str(raw.get("rencana_mitigasi") or raw.get("Rencana Mitigasi") or raw.get("mitigation"))
    pic = (
        clean_str(raw.get("penanggung_jawab_pic") or raw.get("PIC Satgas") or raw.get("pic"))
        or "Paspampres & Protokol Setpres"
    )

    return SetpresMatriksRisikoKunjunganRecord(
        id_risiko=id_rsk,
        kategori_risiko=kategori,
        deskripsi_ancaman=ancaman,
        tingkat_probabilitas=probabilitas,
        tingkat_dampak=dampak,
        rencana_mitigasi=mitigasi,
        penanggung_jawab_pic=pic,
    )


class SetpresMatriksRisikoKunjunganNormalizer(BaseNormalizer):
    """Maps raw risk matrix payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Setpres risk matrix record: %s", exc)


Normalizer = SetpresMatriksRisikoKunjunganNormalizer
