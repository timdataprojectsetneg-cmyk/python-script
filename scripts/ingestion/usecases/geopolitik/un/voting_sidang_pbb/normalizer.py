"""Data normalizer for UN Voting Sidang PBB."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import UnVotingSidangPbbRecord, Record

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


def normalize_single(raw: Dict[str, Any]) -> UnVotingSidangPbbRecord:
    """Convert raw dict into validated UnVotingSidangPbbRecord."""
    nomor = (
        clean_str(raw.get("nomor_resolusi") or raw.get("Nomor Resolusi") or raw.get("resolution_no"))
        or "A/RES/GEN/00"
    )
    badan = (
        clean_str(raw.get("badan_pbb") or raw.get("Badan PBB") or raw.get("body"))
        or "UN General Assembly"
    )
    tanggal = clean_str(raw.get("tanggal_voting") or raw.get("Tanggal Voting") or raw.get("date"))
    judul = (
        clean_str(raw.get("judul_resolusi") or raw.get("Judul Resolusi") or raw.get("title"))
        or "Resolusi Sidang PBB"
    )
    posisi_ri = (
        clean_str(raw.get("posisi_indonesia") or raw.get("Posisi Indonesia") or raw.get("indonesia_position"))
        or "In Favor"
    )
    in_favor = parse_int_safe(raw.get("total_suara_in_favor") or raw.get("In Favor") or raw.get("in_favor"))
    against = parse_int_safe(raw.get("total_suara_against") or raw.get("Against") or raw.get("against"))
    abstain = parse_int_safe(raw.get("total_abstain") or raw.get("Abstain") or raw.get("abstain"))
    mitra = clean_str(raw.get("posisi_negara_mitra_utama") or raw.get("Posisi Mitra Kunci") or raw.get("key_partners"))

    return UnVotingSidangPbbRecord(
        nomor_resolusi=nomor,
        badan_pbb=badan,
        tanggal_voting=tanggal,
        judul_resolusi=judul,
        posisi_indonesia=posisi_ri,
        total_suara_in_favor=in_favor,
        total_suara_against=against,
        total_abstain=abstain,
        posisi_negara_mitra_utama=mitra,
    )


class UnVotingSidangPbbNormalizer(BaseNormalizer):
    """Maps raw UN voting payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for UN voting record: %s", exc)


Normalizer = UnVotingSidangPbbNormalizer
