"""HttpClient impersonation (Cloudflare TLS fingerprint support)."""

import pytest

from ingestion.core.base.http import HttpClient, curl_requests
from ingestion.exceptions import ConfigError


def test_default_client_uses_requests():
    assert HttpClient().session.__class__.__module__.startswith("requests")


@pytest.mark.skipif(curl_requests is None, reason="curl_cffi not installed")
def test_impersonate_uses_curl_cffi():
    client = HttpClient(impersonate="chrome")
    assert client.session.__class__.__module__.startswith("curl_cffi")


def test_impersonate_without_curl_cffi_raises(monkeypatch):
    import ingestion.core.base.http as http

    monkeypatch.setattr(http, "curl_requests", None)
    with pytest.raises(ConfigError):
        HttpClient(impersonate="chrome")
