"""Kemendagri Susunan Pemerintahan Daerah Ingestion Module."""

from .models import Record, KemendagriSusunanPemdaRecord
from .normalizer import Normalizer, KemendagriSusunanPemdaNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "KemendagriSusunanPemdaRecord",
    "Normalizer",
    "KemendagriSusunanPemdaNormalizer",
    "Extractor",
]
