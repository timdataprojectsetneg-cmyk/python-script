"""Heuristic summarisation for long catalog names, titles, and table headings.

The catalog contains long source names (often whole table captions).  Slugs are
derived from them, so a long name either gets truncated or produces an
unreadable identifier.  This module keeps the main subject phrase, drops leading
"Tabel/Table/Gambar" noise and trailing qualifiers, and caps the result at a
configurable number of words.

CLI::

    python -m ingestion.catalog.summarize "PLN - Sustainability Report | Volume ..." --max-words 8
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Final

_SPACE_RE = re.compile(r"\s+")
# Report titles commonly use a pipe or a dash to separate organisation/report
# prefixes from the actual table or chart title.
_SEPARATOR_RE = re.compile(r"\s*[|–—]\s*|\s+-\s+")
_WORD_RE = re.compile(r"\S+")

_LEADING_NOISE: Final[tuple[str, ...]] = (
    "tabel", "table", "gambar", "figure", "grafik", "chart", "diagram",
    "lampiran", "attachment", "sumber", "source",
)

# If a title contains a long trailing qualifier, keep the main subject phrase.
_TRAILING_QUALIFIERS: Final[tuple[str, ...]] = (
    " dari pemakaian sumber energi",
    " berdasarkan sumber energi yang digunakan",
)

# These words are normally lowercase in Indonesian title-style output.
_LOWERCASE_TITLE_WORDS: Final[frozenset[str]] = frozenset(
    {"dan", "di", "dari", "ke", "untuk", "pada", "dengan", "atau", "dalam", "oleh", "yang"}
)

DEFAULT_MAX_WORDS = 8


def _clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\n", " ").replace("\t", " ")
    text = _SPACE_RE.sub(" ", text).strip(" \t\r\n:;,.|–—-")
    return text


def _select_main_segment(text: str) -> str:
    """Prefer the last segment in common report-title separators."""
    parts = [_clean_text(part) for part in _SEPARATOR_RE.split(text)]
    parts = [part for part in parts if part]
    if len(parts) > 1:
        # The final segment is usually the table/chart/indicator title after
        # organization and report-name prefixes such as "PLN - Sustainability".
        return parts[-1]
    return text


def _remove_leading_noise(text: str) -> str:
    result = text.strip()
    changed = True
    while changed:
        changed = False
        lowered = result.casefold()
        for prefix in _LEADING_NOISE:
            if lowered.startswith(prefix + " "):
                result = result[len(prefix):].lstrip(" :-–—")
                changed = True
                break
    return result


def _remove_trailing_qualifier(text: str) -> str:
    lowered = text.casefold()
    for phrase in _TRAILING_QUALIFIERS:
        index = lowered.find(phrase)
        # Avoid reducing short phrases unnecessarily. Remove the qualifier
        # only when a meaningful subject precedes it.
        if index > 0 and len(_WORD_RE.findall(text[:index])) >= 2:
            return text[:index].rstrip(" ,;:-")
    return text


def _title_case_indonesian(text: str) -> str:
    words = text.split()
    if not words:
        return ""
    result: list[str] = []
    for index, word in enumerate(words):
        if index > 0 and word.casefold() in _LOWERCASE_TITLE_WORDS:
            result.append(word.casefold())
        elif word.isupper() and len(word) <= 5:
            # Preserve acronyms such as PLN, LNG, and PPU.
            result.append(word)
        else:
            result.append(word[:1].upper() + word[1:].lower())
    return " ".join(result)


def summarize_context(text: str, max_words: int = DEFAULT_MAX_WORDS) -> str:
    """Shorten a report title or table/chart context using simple rules.

    Args:
        text: Original title or context text.
        max_words: Maximum number of words in the result. Must be >= 1.

    Returns:
        A concise title-style phrase. Empty input returns an empty string.

    Notes:
        This is heuristic, language-aware text cleanup, not semantic AI
        summarization. For titles with unusual wording, inspect the result.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(max_words, int) or isinstance(max_words, bool) or max_words < 1:
        raise ValueError("max_words must be an integer >= 1")

    result = _clean_text(text)
    if not result:
        return ""

    result = _select_main_segment(result)
    result = _clean_text(result)
    result = _remove_leading_noise(result)
    result = _remove_trailing_qualifier(result)
    result = _clean_text(result)

    words = _WORD_RE.findall(result)
    if len(words) > max_words:
        words = words[:max_words]
    return _title_case_indonesian(" ".join(words))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ringkas judul/konteks dengan aturan sederhana.")
    parser.add_argument("text", help="Teks judul atau konteks yang ingin diringkas")
    parser.add_argument(
        "--max-words",
        type=int,
        default=DEFAULT_MAX_WORDS,
        help=f"Maksimum kata (default: {DEFAULT_MAX_WORDS})",
    )
    args = parser.parse_args(argv)
    try:
        print(summarize_context(args.text, max_words=args.max_words))
    except (TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
