"""Ekspor HS Pertanian: ekspor komoditas pertanian per kode HS dari portal Eksim Kementan.

Optional config (env ``GEOPOLITIK__PERTANIAN__EKSPOR_HS_PERTANIAN__<KEY>``):
``YEARS`` (``2025``, ``2022-2025`` or ``2022,2024``; default the latest two years
offered by the portal) and ``PARAMS`` as a JSON object with ``subsektor``
(comma-separated ids 1-5; default all) and ``include_zero`` (keep months with
zero volume and value; default false).
"""

from __future__ import annotations

from .._eksim import EksimHsExtractor


class Extractor(EksimHsExtractor):
    ARUS = "Ekspor"
    DEFAULT_URL = "https://app3.pertanian.go.id/eksim/eksporHs.php"
    RESULT_PAGE = "hasilEksporHs.php"
