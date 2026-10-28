"""Caldara-Iacoviello Geopolitical Risk (GPR) index ingestion module."""

from .config import ACCESS_TYPE, DISPLAY_NAME, FREQUENCY, PUBLISHER, SOURCE, TARGET
from .extractor import Extractor
from .models import Record

__all__ = [
    "SOURCE",
    "PUBLISHER",
    "DISPLAY_NAME",
    "ACCESS_TYPE",
    "FREQUENCY",
    "TARGET",
    "Extractor",
    "Record",
]
