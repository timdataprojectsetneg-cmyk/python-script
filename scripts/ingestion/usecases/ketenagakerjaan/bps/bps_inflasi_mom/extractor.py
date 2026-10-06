"""Api access — BPS Inflasi MoM."""

from __future__ import annotations

from .....core.extractors.api_extractor import ApiExtractor


class Extractor(ApiExtractor):
    """Implemented per source; falls back to the generic api extractor."""
