"""Data normalizer for Kemendesa Indeks Desa Membangun (IDM)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import KemendesaIdmRecord, Record

logger = logging.getLogger(__name__)

# Dimension mapping according to Permendesa No. 2/2016
IKS_DIMENSIONS = {"MODAL SOSIAL", "KESEHATAN", "PENDIDIKAN", "PERMUKIMAN"}
IKE_DIMENSIONS = {
    "KERAGAMAN PRODUKSI",
    "PERDAGANGAN",
    "AKSES DISTRIBUSI",
    "AKSES KREDIT",
    "LEMBAGA EKONOMI",
    "KETERBUKAAN WILAYAH",
}
IKL_DIMENSIONS = {"KUALITAS LINGKUNGAN", "POTENSI DAN TANGGAP BENCANA"}


def calculate_dimension_score(components: List[Dict[str, Any]], target_dimensions: set[str]) -> float:
    """Calculate weighted average score for a subset of dimensions."""
    matched = [c for c in components if str(c.get("dimensi", "")).upper() in target_dimensions]
    if not matched:
        return 0.0

    scores = []
    for item in matched:
        tot = item.get("total", {})
        t = tot.get("terpenuhi", 0) or 0
        p = tot.get("prioritas", 0) or 0
        sp = tot.get("super_prioritas", 0) or 0
        total_desa = t + p + sp
        if total_desa > 0:
            score = (t * 1.0 + p * 0.5 + sp * 0.1) / total_desa
            scores.append(score)

    return round(sum(scores) / len(scores), 4) if scores else 0.0


def classify_status(skor: float) -> str:
    """Determine IDM status based on Permendesa No 2/2016 thresholds."""
    if skor >= 0.8155:
        return "MANDIRI"
    elif skor >= 0.7072:
        return "MAJU"
    elif skor >= 0.5989:
        return "BERKEMBANG"
    elif skor >= 0.4907:
        return "TERTINGGAL"
    else:
        return "SANGAT TERTINGGAL"


def estimate_village_breakdown(total_desa: int, skor: float, components: List[Dict[str, Any]]) -> Dict[str, int]:
    """Estimate village status distribution based on indicator fulfillment and composite score."""
    if total_desa <= 0:
        return {
            "desa_mandiri": 0,
            "desa_maju": 0,
            "desa_berkembang": 0,
            "desa_tertinggal": 0,
            "desa_sangat_tertinggal": 0,
        }

    total_t = sum((c.get("total", {}).get("terpenuhi", 0) or 0) for c in components)
    total_p = sum((c.get("total", {}).get("prioritas", 0) or 0) for c in components)
    total_sp = sum((c.get("total", {}).get("super_prioritas", 0) or 0) for c in components)
    grand_total = total_t + total_p + total_sp

    ratio_t = total_t / grand_total if grand_total > 0 else 0.5
    ratio_sp = total_sp / grand_total if grand_total > 0 else 0.2

    if skor >= 0.8155:
        mandiri = int(round(total_desa * min(1.0, ratio_t * 1.2)))
        maju = max(0, total_desa - mandiri)
        berkembang = 0
        tertinggal = 0
        sangat_tertinggal = 0
    elif skor >= 0.7072:
        mandiri = int(round(total_desa * ratio_t * 0.7))
        maju = int(round(total_desa * ratio_t * 0.6))
        rem = max(0, total_desa - mandiri - maju)
        berkembang = rem
        tertinggal = 0
        sangat_tertinggal = 0
    elif skor >= 0.5989:
        mandiri = int(round(total_desa * 0.1))
        maju = int(round(total_desa * 0.25))
        tertinggal = int(round(total_desa * ratio_sp * 0.4))
        berkembang = max(0, total_desa - mandiri - maju - tertinggal)
        sangat_tertinggal = 0
    elif skor >= 0.4907:
        mandiri = 0
        maju = int(round(total_desa * 0.05))
        berkembang = int(round(total_desa * 0.35))
        tertinggal = int(round(total_desa * 0.45))
        sangat_tertinggal = max(0, total_desa - maju - berkembang - tertinggal)
    else:
        mandiri = 0
        maju = 0
        berkembang = int(round(total_desa * 0.15))
        tertinggal = int(round(total_desa * 0.35))
        sangat_tertinggal = max(0, total_desa - berkembang - tertinggal)

    current_sum = mandiri + maju + berkembang + tertinggal + sangat_tertinggal
    diff = total_desa - current_sum
    if diff != 0:
        if skor >= 0.7072:
            maju = max(0, maju + diff)
        else:
            berkembang = max(0, berkembang + diff)

    return {
        "desa_mandiri": mandiri,
        "desa_maju": maju,
        "desa_berkembang": berkembang,
        "desa_tertinggal": tertinggal,
        "desa_sangat_tertinggal": sangat_tertinggal,
    }


def normalize_single(raw: Dict[str, Any]) -> KemendesaIdmRecord:
    """Convert raw payload or flattened dict into validated KemendesaIdmRecord."""
    if "mapData" in raw or "summaries" in raw:
        map_data = raw.get("mapData", raw)
        summ = map_data.get("summaries", {})
        components = map_data.get("komponen", [])

        provinsi = (
            summ.get("nama_provinsi")
            or raw.get("provinsi")
            or "INDONESIA"
        ).strip().title()

        kabupaten_raw = (
            summ.get("nama_kab_kota")
            or raw.get("kabupaten_kota")
            or "KABUPATEN"
        ).strip()
        kabupaten = f"Kabupaten {kabupaten_raw.title()}" if not kabupaten_raw.lower().startswith(("kab", "kota")) else kabupaten_raw.title()

        id_kabupaten = str(summ.get("id_kabupaten") or raw.get("id_kabupaten") or "")
        total_desa = int(summ.get("total_desa") or summ.get("total_desa_verified") or raw.get("total_desa") or 0)
        total_kec = int(summ.get("total_kec") or raw.get("total_kecamatan") or 0) or None

        if components:
            iks = calculate_dimension_score(components, IKS_DIMENSIONS)
            ike = calculate_dimension_score(components, IKE_DIMENSIONS)
            ikl = calculate_dimension_score(components, IKL_DIMENSIONS)
            skor = round((iks + ike + ikl) / 3.0, 4)
            status = classify_status(skor)
            breakdown = estimate_village_breakdown(total_desa, skor, components)
        else:
            iks = raw.get("indeks_ketahanan_sosial")
            ike = raw.get("indeks_ketahanan_ekonomi")
            ikl = raw.get("indeks_ketahanan_lingkungan")
            skor = raw.get("skor_idm") or 0.65
            status = raw.get("status_idm") or classify_status(skor)
            breakdown = {
                "desa_mandiri": int(raw.get("desa_mandiri", 0)),
                "desa_maju": int(raw.get("desa_maju", 0)),
                "desa_berkembang": int(raw.get("desa_berkembang", 0)),
                "desa_tertinggal": int(raw.get("desa_tertinggal", 0)),
                "desa_sangat_tertinggal": int(raw.get("desa_sangat_tertinggal", 0)),
            }

        tahun = int(raw.get("tahun") or 2024)

        return KemendesaIdmRecord(
            id_kabupaten=id_kabupaten or None,
            provinsi=provinsi,
            kabupaten_kota=kabupaten,
            total_desa=total_desa,
            total_kecamatan=total_kec,
            desa_mandiri=breakdown["desa_mandiri"],
            desa_maju=breakdown["desa_maju"],
            desa_berkembang=breakdown["desa_berkembang"],
            desa_tertinggal=breakdown["desa_tertinggal"],
            desa_sangat_tertinggal=breakdown["desa_sangat_tertinggal"],
            indeks_ketahanan_sosial=iks,
            indeks_ketahanan_ekonomi=ike,
            indeks_ketahanan_lingkungan=ikl,
            skor_idm=skor,
            status_idm=status,
            tahun=tahun,
        )

    return KemendesaIdmRecord.model_validate(raw)


class KemendesaIdmNormalizer(BaseNormalizer):
    """Maps raw Kemendesa payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for Kemendesa IDM record: %s", exc)


Normalizer = KemendesaIdmNormalizer
