from __future__ import annotations

import os
import sys
import json
import time
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple

from openai import OpenAI

logger = logging.getLogger("jdih_llm_categorize")


# ---------------- logging ----------------
def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(lvl)
    h = logging.StreamHandler(stream=sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.handlers = [h]


# ---------------- categories ----------------
SEKTOR_KEBIJAKAN = {
    "Pangan": ["pangan", "pertanian", "perkebunan", "ketahanan pangan", "petani", "pupuk", "peternakan", "perikanan"],
    "Kesehatan": ["kesehatan", "rumah sakit", "obat", "farmasi", "medis", "dokter", "BPJS kesehatan", "vaksin"],
    "Pendidikan": ["pendidikan", "sekolah", "universitas", "guru", "dosen", "mahasiswa", "kurikulum", "penelitian"],
    "Sosial": ["sosial", "kesejahteraan", "bantuan sosial", "ketenagakerjaan", "tenaga kerja", "upah", "jaminan sosial"],
    "Infrastruktur": ["infrastruktur", "jalan", "jembatan", "transportasi", "perumahan", "telekomunikasi", "internet"],
    "Industri": ["industri", "perdagangan", "ekspor", "impor", "UMKM", "manufaktur", "investasi", "ekonomi"],
    "Energi": ["energi", "listrik", "minyak", "gas", "pertambangan", "lingkungan", "kehutanan", "konservasi"],
    "Birokrasi": ["birokrasi", "pemerintahan", "ASN", "pegawai negeri", "anggaran", "pajak", "audit", "BPK"],
    "Pertahanan": ["pertahanan", "keamanan", "TNI", "militer", "polisi", "hukum", "peradilan", "HAM"],
}

SEKTOR_INVESTASI = {
    "Peternakan": ["peternakan", "sapi", "ayam", "kambing", "domba", "ternak", "kandang", "pakan ternak", "susu", "daging", "unggas"],
    "Perikanan": ["perikanan", "ikan", "tambak", "budidaya ikan", "nelayan", "laut", "udang", "rumput laut", "hasil laut", "kapal ikan"],
    "Pariwisata": ["pariwisata", "wisata", "hotel", "restoran", "destinasi wisata", "objek wisata", "turis", "wisatawan", "perhotelan", "rekreasi"],
    "Mineral": ["mineral", "tambang", "pertambangan", "batubara", "nikel", "tembaga", "emas", "timah", "bauksit", "galian", "minerba"],
    "Agrikultur": ["agrikultur", "pertanian", "perkebunan", "tanaman", "padi", "jagung", "kedelai", "sawit", "karet", "kakao", "kopi", "tebu"],
    "Infrastruktur": ["infrastruktur", "jalan tol", "pelabuhan", "bandara", "jembatan", "bendungan", "irigasi", "pembangunan", "konstruksi", "properti"],
    "Energi Terbarukan": ["energi terbarukan", "energi baru", "solar", "surya", "angin", "panas bumi", "geothermal", "bioenergi", "biodiesel", "hijau", "ramah lingkungan"],
    "Industri": ["industri", "pabrik", "manufaktur", "tekstil", "garmen", "elektronik", "otomotif", "kimia", "farmasi", "makanan", "minuman", "pengolahan"],
    "Lainnya": ["pasar modal", "bursa efek", "saham", "obligasi", "reksadana", "sekuritas", "fintech", "startup", "teknologi", "digital", "e-commerce"],
}


# ---------------- SQL helpers ----------------
def sql_quote(s: Optional[str]) -> str:
    """Postgres SQL string literal (or NULL)."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def sql_text_array(arr: Optional[List[str]]) -> str:
    """Postgres text[] literal using ARRAY[...] with properly quoted string elements."""
    if not arr:
        return "ARRAY[]::text[]"

    items: List[str] = []
    for x in arr:
        if x is None:
            continue
        items.append(sql_quote(str(x)))

    if not items:
        return "ARRAY[]::text[]"

    return "ARRAY[" + ", ".join(items) + "]::text[]"


# ---------------- Input parsing ----------------
def _extract_json_block(text: str) -> str:
    """
    Try to extract the first JSON object/array from text.
    Helps when model returns extra whitespace or accidental text.
    """
    text = text.strip()
    if not text:
        return text

    # strip code fences
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # find first '{' or '[' and last matching '}' or ']'
    first_obj = text.find("{")
    first_arr = text.find("[")
    if first_obj == -1 and first_arr == -1:
        return text

    if first_arr != -1 and (first_obj == -1 or first_arr < first_obj):
        start = first_arr
        end = text.rfind("]")
        return text[start:end + 1] if end != -1 else text[start:]
    else:
        start = first_obj
        end = text.rfind("}")
        return text[start:end + 1] if end != -1 else text[start:]


def read_input_rows() -> List[Dict[str, Any]]:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return []

    try:
        data = json.loads(raw)
    except Exception:
        # if NiFi wraps or adds BOM, attempt a cleanup
        cleaned = raw.strip().lstrip("\ufeff")
        data = json.loads(cleaned)

    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]

    if isinstance(data, dict):
        for key in ("results", "result", "records", "rows", "data"):
            v = data.get(key)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]

    return []


# ---------------- Prompt (ONE CALL: description + categories) ----------------
def create_prompt(regulations: List[Dict[str, Any]]) -> str:
    reg_list = []
    for i, reg in enumerate(regulations, 1):
        tentang = reg.get("tentang") or "N/A"
        if isinstance(tentang, str) and len(tentang) > 220:
            tentang = tentang[:220] + "..."

        desc = reg.get("description")
        if desc is None:
            desc = "NULL"
        elif isinstance(desc, str):
            desc = desc.strip() or "NULL"
            if len(desc) > 220:
                desc = desc[:220] + "..."

        reg_list.append(
            f"""
{i}. ID: {reg.get('id_source')}
   Jenis: {reg.get('jenis','N/A')}
   Nomor: {reg.get('nomor','N/A')} Tahun {reg.get('tahun','N/A')}
   Tentang: {tentang}
   Description existing: {desc}"""
        )

    kebijakan_list = "\n".join([f"- {k}" for k in SEKTOR_KEBIJAKAN.keys()])
    investasi_list = "\n".join([f"- {k}" for k in SEKTOR_INVESTASI.keys()])

    return f"""Kamu adalah ahli hukum Indonesia yang bertugas mengkategorisasi peraturan perundang-undangan.

Kamu harus memproses SEMUA {len(regulations)} peraturan berikut dan mengembalikan:
1) sektor_kebijakan (WAJIB)
2) sektor_investasi (OPSIONAL)
3) description (WAJIB: selalu isi deskripsi singkat 1-2 kalimat Bahasa Indonesia)

