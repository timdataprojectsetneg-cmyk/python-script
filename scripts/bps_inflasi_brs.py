"""
Scrape Berita Resmi Statistik (BRS) inflasi BPS -> CSV.

Kolom output (1 baris per komponen pendorong):
  Periode, Inflasi_YoY, Inflasi_MtM, Basis_Andil (MtM/YoY), Peringkat,
  Komponen_Pendorong, Andil

Alur:
  1. Ambil halaman BRS, parse Periode / YoY / MtM dari teks abstraksi (regex).
  2. Cari link "Unduh Infografik" di HTML.
  3. Unduh infografik, baca dua grafik "Komoditas Penyumbang Utama Andil Inflasi"
     (m-to-m dan y-on-y) dengan:
        --engine ocr  (default, tanpa LLM; pakai RapidOCR + pemetaan posisi)
        --engine llm  (Claude vision; butuh ANTHROPIC_API_KEY)
  4. Bentuk long format (satu baris per komoditas) dan simpan ke CSV.

Catatan: server web-api.bps.go.id melarang akses otomatis (robots). Kalau
download ditolak, unduh gambar manual lalu pakai --image.

Install:
  pip install requests beautifulsoup4 pandas pillow rapidocr-onnxruntime
  pip install anthropic          # hanya untuk --engine llm

Contoh:
  python bps_inflasi_brs.py
  python bps_inflasi_brs.py --image infografik.png
  python bps_inflasi_brs.py --url <URL_BRS> --out inflasi.csv --engine llm
"""
import argparse
import base64
import difflib
import io
import json
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image

DEFAULT_URL = (
    "https://www.bps.go.id/id/pressrelease/2026/09/01/2611/"
    "inflasi-year-on-year--y-on-y--pada-agustus-2026-sebesar-3-19-persen-.html"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; mytens-data-pipeline)"}
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# Kamus nama komoditas untuk memperbaiki salah baca OCR (tambah sesuai kebutuhan).
KNOWN_COMMODITIES = [
    "Daging Ayam Ras", "Telur Ayam Ras", "Cabai Rawit", "Cabai Merah", "Bawang Merah",
    "Bawang Putih", "Ikan Segar", "Beras", "Emas Perhiasan", "Bensin", "Minyak Goreng",
    "Tomat", "Kopi Bubuk", "Gula Pasir", "Tarif Angkutan Udara", "Sigaret Kretek Mesin",
    "Sigaret Kretek Tangan", "Biaya Kuliah Akademi/Perguruan Tinggi", "Daging Sapi",
    "Bawang Merah", "Kentang", "Wortel", "Jeruk", "Apel", "Pisang", "Mie Kuah",
    "Nasi Dengan Lauk", "Air Kemasan", "Tarif Listrik", "Kontrakan Rumah", "Upah Asisten Rumah Tangga",
]

VISION_PROMPT = """Ini infografik BPS tentang perkembangan IHK.
Baca dua grafik batang "Komoditas Penyumbang Utama Andil Inflasi (atau Deflasi)":
kiri = m-to-m, kanan = y-on-y. Urutkan dari kiri ke kanan seperti di gambar.
Balas HANYA JSON valid (tanpa teks lain, tanpa markdown) dengan bentuk:
{"mtm": [{"komoditas": "Daging Ayam Ras", "andil": 0.17}],
 "yoy": [{"komoditas": "Emas Perhiasan", "andil": 0.53}]}
Gunakan titik sebagai desimal. Nilai negatif (andil deflasi) ditulis dengan tanda minus."""

NUM = re.compile(r"^-?\d+[.,]\d+$")


# ---------- helpers ----------
def to_num(s: str, negative: bool = False) -> float:
    s = s.strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    v = float(s)
    return -v if negative else v


def get_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.text


def parse_brs(html: str) -> dict:
    """Ambil Periode, YoY, MtM dari teks abstraksi."""
    text = re.sub(r"\s+", " ", BeautifulSoup(html, "html.parser").get_text(" "))

    m = re.search(
        r"Pada ([A-Za-z]+ \d{4}), terjadi (inflasi|deflasi) year-on-year \(y-on-y\) "
        r"sebesar ([\d.,]+) persen",
        text, re.I,
    )
    if not m:
        raise ValueError("Pola YoY tidak ditemukan di halaman BRS.")
    periode, jenis, yoy = m.group(1), m.group(2).lower(), m.group(3)

    mm = re.search(
        r"(inflasi|deflasi) month-to-month \(m-to-m\).*?sebesar ([\d.,]+) persen",
        text, re.I,
    )
    if not mm:
        raise ValueError("Pola MtM tidak ditemukan di halaman BRS.")

    return {
        "Periode": periode,
        "Inflasi_YoY": to_num(yoy, jenis == "deflasi"),
        "Inflasi_MtM": to_num(mm.group(2), mm.group(1).lower() == "deflasi"),
    }


