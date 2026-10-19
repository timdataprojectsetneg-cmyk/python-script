"""Normalizer for SIPRI Military Expenditure records."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)

REGION_MAP = {
    "indonesia": "Asia Tenggara",
    "singapore": "Asia Tenggara",
    "malaysia": "Asia Tenggara",
    "thailand": "Asia Tenggara",
    "vietnam": "Asia Tenggara",
    "philippines": "Asia Tenggara",
    "myanmar": "Asia Tenggara",
    "cambodia": "Asia Tenggara",
    "brunei": "Asia Tenggara",
    "china": "Asia Timur",
    "japan": "Asia Timur",
    "korea, south": "Asia Timur",
    "korea, north": "Asia Timur",
    "taiwan": "Asia Timur",
    "india": "Asia Selatan",
    "pakistan": "Asia Selatan",
    "australia": "Oseania",
    "new zealand": "Oseania",
    "united states": "Amerika Utara",
    "united states of america": "Amerika Utara",
    "usa": "Amerika Utara",
    "russia": "Eropa / Eurasia",
    "russian federation": "Eropa / Eurasia",
    "united kingdom": "Eropa",
    "france": "Eropa",
    "germany": "Eropa",
    "saudi arabia": "Timur Tengah",
    "iran": "Timur Tengah",
    "israel": "Timur Tengah",
    "turkey": "Timur Tengah / Eurasia",
}

MODERNIZATION_FOCUS = {
    "indonesia": "Modernisasi Jet Tempur Rafale/F-15EX, Fregat Merah Putih, dan Radar Hanud",
    "singapore": "Pesawat Tempur Siluman F-35B dan Kapal Selam Invincible-class",
    "australia": "Kapal Selam Bertenaga Nuklir (AUKUS) dan Sistem Rudal Serang Jarak Jauh",
    "china": "Kapal Induk Type 003, Pesawat Siluman J-20/J-35, dan Rudal Hipersonik",
    "united states": "Armada Laut Tanpa Awak, Pembom B-21 Raider, dan Sistem Satelit Militer",
    "russia": "Sistem Rudal Hipersonik Kinzhal/Zircon dan Modernisasi Kapal Selam Nuklir",
    "japan": "Kapasitas Serangan Balasan (Counterstrike), Kapal Induk Kaga/Izumo, F-35",
    "india": "Program Rudal BrahMos, Kapal Induk INS Vikrant, dan Jet Tempur Tejas",
}


def clean_percentage(val: Any) -> Optional[float]:
    """Clean and normalize ratio to percentage (e.g. 0.018 -> 1.80%)."""
    if val is None or val in (". .", "xxx", "-", ""):
        return None
    try:
        fval = float(val)
        # If expressed as a decimal ratio (e.g. 0.02)
        if 0.0 < fval < 1.0:
            return round(fval * 100, 2)
        return round(fval, 2)
    except (ValueError, TypeError):
        return None


def clean_expenditure(val: Any) -> Optional[float]:
    """Clean expenditure numeric value."""
    if val is None or val in (". .", "xxx", "-", ""):
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None


class Normalizer(BaseNormalizer):
    """Maps raw extracted SIPRI country-year data to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                cname = str(raw.get("country") or "").strip()
                if not cname or cname.lower() in ("country", "total", "world", "africa", "asia"):
                    continue

                year_val = int(raw.get("year") or 2024)
                exp_usd = clean_expenditure(raw.get("expenditure_usd_million"))
                if exp_usd is None or exp_usd <= 0:
                    continue

                gdp_pct = clean_percentage(raw.get("gdp_pct"))
                govt_pct = clean_percentage(raw.get("govt_pct"))

                clower = cname.lower()
                kawasan = REGION_MAP.get(clower, "Internasional")
                focus = MODERNIZATION_FOCUS.get(clower, "Pemeliharaan Kesiapan Operasional Militer Standar")

                norm_data = {
                    "negara": cname,
                    "tahun": year_val,
                    "belanja_militer_juta_usd": exp_usd,
                    "belanja_militer_pct_pdb": gdp_pct,
                    "belanja_militer_pct_apbn": govt_pct,
                    "peringkat_belanja_dunia": raw.get("rank"),
                    "tren_modernisasi_alutsista": focus,
                    "kawasan": kawasan,
                    "data_source": "Stockholm International Peace Research Institute (SIPRI)",
                }

                yield Record(**norm_data).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for SIPRI record: %s", exc)
            except Exception as exc:
                logger.warning("Unexpected normalization error for SIPRI: %s", exc)
