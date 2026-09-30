#!/usr/bin/env python3
"""Capture a page's *rendered* HTML to a file for offline scraping.

For Cloudflare/JS-protected pages (e.g. data.goodstats.id) that block automated
fetching, run this locally where you have a real browser:

    python tools/capture_page.py \
        --url https://data.goodstats.id/statistic/daftar-umk-sumatra-utara-2026-kota-medan-naik-8-RCShe \
        --output ./data/umk_sumut.html --headed

Then point the source at the file:

    KETENAGAKERJAAN__GOODSTATS__UMK_SUMUT__SCRAPER__SOURCE_FILE=./data/umk_sumut.html

Two modes:
- default: launches a browser (Playwright). For heavily protected sites use
  ``--cdp`` to attach to your own Chrome instead (no automation flags):
    chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-capture"
    python tools/capture_page.py --cdp http://127.0.0.1:9222 --url <url> --output <file>

Use this instead of "View page source" for client-rendered pages: view-source
shows pre-JavaScript HTML, while this saves the DOM you actually see.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

CHALLENGE_MARKERS = (
    "Performing security verification",
    "Melakukan verifikasi keamanan",
    "Tunggu sebentar",
    "challenges.cloudflare.com",
    "cdn-cgi/challenge-platform",
    "Just a moment",
)


def is_challenge(html: str) -> bool:
    return any(marker in html for marker in CHALLENGE_MARKERS)


def _report(path: Path, html: str) -> None:
    if is_challenge(html):
        print(
            f"[warn] {path} still contains the challenge page — the real page never loaded. "
            "Try CDP mode (--cdp) with your own Chrome, or save the page manually.",
            file=sys.stderr,
        )
    else:
        print(f"[ok] captured {len(html)} bytes -> {path}")


def capture(
    url: str,
    output: str,
    headed: bool = False,
    wait: int = 30,
    timeout: int = 60,
    channel: str | None = None,
    user_agent: str | None = None,
    cdp: str | None = None,
) -> Path:
    from playwright.sync_api import sync_playwright

    html = ""

    if cdp:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(cdp)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            host = urlparse(url).netloc
            page = next((pg for pg in context.pages if host and host in pg.url), None)
            owned = page is None
            if page is None:
                page = context.new_page()
            try:
                if not (host and host in page.url):
                    page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                while True:
                    try:
                        input(
                            "If you still see the verification page, complete it in Chrome, "
                            "then press ENTER here (Ctrl+C to abort)... "
                        )
                    except EOFError:
                        break
                    if not is_challenge(page.content()):
                        break
                    print("Still showing the security/challenge page. Press ENTER again once it clears.")
                html = page.content()
            finally:
                if owned:
                    page.close()  # never close the user's browser
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        _report(path, html)
        return path

    launch_kwargs = {"headless": not headed}
    if channel:
        launch_kwargs["channel"] = channel

    with sync_playwright() as pw:
        browser = pw.chromium.launch(**launch_kwargs)
        context_kwargs = {"locale": "id-ID"}
        if user_agent:
            context_kwargs["user_agent"] = user_agent
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            if headed:
                while True:
                    try:
                        input("Wait until the real page is visible, then press ENTER (Ctrl+C to abort)... ")
                    except EOFError:
                        break
                    if not is_challenge(page.content()):
                        break
                    print("Still showing the security/challenge page. Wait for it to clear, then press ENTER again.")
            else:
                deadline = time.time() + wait
                while time.time() < deadline:
                    if not is_challenge(page.content()):
                        break
                    page.wait_for_timeout(1500)
            html = page.content()
        finally:
            browser.close()

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    _report(path, html)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="Page URL to capture")
    parser.add_argument("--output", required=True, help="Path of the HTML file to write")
    parser.add_argument("--headed", action="store_true", help="Open a visible browser (solve challenges manually)")
    parser.add_argument("--wait", type=int, default=30, help="Seconds to wait for a challenge to clear (headless)")
    parser.add_argument("--timeout", type=int, default=60, help="Navigation timeout in seconds")
    parser.add_argument("--channel", default=None, help="Browser channel, e.g. chrome")
    parser.add_argument("--user-agent", default=None, help="Custom User-Agent")
    parser.add_argument(
        "--cdp",
        default=None,
        help="Attach to your own Chrome via CDP (e.g. http://127.0.0.1:9222) — best for Cloudflare",
    )
    args = parser.parse_args()

    try:
        capture(
            args.url,
            args.output,
            headed=args.headed,
            wait=args.wait,
            timeout=args.timeout,
            channel=args.channel,
            user_agent=args.user_agent,
            cdp=args.cdp,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
