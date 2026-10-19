"""Normalizer for Kemlu RI Safe Travel Appeals."""

from __future__ import annotations

import html
import logging
import re
from typing import Any, Dict, Iterator, Optional, Tuple
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)

MONTH_MAP = {
    "januari": "01", "februari": "02", "maret": "03", "april": "04",
    "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
    "september": "09", "oktober": "10", "november": "11", "desember": "12"
}

REGION_MAP = {
    # Asia Tenggara
    "viet nam": ("Viet Nam", "Asia Tenggara"),
    "vietnam": ("Viet Nam", "Asia Tenggara"),
    "malaysia": ("Malaysia", "Asia Tenggara"),
    "singapura": ("Singapura", "Asia Tenggara"),
    "thailand": ("Thailand", "Asia Tenggara"),
    "filipina": ("Filipina", "Asia Tenggara"),
    "kamboja": ("Kamboja", "Asia Tenggara"),
    "laos": ("Laos", "Asia Tenggara"),
    "myanmar": ("Myanmar", "Asia Tenggara"),
    "brunei": ("Brunei Darussalam", "Asia Tenggara"),
    "timor leste": ("Timor Leste", "Asia Tenggara"),
    # Asia Selatan
    "nepal": ("Nepal", "Asia Selatan"),
    "india": ("India", "Asia Selatan"),
    "pakistan": ("Pakistan", "Asia Selatan"),
    "bangladesh": ("Bangladesh", "Asia Selatan"),
    "sri lanka": ("Sri Lanka", "Asia Selatan"),
    # Asia Timur
    "tiongkok": ("Tiongkok", "Asia Timur"),
    "china": ("Tiongkok", "Asia Timur"),
    "jepang": ("Jepang", "Asia Timur"),
    "korea selatan": ("Korea Selatan", "Asia Timur"),
    "korea utara": ("Korea Utara", "Asia Timur"),
    "taiwan": ("Taiwan", "Asia Timur"),
    # Timur Tengah
    "iran": ("Iran", "Timur Tengah"),
    "irak": ("Irak", "Timur Tengah"),
    "lebanon": ("Lebanon", "Timur Tengah"),
    "suriah": ("Suriah", "Timur Tengah"),
    "yaman": ("Yaman", "Timur Tengah"),
    "israel": ("Israel", "Timur Tengah"),
    "palestina": ("Palestina", "Timur Tengah"),
    "arab saudi": ("Arab Saudi", "Timur Tengah"),
    "yordania": ("Yordania", "Timur Tengah"),
    "uea": ("Uni Emirat Arab", "Timur Tengah"),
    "uni emirat arab": ("Uni Emirat Arab", "Timur Tengah"),
    "qatar": ("Qatar", "Timur Tengah"),
    "kuwait": ("Kuwait", "Timur Tengah"),
    "turki": ("Turki", "Timur Tengah / Eurasia"),
    # Eropa
    "ukraina": ("Ukraina", "Eropa"),
    "rusia": ("Rusia", "Eropa"),
    "inggris": ("Inggris Raya", "Eropa"),
    "jerman": ("Jerman", "Eropa"),
    "prancis": ("Prancis", "Eropa"),
    "belanda": ("Belanda", "Eropa"),
    "swiss": ("Swiss", "Eropa"),
    # Afrika
    "republik demokratik kongo": ("Republik Demokratik Kongo", "Afrika"),
    "kongo": ("Kongo", "Afrika"),
    "uganda": ("Uganda", "Afrika"),
    "sudan": ("Sudan", "Afrika"),
    "mesir": ("Mesir", "Afrika Utara"),
    "nigeria": ("Nigeria", "Afrika"),
    "somalia": ("Somalia", "Afrika"),
    # Amerika
    "kolombia": ("Kolombia", "Amerika Latin"),
    "haiti": ("Haiti", "Karibia"),
    "amerika serikat": ("Amerika Serikat", "Amerika Utara"),
    "kanada": ("Kanada", "Amerika Utara"),
    "brasil": ("Brasil", "Amerika Latin"),
    "venezuela": ("Venezuela", "Amerika Latin"),
    "meksiko": ("Meksiko", "Amerika Utara"),
    # Oseania
    "australia": ("Australia", "Oseania"),
    "selandia baru": ("Selandia Baru", "Oseania"),
    "papua nugini": ("Papua Nugini", "Oseania"),
}


def parse_date(date_raw: Any) -> str:
    """Parse Indonesian date string (e.g. '1 Agustus 2026') to ISO 'YYYY-MM-DD'."""
    if not date_raw or not isinstance(date_raw, str):
        return ""
    parts = date_raw.strip().split()
    if len(parts) >= 3:
        day = parts[0].zfill(2)
        month = MONTH_MAP.get(parts[1].lower(), "01")
        year = parts[2]
        return f"{year}-{month}-{day}"
    return date_raw.strip()


