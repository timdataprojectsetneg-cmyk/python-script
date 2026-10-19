"""BPS Profil Sosioekonomi Ingestion Module."""

from .models import Record, BpsProfilSosioekonomiRecord
from .normalizer import Normalizer, BpsProfilSosioekonomiNormalizer
from .extractor import Extractor

__all__ = [
    "Record",
    "BpsProfilSosioekonomiRecord",
    "Normalizer",
    "BpsProfilSosioekonomiNormalizer",
    "Extractor",
]