PERATURAN:
{chr(10).join(reg_list)}

TUGAS A - SEKTOR KEBIJAKAN (WAJIB, pilih dari daftar ini saja):
{kebijakan_list}

ATURAN sektor_kebijakan:
- Utamakan 1 kategori jika fokusnya jelas
- Maksimal 3 kategori jika lintas sektor
- Jika lebih dari 1, pisahkan dengan koma

TUGAS B - SEKTOR INVESTASI (OPSIONAL, pilih dari daftar ini saja):
{investasi_list}

ATURAN sektor_investasi:
- Isi HANYA jika jelas terkait investasi/penanaman modal
- Jika bukan investasi: gunakan null (literal null, bukan string)

TUGAS C - DESCRIPTION (WAJIB):
- Buat 1-2 kalimat, ringkas, informatif, Bahasa Indonesia
- Jangan bullet/daftar
- Jangan mengarang detail yang tidak ada; kalau info minim, deskripsikan secara umum berdasarkan "tentang" dan metadata

OUTPUT WAJIB JSON VALID (RFC 8259), TANPA TEKS TAMBAHAN, TANPA TRAILING COMMA.
Format:
{{
  "hasil": [
    {{
      "id_source": "ID",
      "sektor_kebijakan": "Kategori" atau "Kategori1, Kategori2",
      "sektor_investasi": "Kategori" atau "Kategori1, Kategori2" atau null,
      "description": "teks deskripsi"
    }}
  ]
}}

