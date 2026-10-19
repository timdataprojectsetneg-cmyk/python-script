"""Data normalizer for UN Status Traktat Multilateral."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import UnStatusTraktatMultilateralRecord, Record

logger = logging.getLogger(__name__)


def clean_str(val: Any) -> Optional[str]:
    """Clean string values."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ["..", "-", "NA", "NaN", "N/A"]:
        return None
    return s


def normalize_single(raw: Dict[str, Any]) -> UnStatusTraktatMultilateralRecord:
    """Convert raw dict into validated UnStatusTraktatMultilateralRecord."""
    id_tr = (
        clean_str(raw.get("id_traktat") or raw.get("ID Traktat") or raw.get("id"))
        or "UNTC-GEN-00"
    )
    nama = (
        clean_str(raw.get("nama_konvensi_internasional") or raw.get("Nama Konvensi") or raw.get("title"))
        or "Konvensi Multilateral PBB"
    )
    depository = (
        clean_str(raw.get("organisasi_penyimpan_depository") or raw.get("Depository") or raw.get("depository"))
        or "Sekjen PBB"
    )
    tgl_adopsi = clean_str(raw.get("tanggal_adopsi_dunia") or raw.get("Tanggal Adopsi") or raw.get("adoption_date"))
    status_ri = (
        clean_str(raw.get("status_keikutsertaan_indonesia") or raw.get("Status RI") or raw.get("status"))
        or "Pihak (Diratifikasi)"
    )
    uu_ri = clean_str(raw.get("dokumen_pengesahan_uu_ri") or raw.get("UU Ratifikasi") or raw.get("ratification_doc"))
    tgl_deposit = clean_str(raw.get("tanggal_penyerahan_instrumen") or raw.get("Tanggal Deposit") or raw.get("deposit_date"))
    reservasi = clean_str(raw.get("catatan_reservasi_deklarasi") or raw.get("Reservasi/Deklarasi") or raw.get("reservation"))

    return UnStatusTraktatMultilateralRecord(
        id_traktat=id_tr,
        nama_konvensi_internasional=nama,
        organisasi_penyimpan_depository=depository,
        tanggal_adopsi_dunia=tgl_adopsi,
        status_keikutsertaan_indonesia=status_ri,
        dokumen_pengesahan_uu_ri=uu_ri,
        tanggal_penyerahan_instrumen=tgl_deposit,
        catatan_reservasi_deklarasi=reservasi,
    )


class UnStatusTraktatMultilateralNormalizer(BaseNormalizer):
    """Maps raw treaty status payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for UN treaty record: %s", exc)


Normalizer = UnStatusTraktatMultilateralNormalizer
