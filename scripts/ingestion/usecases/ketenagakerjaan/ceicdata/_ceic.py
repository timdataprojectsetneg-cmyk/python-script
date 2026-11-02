"""Shared extractor base for CEIC API tables.

Alur: tabel (``TB...``) -> seluruh series di dalam tabel -> observasi per series.
Setiap source cukup menetapkan ``table_id``. Satu record dihasilkan per observasi
(periode x series). Dimensi tabel (provinsi, usia, industri, dst.) ada di nama
series, sehingga normalizer source yang memetakannya ke kolom sendiri.

Token diambil dari config ``token`` atau env ``CEIC_API_TOKEN``.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Callable, Dict, Iterator, List

from ceic_api_client.api_client import ApiClient
from ceic_api_client.apis.layout_api import LayoutApi
from ceic_api_client.apis.series_api import SeriesApi
from ceic_api_client.rest import ApiException

from ....core.base.extractor import BaseExtractor
from ....core.base.normalizer import BaseNormalizer

RETRIES = 5


def _iso(value: Any) -> Any:
    return value.isoformat() if hasattr(value, "isoformat") else value


class RawNormalizer(BaseNormalizer):
    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        yield from records


class CeicTableExtractor(BaseExtractor):
    table_id: str = ""
    accept_language: str = "id"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._token = config.get("token") or os.getenv("CEIC_API_TOKEN")
        if not self._token:
            raise ValueError("CEIC_API_TOKEN tidak ditemukan di env atau config 'token'")
        self._accept_language = str(
            config.get("accept_language") or self.accept_language
        ).strip()

    @staticmethod
    def _call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        for attempt in range(RETRIES):
            try:
                return func(*args, **kwargs)
            except ApiException as exc:
                retryable = exc.status == 429 or (exc.status or 0) >= 500
                if not retryable or attempt == RETRIES - 1:
                    raise
                time.sleep(2**attempt * 5)

    @staticmethod
    def _items(response: Any) -> List[Dict[str, Any]]:
        data = response.to_dict() if hasattr(response, "to_dict") else response
        items = data.get("data") if isinstance(data, dict) else data
        return items or []

    @staticmethod
    def _province(meta: Dict[str, Any]) -> Any:
        """Series province: ``metadata.province``, else the first geo city/province.

        CEIC often leaves ``metadata.province`` null and puts the location only in
        ``geo_info`` (e.g. ``CITY: Aceh`` for a province-level series). National
        series only have ``COUNTRY``/``REGION`` entries and stay null.
        """
        name = (meta.get("province") or {}).get("name")
        if name:
            return name
        for geo in meta.get("geo_info") or []:
            if geo.get("type") in ("CITY", "PROVINCE"):
                return geo.get("name")
        return None

    def extract(self) -> Iterator[Dict[str, Any]]:
        if not self.table_id:
            raise ValueError(f"{self.__class__.__name__}: table_id belum diisi")

        client = ApiClient(header_name="Authorization", header_value=self._token)
        layout_api, series_api = LayoutApi(client), SeriesApi(client)

        range_kwargs = {
            key: self.config[key]
            for key in ("start_date", "end_date")
            if self.config.get(key)
        }
        if self.config.get("watermark"):
            range_kwargs["updated_after"] = datetime.fromisoformat(self.config["watermark"])
        language_kwargs = (
            {"accept_language": self._accept_language} if self._accept_language else {}
        )

        for series in self._items(
            self._call(layout_api.get_layout_series, self.table_id, **language_kwargs)
        ):
            meta = series.get("metadata") or {}
            series_id = meta.get("id")
            if series_id is None:
                continue

            rows = self._items(
                self._call(
                    series_api.get_series,
                    series_id,
                    **language_kwargs,
                    **range_kwargs,
                )
            )
            for row in rows:
                for point in row.get("time_points") or []:
                    yield {
                        "table_id": self.table_id,
                        "series_id": series_id,
                        "series_name": meta.get("name"),
                        "unit": (meta.get("unit") or {}).get("name"),
                        "frequency": (meta.get("frequency") or {}).get("name"),
                        "province": self._province(meta),
                        "date": _iso(point.get("date")),
                        "value": point.get("value"),
                        "last_update_time": _iso(point.get("last_update_time")),
                    }
