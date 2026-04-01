from __future__ import annotations

import os
import sys
import json
import time
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple

from tavily import TavilyClient
from openai import OpenAI

logger = logging.getLogger("rpjmn_llm_evaluate")


# ---------------- logging ----------------
def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(lvl)

    h = logging.StreamHandler(stream=sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))

    logger.handlers = [h]


# ---------------- constants ----------------
DEFAULT_FALSE_SUMMARY = (
    "Program belum berjalan, ditunjukkan oleh tidak ditemukannya bukti "
    "pelaksanaan pada 2025. Hasil pencarian 2025 tidak menemukan publikasi "
    "kredibel yang menunjukkan realisasi program tersebut."
)


# ---------------- SQL helpers ----------------
def sql_quote(s: Optional[str]) -> str:
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ---------------- input parsing ----------------
def read_input_rows() -> List[Dict[str, Any]]:
    raw = sys.stdin.read()

    if not raw or not raw.strip():
        return []

    try:
        data = json.loads(raw)
    except Exception:
        cleaned = raw.strip().lstrip("\ufeff")
        data = json.loads(cleaned)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("results", "rows", "data", "records"):
            v = data.get(key)
            if isinstance(v, list):
                return v

    return []


# ---------------- clients ----------------
def get_clients() -> Tuple[TavilyClient, OpenAI]:

    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not tavily_key:
        raise RuntimeError("TAVILY_API_KEY missing")

    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    tavily = TavilyClient(api_key=tavily_key)
    openai = OpenAI(api_key=openai_key)

    return tavily, openai


# ---------------- Tavily search ----------------
def tavily_search(client: TavilyClient, query: str, max_results: int) -> List[Dict]:

    retries = 3

    for i in range(retries):
        try:
            r = client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            return r.get("results", [])
        except Exception as e:
            logger.warning("Tavily retry %s: %s", i + 1, e)
            time.sleep(2)

    return []


# ---------------- LLM evaluation (PROMPT TIDAK DIUBAH) ----------------
def evaluate_program(
    openai_client: OpenAI,
    model: str,
    program: str,
    target: str,
    evidence_text: str
) -> Tuple[bool, str]:

    prompt = f"""
Anda bertindak sebagai evaluator profesional program pemerintah Indonesia.

Tugas Anda menilai apakah program SUDAH DIREALISASIKAN pada tahun 2025.

Program:
{program}

Target 2025:
{target}

Bukti hasil pencarian internet:
{evidence_text}

Aturan penilaian:

Realisasi = true jika:
- Program sudah mulai dilaksanakan pada 2025
- Ada kegiatan implementasi nyata
- Ada progress nyata

Realisasi = false jika:
- Tidak ada bukti implementasi
- Hanya rencana / target / wacana
- Tidak ada berita kegiatan

Aturan penulisan Implementation Summary:

Jika Realisasi = true:
Program berjalan, ditandai dengan <progress implementasi tahun 2025>. Data 2025 menunjukkan <fakta atau angka dari sumber kredibel>.

Jika Realisasi = false:
Program belum berjalan, ditunjukkan oleh tidak ditemukannya bukti pelaksanaan pada 2025. Hasil pencarian 2025 tidak menemukan publikasi kredibel yang menunjukkan realisasi program tersebut.

Output JSON:
{{
  "realisasi": true atau false,
  "implementation_summary": "maksimal dua kalimat sesuai template"
}}
"""

    try:

        resp = openai_client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Anda evaluator kebijakan publik Indonesia."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = json.loads(resp.choices[0].message.content)

        realisasi = bool(result.get("realisasi", False))

        summary = str(
            result.get("implementation_summary", DEFAULT_FALSE_SUMMARY)
        ).strip()

        return realisasi, summary

    except Exception as e:
        logger.error("OpenAI error: %s", e)

        return False, DEFAULT_FALSE_SUMMARY


# ---------------- SQL builder ----------------
def build_bulk_update_sql(rows: List[Tuple]) -> str:

    if not rows:
        return ""

    values = []

    for row_id, realisasi, summary, citations in rows:

        values.append(
            f"({row_id}, {str(realisasi).lower()}, {sql_quote(summary)}, {sql_quote(citations)})"
        )

    values_sql = ",\n".join(values)

    return f"""
UPDATE data_rpjmn.master_rpjmn AS p
SET
    realisasi = v.realisasi,
    implementation_summary = v.summary,
    updated_at = now()
FROM (
    VALUES
{values_sql}
) AS v(id, realisasi, summary)
WHERE p.id = v.id;
"""


# ---------------- main ----------------
def main() -> int:

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--max-results", type=int, default=3)
    ap.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))

    args = ap.parse_args()

    setup_logging(args.log_level)

    rows = read_input_rows()

    if not rows:
        logger.info("No input rows")
        return 0

    tavily, openai_client = get_clients()

    total = len(rows)
    logger.info("Rows to process: %s", total)

    output_rows = []

    for r in rows:

        row_id = r.get("id")

        indikator = str(r.get("indikator", "")).strip()
        sub_indikator = str(r.get("sub_indikator", "")).strip()
        target = str(r.get("target_2025", "")).strip()
        keyword = str(r.get("keyword", "")).strip()

        program = f"{indikator} {sub_indikator}".strip()

        query = f"{program} 2025 Indonesia"

        if keyword:
            query += f" {keyword}"

        search_results = tavily_search(
            tavily,
            query,
            args.max_results
        )

        evidence_text = ""
        urls = []

        for r in search_results:

            url = r.get("url")
            content = r.get("content")

            if url:
                urls.append(url)

            if content:
                evidence_text += content + " "

        if not evidence_text.strip():

            realisasi = False
            summary = DEFAULT_FALSE_SUMMARY

        else:

            realisasi, summary = evaluate_program(
                openai_client,
                args.model,
                program,
                target,
                evidence_text
            )

        citations = "; ".join(urls)

        output_rows.append(
            (row_id, realisasi, summary, citations)
        )

        time.sleep(args.sleep)

    sql = build_bulk_update_sql(output_rows)

    sys.stdout.write(sql + "\n")
    sys.stdout.flush()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)