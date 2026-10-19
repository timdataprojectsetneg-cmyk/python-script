"""UCDP Konflik Global (Peta Konflik Bersenjata Global) Ingestion Module."""

from .models import Record, UcdpKonflikGlobalRecord
from .normalizer import Normalizer, UcdpKonflikGlobalNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "UcdpKonflikGlobalRecord",
    "Normalizer",
    "UcdpKonflikGlobalNormalizer",
    "Extractor",
]
