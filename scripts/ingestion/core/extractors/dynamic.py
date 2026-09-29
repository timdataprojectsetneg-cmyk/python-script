"""Render JavaScript-heavy pages with Playwright (soft dependency).

Used by extractors that must read content produced client-side (e.g. React SPAs
like satudata.kemnaker.go.id, where the download link is not in the raw HTML).

Requires: ``pip install playwright`` and ``playwright install chromium``.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from ...exceptions import ConfigError, SourceUnavailable

DEFAULT_WAIT_UNTIL = "networkidle"
DEFAULT_TIMEOUT_MS = 60000


def is_dynamic(value: object) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "y")


def is_missing_browser_error(exc: BaseException) -> bool:
    """True when Playwright has no browser binary installed (setup issue, not source)."""
    detail = str(exc)
    return "Executable doesn't exist" in detail or "playwright install" in detail


def install_hint() -> str:
    """Exact command to install the browser for the current interpreter."""
    cache = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "(default cache)")
    return (
        "Playwright browser is not installed for this interpreter.\n"
        f"  Interpreter : {sys.executable}\n"
        f"  Browsers    : {cache}\n"
        "Install it with the SAME interpreter, e.g.:\n"
        f"  {sys.executable} -m playwright install chromium\n"
        "  (add --with-deps if system libraries are missing; needs sudo on Linux)"
    )


def _launch(pw: object) -> object:
    """Launch chromium, falling back to the full channel build if headless shell is absent."""
    try:
        return pw.chromium.launch()
    except Exception as exc:  # pragma: no cover - browser dependent
        if is_missing_browser_error(exc):
            return pw.chromium.launch(channel="chromium")
        raise


def render_html(
    url: str,
    wait_until: str = DEFAULT_WAIT_UNTIL,
    timeout: int = DEFAULT_TIMEOUT_MS,
    wait_for_selector: Optional[str] = None,
    selector_timeout: int = 30000,
) -> str:
    """Load ``url`` in a headless browser and return the rendered HTML.

    ``wait_for_selector`` is best-effort: if the element never appears (selector
    changed, page blocked, or empty SPA), the rendered HTML is returned anyway so
    the caller can search generically.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on optional package
        raise ConfigError(
            "Dynamic page rendering requires Playwright: "
            "pip install playwright && playwright install chromium"
        ) from exc

    try:
        with sync_playwright() as pw:
            browser = _launch(pw)
            page = browser.new_page()
            try:
                page.goto(url, wait_until=wait_until, timeout=timeout)
                if wait_for_selector:
                    try:
                        page.wait_for_selector(wait_for_selector, timeout=selector_timeout)
                    except Exception:  # noqa: BLE001 - fall through to generic search
                        pass
                return page.content()
            finally:
                browser.close()
    except Exception as exc:  # pragma: no cover - browser/network dependent
        if is_missing_browser_error(exc):
            raise ConfigError(install_hint()) from exc
        raise SourceUnavailable(f"Failed to render dynamic page {url}: {exc}") from exc
