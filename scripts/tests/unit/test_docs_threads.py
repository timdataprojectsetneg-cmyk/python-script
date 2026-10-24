"""Tests for concurrent Data Dictionary fetching in ``ingestion docs``."""

from __future__ import annotations

import threading

from ingestion import cli
from ingestion.sharepoint import client as sharepoint_client

MATRIX = [
    ["Label", "Tipe Data", "Satuan", "Deskripsi"],
    ["nilai", "Integer", "-", "Nilai contoh"],
]

BARRIER = threading.Barrier(2)
WORKER_THREADS: set[int] = set()


class FakeSharePointClient:
    """Minimal catalog/dictionary client that forces two workers to overlap."""

    def catalog_ref(self, override=None):
        return "catalog"

    def list_sheets(self, ref):
        return {
            "catalog": ["DEMO"],
            "dict_a": ["Source A"],
            "dict_b": ["Source B"],
        }[ref]

    def read_sheet(self, ref, sheet, header_hints=None):
        return [
            {
                "No": 1,
                "Source Name": "Source A",
                "Publisher": "pub",
                "Data Access": "pdf",
                "Eligible": True,
                "Data Dictionary": "dict_a",
            },
            {
                "No": 2,
                "Source Name": "Source B",
                "Publisher": "pub",
                "Data Access": "pdf",
                "Eligible": True,
                "Data Dictionary": "dict_b",
            },
        ]

    def resolve_dictionary_link(self, link, sheet):
        return None

    def dictionary_ref(self, name, sheet):
        return name

    def link_sheet_hint(self, link):
        return None

    def read_matrix(self, ref, sheet):
        WORKER_THREADS.add(threading.get_ident())
        if ref in {"dict_a", "dict_b"}:
            BARRIER.wait(timeout=5)
        return MATRIX


def test_docs_fetches_dictionaries_in_parallel(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCS_SOURCE", raising=False)
    monkeypatch.setattr(sharepoint_client, "SharePointClient", FakeSharePointClient)

    cli._generate_docs("demo", None, str(tmp_path), None, False, None, thread_workers=2)

    docs = tmp_path / "demo"
    first = (docs / "dictionary_source_a.md").read_text(encoding="utf-8")
    second = (docs / "dictionary_source_b.md").read_text(encoding="utf-8")
    assert "nilai" in first and "nilai" in second
    assert (docs / "usecase.md").is_file()
    assert (docs / "usecase.env").is_file()
    assert len(WORKER_THREADS) == 2
