"""Generic PDF extractor.

Flow for PDF data access:

    Source / landing URL
            |
            v
    resolve PDF download URL (direct or via CSS selector)
            |
            v
    download bytes
            |
            v
    upload to MinIO / S3 on-prem
            |
            v
    yield metadata record (bucket, object_key, etag, size, ...)

PDF text extraction is intentionally out of scope; the destination stores the
binary object, and metadata is emitted for downstream loading if required.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterator
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ...exceptions import ConfigError, SourceUnavailable
from ..base.extractor import BaseExtractor
from ..storage.minio_storage import MinioStorage
from .utils import decode_url


class PdfExtractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.storage = MinioStorage(config)

    def _looks_like_pdf_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return path.endswith(".pdf") or "download" in path and "pdf" in path

    def _resolve_pdf_url(self) -> str:
        pdf_url = self.config.get("pdf_url")
        if pdf_url:
            return decode_url(pdf_url)

        url = self.url
        if self._looks_like_pdf_url(url):
            return decode_url(url)

        selector = self.config.get("selector") or self.config.get("download_selector")
        resp = self.http.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        if selector:
            node = soup.select_one(selector)
            if node and node.get("href"):
                return decode_url(node["href"])
        for link in soup.find_all("a", href=True):
            href = decode_url(link["href"])
            if urlparse(href).path.lower().endswith(".pdf"):
                return href
        raise SourceUnavailable(f"No PDF download link found at {url}")

    def _object_key(self, filename: str, content: bytes) -> str:
        explicit = self.config.get("object_key")
        if explicit:
            return explicit
        prefix = (self.config.get("minio_prefix") or self.config["source"]).strip("/")
        digest = hashlib.sha256(content).hexdigest()[:12]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{prefix}/{stamp}_{digest}_{filename}"

    def extract(self) -> Iterator[Dict[str, Any]]:
        pdf_url = self._resolve_pdf_url()
        resp = self.http.get(pdf_url, timeout=180)
        content = resp.content
        if not content:
            raise SourceUnavailable(f"Empty PDF response from {pdf_url}")

        filename = self.config.get("filename") or urlparse(pdf_url).path.split("/")[-1] or "document.pdf"
        object_key = self._object_key(filename, content)
        content_type = resp.headers.get("Content-Type", "application/pdf")

        meta = self.storage.upload_bytes(content, object_key, content_type)
        record = {
            "usecase": self.config["usecase"],
            "source": self.config["source"],
            "access": "pdf",
            "source_url": self.url,
            "download_url": pdf_url,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "bucket": meta.get("bucket"),
            "object_key": meta.get("object_key"),
            "etag": meta.get("etag"),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
        yield record
