"""CekFakta Klarifikasi Hoaks Ingestion Module."""

from .models import Record, CekfaktaKlarifikasiHoaksRecord
from .normalizer import Normalizer, CekfaktaKlarifikasiHoaksNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "CekfaktaKlarifikasiHoaksRecord",
    "Normalizer",
    "CekfaktaKlarifikasiHoaksNormalizer",
    "Extractor",
]
