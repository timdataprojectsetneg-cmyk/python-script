"""Kemenkop SIMKOPDES (Koperasi Desa Merah Putih) Ingestion Module."""

from .models import Record, KemenkopSimkopdesKdmpRecord
from .normalizer import Normalizer, KemenkopSimkopdesKdmpNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "KemenkopSimkopdesKdmpRecord",
    "Normalizer",
    "KemenkopSimkopdesKdmpNormalizer",
    "Extractor",
]
