"""Small parsing helpers shared by extractors."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.parse import unquote


def parse_json_value(value: Any, default: Any) -> Any:
    """Env vars store JSON as text; accept both already-parsed and raw forms."""
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return default
    return default


def parse_headers(value: Any) -> Dict[str, str]:
    return parse_json_value(value, {})


def parse_fields(value: Any) -> List[Dict[str, Any]]:
    return parse_json_value(value, [])


def decode_url(url: str) -> str:
    """Resolve double URL-encoding (``%2520`` -> ``%20``) seen on satudata links."""
    if not url:
        return url
    decoded = unquote(url)
    if "%25" in decoded and decoded != unquote(decoded):
        decoded = unquote(decoded)
    return decoded


def get_path(data: Any, path: Optional[str]) -> Any:
    """Traverse a dotted path such as ``data.items`` or ``result[0].rows``."""
    if not path:
        return data
    current = data
    for part in path.replace("[", ".").replace("]", "").split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if current is None:
            return None
    return current