WAJIB isi semua ID yang diberikan, dan jangan menambahkan field lain."""


# ---------------- OpenAI client + categorization ----------------
def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing (set it in ExecuteStreamCommand Environment Variables)")

    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def llm_enrich_batch(
    client: OpenAI,
    regs: List[Dict[str, Any]],
    model: str
) -> Dict[str, Tuple[List[str], Optional[List[str]], Optional[str]]]:
    """
    Returns mapping:
      id_source -> (kebijakan_list, investasi_list, description_text_or_none)
    investasi_list uses ["0"] if null/empty/invalid
    """
    prompt = create_prompt(regs)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ahli kategorisasi peraturan Indonesia. Jawab hanya JSON valid."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.25,
        max_tokens=min(len(regs) * 95 + 1400, 16000),
    )

    text = (resp.choices[0].message.content or "").strip()
    text = _extract_json_block(text)

    try:
        data = json.loads(text)
    except Exception:
        logger.error("Failed to parse LLM JSON. Head=%r", text[:400])
        raise

    hasil = data.get("hasil", [])
    valid_k = set(SEKTOR_KEBIJAKAN.keys())
    valid_i = set(SEKTOR_INVESTASI.keys())

    out: Dict[str, Tuple[List[str], List[str], Optional[str]]] = {}

    for item in hasil:
        id_source = item.get("id_source")
        if not id_source:
            continue
        id_source = str(id_source)

        # sektor_kebijakan
        keb = item.get("sektor_kebijakan", "")
        if isinstance(keb, str):
            keb_list = [x.strip() for x in keb.split(",") if x.strip()]
        elif isinstance(keb, list):
            keb_list = [str(x).strip() for x in keb if str(x).strip()]
        else:
            keb_list = []
        keb_list = [x for x in keb_list if x in valid_k]
        if not keb_list:
            keb_list = ["Tidak Terkategorisasi"]

        # sektor_investasi
        inv = item.get("sektor_investasi")
        if inv is None or inv == "" or inv == "null":
            inv_list = None
        else:
            if isinstance(inv, str):
                inv_list = [x.strip() for x in inv.split(",") if x.strip()]
            elif isinstance(inv, list):
                inv_list = [str(x).strip() for x in inv if str(x).strip()]
            else:
                inv_list = []
            inv_list = [x for x in inv_list if x in valid_i]
            if not inv_list:
                inv_list = None

        # description (always attempted, but keep safe)
        desc = item.get("description")
        if isinstance(desc, str):
            desc = desc.strip()
            if not desc:
                desc = None
            elif len(desc) > 1200:
                desc = desc[:1200].rstrip() + "..."
        else:
            desc = None

        out[id_source] = (keb_list, inv_list, desc)

    return out


def to_update_sql(
    id_source: str,
    kebijakan: List[str],
    investasi: Optional[List[str]],
    generated_description: Optional[str] = None
) -> str:

    set_clauses = [
        f"sektor_kebijakan = {sql_text_array(kebijakan)}",
        "updated_at = now()",
    ]

    if not investasi:
        set_clauses.append("sektor_investasi = NULL")
    else:
        set_clauses.append(f"sektor_investasi = {sql_text_array(investasi)}")

    if generated_description and generated_description.strip():
        set_clauses.insert(
            0,
            f"description = COALESCE(NULLIF(description, ''), {sql_quote(generated_description)})"
        )

    return (
        "UPDATE data_jdih.all_produk_hukum\n"
        "SET " + ",\n    ".join(set_clauses) + "\n"
        f"WHERE id_source = {sql_quote(id_source)};"
    )


# ---------------- main ----------------
def main() -> int:
    ap = argparse.ArgumentParser(description="LLM enrich (description + categories) -> output SQL UPDATE for NiFi PutSQL.")
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--batch-size", type=int, default=50)  # safer default
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = ap.parse_args()

    setup_logging(args.log_level)

    regs = read_input_rows()
    if not regs:
        logger.info("No input rows from STDIN. Nothing to do.")
        return 0

    regs = [r for r in regs if r.get("id_source")]
    if not regs:
        logger.info("Input rows exist, but none has id_source. Nothing to do.")
        return 0

    client = get_client()

    total = len(regs)
    logger.info("Rows to enrich: %s (batch_size=%s)", total, args.batch_size)

    sql_out: List[str] = []
    for i in range(0, total, args.batch_size):
        batch = regs[i : i + args.batch_size]
        logger.info("Batch %s-%s / %s", i + 1, min(i + args.batch_size, total), total)

        enriched = llm_enrich_batch(client, batch, args.model)
        if not enriched:
            raise RuntimeError("LLM returned empty enrichment result")

        for r in batch:
            id_source = str(r["id_source"])
            if id_source not in enriched:
                continue
            keb, inv, desc = enriched[id_source]
            sql_out.append(to_update_sql(id_source, keb, inv, desc))

        if i + args.batch_size < total:
            time.sleep(args.delay)

    sys.stdout.write("\n".join(sql_out) + ("\n" if sql_out else ""))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)