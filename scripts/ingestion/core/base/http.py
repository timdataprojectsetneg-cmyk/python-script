"""Shared HTTP helper with retry / backoff for extractors."""

from __future__ import annotations

import random
import time
from typing import Any, Dict, Optional

import requests

from ...exceptions import AuthError, ConfigError, SourceUnavailable

try:  # optional: browser-fingerprint HTTP (needed to pass Cloudflare TLS checks)
    from curl_cffi import requests as curl_requests
except ImportError:  # pragma: no cover - curl_cffi is optional
    curl_requests = None


def _request_errors() -> tuple:
    errors = [requests.RequestException]
    if curl_requests is not None:
        curl_error = getattr(curl_requests, "RequestsError", None)
        if isinstance(curl_error, type):
            errors.append(curl_error)
    return tuple(errors)


REQUEST_ERRORS = _request_errors()


class HttpClient:
    def __init__(
        self,
        default_headers: Optional[Dict[str, str]] = None,
        impersonate: Optional[str] = None,
    ):
        self.default_headers = default_headers or {}
        self.impersonate = impersonate
        if impersonate:
            if curl_requests is None:
                raise ConfigError(
                    "IMPERSONATE requires the curl_cffi package (pip install curl_cffi)."
                )
            self.session = curl_requests.Session(impersonate=impersonate)
        else:
            self.session = requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        json: Any = None,
        timeout: int = 30,
        max_retries: int = 4,
        base_sleep: float = 2.0,
    ) -> requests.Response:
        merged = {**self.default_headers, **(headers or {})}
        last_exc: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                resp = self.session.request(
                    method.upper(),
                    url,
                    headers=merged,
                    params=params,
                    data=data,
                    json=json,
                    timeout=timeout,
                )
            except REQUEST_ERRORS as exc:
                last_exc = exc
                wait = min(base_sleep * (2 ** attempt) + random.uniform(0, 1.5), 60)
                time.sleep(wait)
                continue

            if resp.status_code in (401, 403):
                raise AuthError(f"Authentication failed ({resp.status_code}) for {url}")

            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                wait = min(base_sleep * (2 ** attempt) + random.uniform(0, 1.5), 60)
                time.sleep(wait)
                continue

            try:
                resp.raise_for_status()
            except requests.HTTPError as exc:
                raise SourceUnavailable(f"HTTP error for {url}: {exc}") from exc
            return resp

        if last_exc is not None:
            raise SourceUnavailable(f"Unreachable after retries: {url} ({last_exc})")
        raise SourceUnavailable(f"Unavailable after retries: {url}")

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", url, **kwargs)
