"""Data normalizer for SP4N-LAPOR! Rekapitulasi Aduan Wilayah."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import LaporRekapAduanRecord, Record

logger = logging.getLogger(__name__)


def clean_kabupaten_name(raw_name: str) -> str:
    """Format and normalize kabupaten/kota name."""
    name = raw_name.strip()
    if not name:
        return "Wilayah Nasional"
    if name.lower().startswith("kota ") or name.lower().startswith("kabupaten "):
        return name
    if name.lower().startswith("kab "):
        return "Kabupaten " + name[4:].strip()
    # Default to Kabupaten prefix if not specified
    return f"Kabupaten {name}"


def normalize_single(raw: Dict[str, Any]) -> LaporRekapAduanRecord:
    """Convert raw LAPOR maps/data payload into a validated LaporRekapAduanRecord."""
    # Case 1: Payload from datawarehouse maps API
    if "location_name" in raw or "total" in raw:
        loc_raw = raw.get("location_name") or "Nasional Tanpa Wilayah"
        kabupaten_kota = clean_kabupaten_name(loc_raw)
        provinsi = raw.get("provinsi") or raw.get("province_name") or "DKI Jakarta"
        
        total_str = str(raw.get("total") or "1").replace(",", "").strip()
        try:
            total_aduan = int(total_str)
        except ValueError:
            total_aduan = 1

        json_id = raw.get("json_id") or raw.get("object_id")
        raw_obj_key = str(raw.get("object_key") or "")
        kode_wil = raw.get("kode_wilayah") or (raw_obj_key.replace("ID-", "") if raw_obj_key else None)
        tahun = int(raw.get("tahun") or 2024)
        tanggal = raw.get("tanggal_lapor") or f"{tahun}-12-31"

        id_suffix = str(kode_wil).replace(".", "") if kode_wil else (str(json_id) if json_id else "NAS")
        id_aduan = f"LAPOR-{id_suffix}-{tahun}"

        instansi_tujuan = raw.get("instansi_tujuan") or f"Pemerintah {kabupaten_kota}"
        kategori = raw.get("kategori_program") or "Pelayanan Publik & Tata Kelola Wilayah"
        status = raw.get("status_tindak_lanjut") or ("Selesai" if total_aduan > 10 else "Ditindaklanjuti")

        uraian = (
            raw.get("uraian_laporan")
            or f"Rekapitulasi {total_aduan:,} aduan masyarakat wilayah {kabupaten_kota} terkait pelayanan publik, infrastruktur, dan administrasi daerah."
        )

        return LaporRekapAduanRecord(
            id_aduan=id_aduan,
            tanggal_lapor=tanggal,
            kategori_program=kategori,
            provinsi=provinsi,
            kabupaten_kota=kabupaten_kota,
            uraian_laporan=uraian,
            status_tindak_lanjut=status,
            instansi_tujuan=instansi_tujuan,
            jumlah_aduan=total_aduan,
            tahun=tahun,
            kode_wilayah=kode_wil,
        )

    # Case 2: Pre-formatted record
    return LaporRekapAduanRecord.model_validate(raw)


class LaporRekapAduanNormalizer(BaseNormalizer):
    """Maps raw LAPOR payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for LAPOR rekap aduan record: %s", exc)


Normalizer = LaporRekapAduanNormalizer
