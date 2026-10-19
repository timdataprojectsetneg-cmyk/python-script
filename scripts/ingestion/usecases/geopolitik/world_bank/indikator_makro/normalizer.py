"""Data normalizer for World Bank Bilateral Macroeconomic Indicators."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import WorldBankIndikatorMakroRecord, Record

logger = logging.getLogger(__name__)

REGION_MAP = {
    "IDN": "Asia Tenggara",
    "MYS": "Asia Tenggara",
    "SGP": "Asia Tenggara",
    "THA": "Asia Tenggara",
    "PHL": "Asia Tenggara",
    "VNM": "Asia Tenggara",
    "BRN": "Asia Tenggara",
    "KHM": "Asia Tenggara",
    "LAO": "Asia Tenggara",
    "MMR": "Asia Tenggara",
    "TLS": "Asia Tenggara",
    "CHN": "Asia Timur",
    "JPN": "Asia Timur",
    "KOR": "Asia Timur",
    "IND": "Asia Selatan",
    "AUS": "Oseania",
    "USA": "Amerika Utara",
    "GBR": "Eropa Barat",
    "DEU": "Eropa Barat",
    "FRA": "Eropa Barat",
    "RUS": "Eropa Timur",
    "SAU": "Timur Tengah",
    "BRA": "Amerika Selatan",
    "ZAF": "Afrika Selatan",
    "TUR": "Timur Tengah & Eropa",
}


def parse_float_safe(val: Any) -> Optional[float]:
    """Parse float safely, handling commas and decimal points."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s in ["..", "-", "NA", "NaN"]:
        return None
    try:
        return round(float(s), 4)
    except (ValueError, TypeError):
        return None


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


def normalize_single(raw: Dict[str, Any]) -> WorldBankIndikatorMakroRecord:
    """Convert raw payload dict into validated WorldBankIndikatorMakroRecord."""
    iso3 = str(raw.get("kode_iso3") or raw.get("countryiso3code") or raw.get("iso3") or "").strip().upper()
    negara = str(raw.get("negara") or raw.get("country") or iso3 or "Unknown").strip()
    tahun = parse_int_safe(raw.get("tahun") or raw.get("date") or raw.get("year")) or 2024
    kawasan = raw.get("kawasan") or REGION_MAP.get(iso3, "Global")

    pop = parse_float_safe(raw.get("populasi_juta_jiwa") or raw.get("populasi"))
    pdb_miliar = parse_float_safe(raw.get("pdb_nominal_miliar_usd") or raw.get("pdb_miliar"))
    pdb_kapita = parse_float_safe(raw.get("pdb_per_kapita_usd") or raw.get("pdb_kapita"))
    pertumbuhan = parse_float_safe(raw.get("pertumbuhan_pdb_pct") or raw.get("pertumbuhan_pdb"))
    inflasi = parse_float_safe(raw.get("inflasi_pct") or raw.get("inflasi"))

    ekspor = parse_float_safe(raw.get("nilai_ekspor_ri_ke_mitra_usd") or raw.get("ekspor_ri"))
    impor = parse_float_safe(raw.get("nilai_impor_ri_dari_mitra_usd") or raw.get("impor_ri"))
    neraca = parse_float_safe(raw.get("neraca_perdagangan_ri_usd") or raw.get("neraca_ri"))
    if neraca is None and ekspor is not None and impor is not None:
        neraca = round(ekspor - impor, 2)

    return WorldBankIndikatorMakroRecord(
        negara=negara,
        kode_iso3=iso3,
        kawasan=kawasan,
        tahun=tahun,
        populasi_juta_jiwa=pop,
        pdb_nominal_miliar_usd=pdb_miliar,
        pdb_per_kapita_usd=pdb_kapita,
        pertumbuhan_pdb_pct=pertumbuhan,
        inflasi_pct=inflasi,
        nilai_ekspor_ri_ke_mitra_usd=ekspor,
        nilai_impor_ri_dari_mitra_usd=impor,
        neraca_perdagangan_ri_usd=neraca,
    )


class WorldBankIndikatorMakroNormalizer(BaseNormalizer):
    """Maps raw World Bank payloads into validated Record dictionaries."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = normalize_single(raw)
                yield record.model_dump()
            except (ValidationError, Exception) as exc:
                logger.warning("Validation failed for World Bank indicator record: %s", exc)


Normalizer = WorldBankIndikatorMakroNormalizer
