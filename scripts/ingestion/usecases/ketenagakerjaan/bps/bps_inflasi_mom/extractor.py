"""API access — BPS Inflasi Bulanan (month-to-month) per city.

BPS WebAPI var=1 (inflasi bulanan), one column per month plus ``tahunan``
(akumulasi tahun kalender). The API key is injected via the URL's
``WebAPI_KEY`` placeholder using ``BPS_WEBAPI_KEY`` (fallback ``BPS_API_KEY``).
"""

from __future__ import annotations

from .._webapi import BpsWebApiExtractor


class Extractor(BpsWebApiExtractor):
    ENTITY_FIELD = "kota_inflasi"
    EXTRA_TURTAHUN_FIELDS = {"tahunan": "tahunan"}
