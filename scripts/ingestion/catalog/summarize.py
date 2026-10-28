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
_SEPARATOR_RE = re.compile(r"\s*\|\s*|\s+[–—-]\s+")
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

# Function words that do not consume one of the ``max_words`` slots.
_COUNT_EXCLUDED_WORDS: Final[frozenset[str]] = _LOWERCASE_TITLE_WORDS | frozenset(
    {
        "per", "terhadap", "menurut", "secara", "bagi", "serta", "maupun",
        "hingga", "sampai", "antara", "tentang", "melalui", "berdasarkan",
        "sesuai", "sebagai", "selama", "tanpa", "setelah", "sebelum",
    }
)

DEFAULT_MAX_WORDS = 8


def _clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\n", " ").replace("\t", " ")
    text = _SPACE_RE.sub(" ", text).strip(" \t\r\n:;,.|–—-")
    return text


_YEAR = re.compile(r"^(?:19|20)\d{2}$|^\d{2}$")


def _is_year_range(text: str, match: re.Match[str]) -> bool:
    """True for dashes between two years, e.g. ``2025 – 2034``.

    Those are ranges inside the title, not separators between a report name and
    the table/chart title. Section numbers such as ``2025 - 3.2.2`` are still
    separators.
    """
    before = text[: match.start()].rstrip().rsplit(maxsplit=1)
    after = text[match.end():].lstrip().split(maxsplit=1)
    if not before or not after:
        return False
    left = before[-1].strip(" ,;.:()")
    right = after[0].strip(" ,;.:()")
    return bool(_YEAR.fullmatch(left) and _YEAR.fullmatch(right))


def _select_main_segment(text: str) -> str:
    """Prefer the last segment in common report-title separators."""
    last_end: int | None = None
    for match in _SEPARATOR_RE.finditer(text):
        separator = match.group(0).strip()
        if separator != "|" and _is_year_range(text, match):
            continue
        last_end = match.end()
    if last_end is not None:
        # The final segment is usually the table/chart/indicator title after
        # organization and report-name prefixes such as "PLN - Sustainability".
        return text[last_end:].strip()
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
            # Capitalise hyphen/dash-joined parts too (Cirebon–Semarang).
            result.append(
                re.sub(
                    r"(^|[–—])(\w)",
                    lambda match: match.group(1) + match.group(2).upper(),
                    word.lower(),
                )
            )
    return " ".join(result)


def _counts_toward_limit(token: str) -> bool:
    """Count only meaningful words; numbers, punctuation and connectors don't count."""
    word = token.strip(" \t.,;:!?()[]{}<>\"'“”‘’|/\\")
    if not re.search(r"[A-Za-zÀ-ÿ]", word):
        return False
    return word.casefold() not in _COUNT_EXCLUDED_WORDS


def meaningful_word_count(text: str) -> int:
    """Number of words that consume a ``max_words`` slot."""
    return sum(1 for token in text.split() if _counts_toward_limit(token))


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

    tokens = result.split()
    if meaningful_word_count(result) > max_words:
        kept: list[str] = []
        counted = 0
        for token in tokens:
            kept.append(token)
            if _counts_toward_limit(token):
                counted += 1
            if counted >= max_words:
                break
        tokens = kept
    return _title_case_indonesian(" ".join(tokens))


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
