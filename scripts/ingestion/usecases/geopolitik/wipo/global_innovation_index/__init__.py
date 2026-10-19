"""WIPO Global Innovation Index Ingestion Module."""

from .models import Record, WipoGlobalInnovationIndexRecord
from .normalizer import Normalizer, WipoGlobalInnovationIndexNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "WipoGlobalInnovationIndexRecord",
    "Normalizer",
    "WipoGlobalInnovationIndexNormalizer",
    "Extractor",
]
