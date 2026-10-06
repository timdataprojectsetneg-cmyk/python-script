import os
import time
import requests
import pandas as pd

# ====== CONFIG ======
BASE_URL = "https://webapi.bps.go.id/v1/api/list/model/data/lang/eng/domain/0000/var/2261"
API_KEY = os.getenv("BPS_API_KEY", "b17cac7b01320076c0497c5d61dad3ca")

# Tahun di-hardcode: tahun -> kode th BPS (tahun - 1900)
YEARS = {
    2026: 126,
    2025: 125,
    2024: 124,
}

MONTH_COLS = [
    "januari", "februari", "maret", "april", "mei", "juni",
    "juli", "agustus", "september", "oktober", "november", "desember",
]
ALL_COLS = ["provinsi"] + MONTH_COLS + ["tahun"]

# Label bulan BPS (eng & ind) -> nama kolom
MONTH_MAP = {
    "january": "januari", "february": "februari", "march": "maret",
    "april": "april", "may": "mei", "june": "juni", "july": "juli",
    "august": "agustus", "september": "september", "october": "oktober",
    "november": "november", "december": "desember",
    # fallback kalau label berbahasa Indonesia
    "januari": "januari", "februari": "februari", "maret": "maret",
    "mei": "mei", "juni": "juni", "juli": "juli", "agustus": "agustus",
    "oktober": "oktober", "desember": "desember",
}

# Kalau ada beberapa turvar (mis. kelompok pengeluaran), pilih yang labelnya mengandung kata ini.
# Kalau tidak ketemu, dipakai turvar pertama.
TURVAR_PREFERRED = ["general", "umum", "total", "all"]

# Set True kalau baris agregat nasional (INDONESIA) ingin dibuang -> tersisa 38 provinsi
DROP_NATIONAL = False


def fetch_bps(th_code: int, retries: int = 3, timeout: int = 60) -> dict:
    url = f"{BASE_URL}/th/{th_code}/key/{API_KEY}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            last_err = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"Gagal fetch th={th_code}: {last_err}")


def to_float(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", ".")
    if s in ("", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def pick_turvar_id(turvars: list) -> str:
    if not turvars:
        return "0"
    for t in turvars:
        label = str(t["label"]).strip().lower()
        if any(p in label for p in TURVAR_PREFERRED):
            return str(t["val"])
    return str(turvars[0]["val"])


def parse_response(payload: dict, year: int) -> pd.DataFrame:
    if payload.get("status") != "OK" or payload.get("data-availability") != "available":
        print(f"[WARN] {year}: data tidak tersedia -> {payload.get('status')} / {payload.get('data-availability')}")
        return pd.DataFrame(columns=ALL_COLS)

    var_id = str(payload["var"][0]["val"])
    vervar = payload["vervar"]                    # daftar provinsi
    turvars = payload.get("turvar") or []
    tahun_list = payload["tahun"]
    turtahun = payload["turtahun"]                # daftar bulan
    datacontent = payload["datacontent"]

    turvar_id = pick_turvar_id(turvars)

    tahun_id = next(
        (str(t["val"]) for t in tahun_list if str(t["label"]) == str(year)),
        str(tahun_list[0]["val"]),
    )

    # mapping id turtahun -> nama kolom (label non-bulan seperti "Annual" diabaikan)
    turtahun_map = {}
    for t in turtahun:
        label = str(t["label"]).strip().lower()
        if label in MONTH_MAP:
            turtahun_map[str(t["val"])] = MONTH_MAP[label]

    rows = []
    for v in vervar:
        v_id = str(v["val"])
        row = {"provinsi": v["label"], "tahun": str(year)}
        for col in MONTH_COLS:
            row[col] = None
        for tt_id, col in turtahun_map.items():
            key = f"{v_id}{var_id}{turvar_id}{tahun_id}{tt_id}"
            row[col] = to_float(datacontent.get(key))
        rows.append(row)

    df = pd.DataFrame(rows, columns=ALL_COLS)
    if DROP_NATIONAL:
        df = df[~df["provinsi"].str.upper().isin(["INDONESIA"])]
    return df


def main():
    frames = []
    for year, th_code in YEARS.items():
        print(f"Fetching {year} (th={th_code}) ...")
        payload = fetch_bps(th_code)
        df_year = parse_response(payload, year)
        print(f"  -> {len(df_year)} baris")
        frames.append(df_year)

    df = pd.concat(frames, ignore_index=True)
    print(df.head(10))

    df.to_csv("bps_ihk_provinsi.csv", index=False)
    # df.to_json("bps_ihk_provinsi.json", orient="records", force_ascii=False)
    return df


if __name__ == "__main__":
    main()