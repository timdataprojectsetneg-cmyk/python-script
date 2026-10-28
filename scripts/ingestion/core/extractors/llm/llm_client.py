"""Chat client used by the document extractor.

Two providers are supported:

- ``openai`` (default): any endpoint that speaks the OpenAI chat-completions
  protocol (``openai`` package).
- ``anthropic``: the official Anthropic SDK (``from anthropic import Anthropic``,
  Messages API). ``base_url`` may point at an Anthropic-compatible gateway; the
  SDK appends ``/v1/messages`` itself.

API keys are read from environment variables only.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Completion", "LLMClient", "LLMSettings", "LLMUnavailable", "parse_json_response"]

log = logging.getLogger("ingestion.llm")


class LLMUnavailable(RuntimeError):
    """Raised when the LLM cannot be used (missing package, model, key or API error)."""


@dataclass
class Completion:
    text: str
    usage: dict[str, Any] = field(default_factory=dict)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


PROVIDERS = ("openai", "anthropic")


@dataclass
class LLMSettings:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    base_url: str | None = None
    api_key_env: str = "LLM_API_KEY"
    timeout: float = 60.0
    max_retries: int = 2
    temperature: float = 0.0
    max_prompt_chars: int = 24_000
    max_images: int = 4
    json_mode: bool = False
    max_tokens: int = 16_000

    @classmethod
    def from_env(cls) -> "LLMSettings":
        return cls(
            provider=(os.environ.get("LLM_PROVIDER") or "openai").strip().lower(),
            model=os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini",
            base_url=os.environ.get("LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or None,
            api_key_env=os.environ.get("LLM_API_KEY_ENV") or "LLM_API_KEY",
            timeout=float(os.environ.get("LLM_TIMEOUT") or 60.0),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES") or 2),
            temperature=float(os.environ.get("LLM_TEMPERATURE") or 0.0),
            max_prompt_chars=int(os.environ.get("LLM_MAX_PROMPT_CHARS") or 24_000),
            max_images=int(os.environ.get("LLM_MAX_IMAGES") or 4),
            json_mode=_env_bool("LLM_JSON_MODE", False),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS") or 16_000),
        )

    def api_key(self) -> str | None:
        fallback = "ANTHROPIC_API_KEY" if self.provider == "anthropic" else "OPENAI_API_KEY"
        return os.environ.get(self.api_key_env) or os.environ.get(fallback)

    def is_ready(self) -> bool:
        return bool(self.model and self.api_key())


class LLMClient:
    def __init__(self, settings: LLMSettings | None = None):
        self.settings = settings or LLMSettings.from_env()

    def _client_kwargs(self) -> dict[str, Any]:
        provider = self.settings.provider
        if provider not in PROVIDERS:
            raise LLMUnavailable(
                f"Unknown LLM provider {provider!r}; expected one of {', '.join(PROVIDERS)}"
            )
        api_key = self.settings.api_key()
        if not api_key:
            fallback = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
            raise LLMUnavailable(
                f"Missing LLM API key: set {self.settings.api_key_env} or {fallback}"
            )
        if not self.settings.model:
            raise LLMUnavailable("Missing LLM_MODEL")
        kwargs: dict[str, Any] = {"api_key": api_key, "timeout": self.settings.timeout}
        if self.settings.base_url:
            kwargs["base_url"] = self.settings.base_url
        return kwargs

    def _client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise LLMUnavailable("The LLM extractor requires the 'openai' package") from exc
        return OpenAI(**self._client_kwargs())

    def _anthropic_client(self):
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise LLMUnavailable(
                "provider 'anthropic' requires the 'anthropic' package (pip install anthropic)"
            ) from exc
        # Retries are handled by ``_with_retries`` for both providers.
        return Anthropic(max_retries=0, **self._client_kwargs())

    @staticmethod
    def _image_part(image: bytes) -> dict[str, Any]:
        encoded = base64.b64encode(image).decode("ascii")
        return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}

    @staticmethod
    def _anthropic_image_part(image: bytes) -> dict[str, Any]:
        encoded = base64.b64encode(image).decode("ascii")
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": encoded},
        }

    @staticmethod
    def _usage(raw_usage: Any) -> dict[str, Any]:
        if raw_usage is None:
            return {}
        return raw_usage.model_dump() if hasattr(raw_usage, "model_dump") else dict(raw_usage)

    def _with_retries(self, call) -> Completion:
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                return call()
            except Exception as exc:  # noqa: BLE001 - provider errors are retried
                last_error = exc
                log.warning("LLM request attempt %s failed: %s", attempt + 1, exc)
                if attempt < self.settings.max_retries:
                    time.sleep(min(2**attempt, 8))
        raise LLMUnavailable(f"LLM request failed: {last_error}")

    def complete(
        self,
        system: str,
        user: str,
        images: list[bytes] | None = None,
    ) -> Completion:
        """Call the model, retrying transient provider errors."""
        if self.settings.provider == "anthropic":
            return self._complete_anthropic(system, user, images)
        return self._complete_openai(system, user, images)

    def _complete_anthropic(
        self,
        system: str,
        user: str,
        images: list[bytes] | None,
    ) -> Completion:
        client = self._anthropic_client()
        content: Any = user
        if images:
            # Images go before the text block, as the Messages API recommends.
            content = [
                self._anthropic_image_part(image) for image in images[: self.settings.max_images]
            ]
            content.append({"type": "text", "text": user})
        if self.settings.json_mode:
            log.debug("json_mode is ignored for provider 'anthropic'; the prompt requests JSON")

        # Sampling parameters (temperature) are not sent: current Claude models
        # reject them. Output format is enforced by the prompt + validator.
        kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": content}],
        }

        def call() -> Completion:
            response = client.messages.create(**kwargs)
            text = "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            )
            return Completion(text=text, usage=self._usage(getattr(response, "usage", None)))

        return self._with_retries(call)

    def _complete_openai(
        self,
        system: str,
        user: str,
        images: list[bytes] | None,
    ) -> Completion:
        client = self._client()
        content: Any = user
        if images:
            content = [{"type": "text", "text": user}]
            content.extend(self._image_part(image) for image in images[: self.settings.max_images])

        kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": content},
            ],
            "temperature": self.settings.temperature,
        }
        if self.settings.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        def call() -> Completion:
            response = client.chat.completions.create(**kwargs)
            message = response.choices[0].message.content or ""
            return Completion(text=message, usage=self._usage(getattr(response, "usage", None)))

        return self._with_retries(call)


def parse_json_response(text: str) -> list[dict[str, Any]]:
    """Extract a record list from an LLM response (plain, fenced, or wrapped)."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("LLM response is empty")

    fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if fenced:
        raw = fenced.group(1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = min((pos for pos in (raw.find("{"), raw.find("[")) if pos >= 0), default=-1)
        if start < 0:
            raise ValueError("LLM response does not contain JSON")
        closing = "}" if raw[start] == "{" else "]"
        end = raw.rfind(closing)
        if end <= start:
            raise ValueError("LLM response contains incomplete JSON")
        data = json.loads(raw[start : end + 1])

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("records", "data", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                records = value
                break
        else:
            records = [data]
    else:
        raise ValueError("LLM response must be a JSON object or array")

    if not all(isinstance(record, dict) for record in records):
        raise ValueError("LLM records must be JSON objects")
    return records
