"""Generic REST API extractor with auth, pagination and retry."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from ...exceptions import SourceUnavailable
from ..base.extractor import BaseExtractor
from ..base.http import HttpClient
from .utils import get_path, parse_headers, parse_json_value


class ApiExtractor(BaseExtractor):
    def _headers(self) -> Dict[str, str]:
        headers = parse_headers(self.config.get("headers"))
        token = self.config.get("token")
        api_key = self.config.get("api_key")
        if token:
            headers.setdefault("Authorization", f"Bearer {token}")
        if api_key:
            headers.setdefault("X-API-KEY", api_key)
        return headers

    def _records_from(self, payload: Any) -> List[Dict[str, Any]]:
        data = get_path(payload, self.config.get("data_path"))
        if data is None:
            data = payload
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    data = value
                    break
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def _next_page(self, payload: Any, current_page: int) -> Optional[int]:
        next_path = self.config.get("next_path")
        if next_path:
            nxt = get_path(payload, next_path)
            if nxt in (None, "", False):
                return None
            try:
                return int(nxt)
            except (TypeError, ValueError):
                return None
        if not self.config.get("pagination_param"):
            return None
        return current_page + 1

    def extract(self) -> Iterator[Dict[str, Any]]:
        pagination_type = (self.config.get("pagination_type") or "none").lower()
        param = self.config.get("pagination_param")
        page = int(self.config.get("start_page", 1) or 1)
        max_pages = int(self.config.get("max_pages", 1) or 1)
        page_size = self.config.get("page_size")
        base_params = parse_json_value(self.config.get("params"), {})
        method = (self.config.get("method") or "GET").upper()

        fetched = 0
        while True:
            params = dict(base_params)
            if pagination_type == "page" and param:
                params[param] = page
            elif pagination_type == "offset" and param:
                params[param] = (page - 1) * int(page_size or 100)
                if page_size:
                    params.setdefault("limit", page_size)

            resp = self.http.request(
                method,
                self.url,
                headers=self._headers(),
                params=params if method == "GET" else None,
                json=params if method != "GET" else None,
                timeout=60,
            )
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"Invalid JSON response from {self.url}") from exc

            records = self._records_from(payload)
            for record in records:
                yield record

            if not records:
                break
            fetched += 1
            if pagination_type == "none" or not param:
                break
            if fetched >= max_pages:
                break
            next_page = self._next_page(payload, page)
            if next_page is None:
                break
            page = next_page
