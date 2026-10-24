

"""Optional LLM assistance (TDD section 11).

The LLM is *never* required: without the ``openai`` package or without an API
key the module simply reports that it is unavailable and the deterministic
result is returned unchanged.

Only the pages and the context that are really needed are sent, the response is
validated against the dictionary, and every value produced here is tagged with
the ``llm_inferred`` provenance so it can never be mistaken for a printed one.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from .config import LLMConfig
from .models import Dictionary, ExtractionMethod, Provenance

log = logging.getLogger("pdf_extractor.llm")

_SYSTEM = (
    "You extract structured records from a document page. "
    "Return ONLY a JSON object with the key \"records\" holding a list of "
    "objects that use exactly the field names of the supplied schema. "
    "Do not invent values: if a value is not printed on the page, use null."
)


class LLMUnavailable(RuntimeError):
    """Raised when the LLM is enabled but cannot be used."""


def is_available(cfg: LLMConfig) -> bool:
    if not cfg.enabled:
        return False
    try:
        import openai  # noqa: F401
    except ImportError:
        log.warning("LLM diminta tetapi package 'openai' tidak terpasang")
        return False
    return cfg.is_ready()


def _client(cfg: LLMConfig):
    from openai import OpenAI

    kwargs: dict[str, Any] = {"api_key": os.environ.get(cfg.api_key_env)}
    if cfg.base_url:
        kwargs["base_url"] = cfg.base_url
    if cfg.timeout:
        kwargs["timeout"] = cfg.timeout
    return OpenAI(**kwargs)


def build_prompt(
    dictionary: Dictionary,
    marker: str,
    page_texts: dict[int, str],
    max_chars: int = 24_000,
) -> str:
    schema = {
        f.name: {
            "type": f.type,
            "aliases": f.aliases,
            "description": f.description,
            "derived": f.derived,
        }
        for f in dictionary.fields
    }
    pages = []
    budget = max_chars
    for page, text in sorted(page_texts.items()):
        chunk = text[: max(0, min(len(text), budget))]
        budget -= len(chunk)
        pages.append(f"--- page {page} ---\n{chunk}")
        if budget <= 0:
            break
    return (
        f"Marker: {marker}\n\n"
        f"Schema (JSON):\n{json.dumps(schema, ensure_ascii=False, indent=1)}\n\n"
        "Document pages:\n" + "\n".join(pages)
    )


def _parse_response(text: str) -> list[dict[str, Any]]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("respons LLM tidak berisi JSON")
    data = json.loads(m.group(0))
    records = data.get("records") if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("respons LLM tidak berisi daftar record")
    return records


def extract_with_llm(
    dictionary: Dictionary,
    marker: str,
    page_texts: dict[int, str],
    cfg: LLMConfig,
) -> tuple[list[dict[str, Any]], list[Provenance]]:
    """Call the model and return ``(records, provenance)``."""
    if not is_available(cfg):
        raise LLMUnavailable("LLM tidak tersedia (package/env belum siap)")
    client = _client(cfg)
    prompt = build_prompt(dictionary, marker, page_texts, cfg.max_prompt_chars)
    last_error: Exception | None = None
    for attempt in range(cfg.max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=cfg.model,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=cfg.temperature,
            )
            content = response.choices[0].message.content or ""
            records = _parse_response(content)
            break
        except Exception as exc:  # noqa: BLE001 - provider errors are data
            last_error = exc
            log.warning("percobaan LLM ke-%s gagal: %s", attempt + 1, exc)
    else:
        raise LLMUnavailable(f"request LLM gagal: {last_error}")

    known = {f.name for f in dictionary.fields}
    clean: list[dict[str, Any]] = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        clean.append({k: v for k, v in rec.items() if k in known})
    provenance = [
        Provenance(
            page=page, marker=marker, method=ExtractionMethod.LLM,
            confidence=0.7,
            value_sources={k: "llm_inferred" for k in (clean[0] if clean else {})},
            warnings=["nilai dihasilkan LLM, bukan dibaca langsung dari dokumen"],
        )
        for page in sorted(page_texts)
        for _ in range(len(clean) // max(1, len(page_texts)) + (1 if clean else 0))
    ]
    provenance = provenance[: len(clean)]
    return clean, provenance