def clean_text(raw_text: Optional[str]) -> str:
    """Strip HTML tags and irregular whitespaces."""
    if not raw_text:
        return ""
    # Decode HTML entities like &nbsp; or \xa0
    text = html.unescape(raw_text).replace("\xa0", " ")
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse multiple whitespaces/newlines
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def resolve_country_and_region(country_name: str, country_names: Any, title: str, content: str) -> Tuple[str, str]:
    """Resolve country and geographic region."""
    # 1. Check country_names list
    candidates = []
    if isinstance(country_names, list) and country_names:
        for c in country_names:
            if c and str(c).strip().lower() != "semua negara":
                candidates.append(str(c).strip())
    elif country_name and country_name.strip().lower() != "semua negara":
        candidates.append(country_name.strip())

    # 2. If candidates found, inspect match
    if candidates:
        selected = candidates[0]
        sel_lower = selected.lower()
        for k, (c_std, reg) in REGION_MAP.items():
            if k in sel_lower:
                return (c_std, reg)
        return (selected, "Internasional")

    # 3. Check in title
    combined = f"{title} {content[:200]}".lower()
    for k, (c_std, reg) in REGION_MAP.items():
        # Match whole word boundaries where possible
        pattern = r"\b" + re.escape(k) + r"\b"
        if re.search(pattern, combined):
            return (c_std, reg)

    return ("Global / Semua Negara", "Global")


def resolve_alert_level(title: str, content: str, info_cat: str) -> str:
    """Determine advisory alert level based on text semantics."""
    combined = f"{title} {content}".lower()
    
    # Level 4 - Bahaya
    if any(k in combined for k in ["evakuasi", "perang", "darurat militer", "hindari perjalanan", "bahaya tinggi", "zona konflik", "siaga 1"]):
        return "Level 4 - Bahaya / Hindari (Merah)"

    # Level 3 - Hati-hati
    if any(k in combined for k in ["hati-hati", "tunda perjalanan", "gempa bumi", "tsunami", "banjir bandang", "letusan", "gunung api", "wabah", "ebola", "mpox", "eskalasi", "siaga 2"]):
        return "Level 3 - Hati-hati (Oranye)"

    # Level 2 - Waspada
    if any(k in combined for k in ["waspada", "imbauan", "unjuk rasa", "kerumunan", "demonstrasi", "pemilu", "cuaca buruk", "badai", "siaga 3"]):
        return "Level 2 - Waspada (Kuning)"

    return "Level 1 - Aman (Hijau)"


def resolve_trigger(title: str, content: str, info_cat: str) -> str:
    """Identify trigger category."""
    combined = f"{title} {content} {info_cat}".lower()

    if any(k in combined for k in ["gempa", "banjir", "tsunami", "topan", "siklon", "letusan", "gunung", "tanah longsor", "bencana"]):
        return "Bencana Alam"
    if any(k in combined for k in ["ebola", "mpox", "virus", "wabah", "kolera", "kesehatan", "flu burung"]):
        return "Wabah Penyakit / Krisis Kesehatan"
    if any(k in combined for k in ["perang", "militer", "senjata", "kerusuhan", "konflik", "penembakan", "teror"]):
        return "Konflik Bersenjata & Kerawanan Keamanan"
    if any(k in combined for k in ["visa", "paspor", "imigrasi", "bebas visa", "perlintasan", "izin tinggal"]):
        return "Kebijakan Keimigrasian & Perjalanan"

    if info_cat:
        return f"Informasi {info_cat}"
    return "Informasi Umum"


def extract_hotline(content: str) -> Optional[str]:
    """Extract emergency hotline if present in content."""
    # Pattern for international or local hotline numbers
    match = re.search(r"(\+\d{1,4}[\s\d\-\(\)]{7,20}|(?:hotline|darurat|kontak|wa|telepon)[:\s]+([\+\d\s\-]{8,20}))", content, re.IGNORECASE)
    if match:
        extracted = match.group(0).strip()
        # Clean prefix
        cleaned = re.sub(r"^(?:hotline|darurat|kontak|wa|telepon)[:\s]+", "", extracted, flags=re.IGNORECASE).strip()
        if len(cleaned) >= 7:
            return cleaned
    return None


class Normalizer(BaseNormalizer):
    """Maps raw Kemlu Safe Travel appeals to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                title = clean_text(raw.get("news_title") or "")
                raw_content = clean_text(raw.get("news_content") or "")
                info_cat = str(raw.get("news_info") or "").strip()
                country_name = str(raw.get("news_country_name") or "").strip()
                country_names = raw.get("news_country_names", [])

                negara, kawasan = resolve_country_and_region(country_name, country_names, title, raw_content)
                level_peringatan = resolve_alert_level(title, raw_content, info_cat)
                pemicu = resolve_trigger(title, raw_content, info_cat)
                tanggal = parse_date(raw.get("news_date"))
                hotline = extract_hotline(raw_content)

                norm_data = {
                    "negara": negara,
                    "kawasan": kawasan,
                    "level_peringatan": level_peringatan,
                    "ringkasan_imbauan": raw_content if raw_content else title,
                    "tanggal_rilis": tanggal,
                    "pemicu_peringatan": pemicu,
                    "nomor_hotline_kbri_kjri": hotline,
                    "news_id": raw.get("news_id"),
                    "uuid": raw.get("uuid"),
                    "news_title": title,
                    "news_info": info_cat,
                    "news_image_path": raw.get("news_image_path"),
                    "news_total_read": int(raw.get("news_total_read") or 0),
                    "data_source": "Kementerian Luar Negeri RI - Portal Safe Travel",
                }

                yield Record(**norm_data).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for Safe Travel record: %s", exc)
            except Exception as exc:
                logger.warning("Unexpected normalization error: %s", exc)
