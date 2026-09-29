"""REST API access — BPS Inflasi MoM."""

from __future__ import annotations

from .....core.extractors.api_extractor import ApiExtractor


class Extractor(ApiExtractor):
    """BPS API extraction; set PAGINATION_*, DATA_PATH and auth via env."""
