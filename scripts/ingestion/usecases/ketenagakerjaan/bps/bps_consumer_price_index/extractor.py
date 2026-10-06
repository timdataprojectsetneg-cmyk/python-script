"""API access — BPS Consumer Price Index (IHK) per province.

BPS WebAPI var=2261 (Indeks Harga Konsumen, tahun dasar 2022), one column per
month. The API key is injected via the URL's ``WebAPI_KEY`` placeholder using
``BPS_WEBAPI_KEY`` (fallback ``BPS_API_KEY``).
"""

from __future__ import annotations

from .._webapi import BpsWebApiExtractor


class Extractor(BpsWebApiExtractor):
    ENTITY_FIELD = "provinsi"
    PREFER_TURVAR = True