def find_infographic_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if "unduh infografik" in a.get_text(" ", strip=True).lower():
            return a["href"]
    m = re.search(r'href="([^"]+)"[^>]*>\s*Unduh Infografik', html, re.I)
    return m.group(1).replace("&amp;", "&") if m else None


def load_image_bytes(source: str | None, url: str | None) -> bytes:
    if source:
        with open(source, "rb") as f:
            return f.read()
    r = requests.get(url, headers=HEADERS, timeout=120)
    r.raise_for_status()
    return r.content


# ---------- engine 1: OCR (tanpa LLM) ----------
def _clean_name(words: list[str]) -> str:
    raw = " ".join(words).strip()
    key = re.sub(r"\s+", "", raw).lower()
    known = {re.sub(r"\s+", "", k).lower(): k for k in KNOWN_COMMODITIES}
    hit = difflib.get_close_matches(key, list(known), n=1, cutoff=0.8)
    return known[hit[0]] if hit else raw


def read_infographic_ocr(raw: bytes) -> dict:
    from rapidocr_onnxruntime import RapidOCR

    result, _ = RapidOCR()(raw)
    if not result:
        raise RuntimeError("OCR tidak menemukan teks.")

    items = []
    for box, txt, _conf in result:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        items.append({"t": txt.strip(), "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys)})
    for i in items:
        i["cx"] = (i["x0"] + i["x1"]) / 2
        i["cy"] = (i["y0"] + i["y1"]) / 2

    # judul dua panel & batas bawah seksi (judul grafik tren y-on-y)
    heads, section_end = {}, None
    for i in items:
        tl = i["t"].lower().replace(" ", "")
        if "andil" in tl and "m-to-m" in tl:
            heads["mtm"] = i
        elif "andil" in tl and "y-on-y" in tl:
            heads["yoy"] = i
        elif "tingkat" in tl and "year" in tl and section_end is None:
            section_end = i["y0"]
    if len(heads) != 2:
        raise RuntimeError("Judul panel 'Andil Inflasi' tidak ditemukan; layout berubah?")
    section_end = section_end or max(h["y1"] for h in heads.values()) + 900
    split_x = (heads["mtm"]["cx"] + heads["yoy"]["cx"]) / 2

    out = {}
    for key, head in heads.items():
        in_panel = [
            i for i in items
            if head["y1"] < i["cy"] < section_end
            and ((i["cx"] < split_x) == (key == "mtm"))
        ]
        values = sorted((i for i in in_panel if NUM.match(i["t"])), key=lambda i: i["cx"])
        labels = [i for i in in_panel if not NUM.match(i["t"])]
        cols = {id(v): [] for v in values}
        for lb in labels:
            v = min(values, key=lambda v: abs(v["cx"] - lb["cx"]), default=None)
            if v is not None and abs(v["cx"] - lb["cx"]) < 120:
                cols[id(v)].append(lb)
        out[key] = [
            {
                "komoditas": _clean_name([w["t"] for w in sorted(cols[id(v)], key=lambda w: w["cy"])]),
                "andil": to_num(v["t"]),
            }
            for v in values
        ]
    if not out["mtm"] or not out["yoy"]:
        raise RuntimeError("Gagal memetakan komoditas; cek manual atau pakai --engine llm.")
    return out


# ---------- engine 2: LLM vision ----------
def read_infographic_llm(raw: bytes) -> dict:
    import anthropic

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((2000, 2800))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode()

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": VISION_PROMPT},
            ],
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def fmt(items: list) -> str:
    return ", ".join(f"{i['komoditas']} ({i['andil']:.2f})" for i in items)


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--image", help="path infografik lokal (lewati download gambar)")
    ap.add_argument("--engine", choices=["ocr", "llm"], default="ocr")
    ap.add_argument("--out", default="bps_inflasi_brs.csv")
    args = ap.parse_args()

    html = get_html(args.url)
    row = parse_brs(html)
    print(f"[OK] {row}")

    info_url = None if args.image else find_infographic_url(html)
    if not args.image and not info_url:
        raise RuntimeError("Link 'Unduh Infografik' tidak ditemukan; pakai --image.")
    if info_url:
        print(f"[OK] infografik: {info_url}")

    raw = load_image_bytes(args.image, info_url)
    reader = read_infographic_ocr if args.engine == "ocr" else read_infographic_llm
    comp = reader(raw)
    print(f"[OK] komponen ({args.engine}): {comp}")

    rows = []
    for basis, key in (("MtM", "mtm"), ("YoY", "yoy")):
        for rank, item in enumerate(comp[key], start=1):
            rows.append({
                **row,
                "Basis_Andil": basis,
                "Peringkat": rank,
                "Komponen_Pendorong": item["komoditas"],
                "Andil": item["andil"],
            })

    cols = ["Periode", "Inflasi_YoY", "Inflasi_MtM", "Basis_Andil",
            "Peringkat", "Komponen_Pendorong", "Andil"]
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(args.out, index=False)
    print(df.to_string(index=False))
    return df


if __name__ == "__main__":
    main()