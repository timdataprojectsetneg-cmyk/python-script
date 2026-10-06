import os
import time
import requests
import pandas as pd

# ====== CONFIG ======
BASE_URL = "https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/1"
API_KEY = os.getenv("BPS_API_KEY", "b17cac7b01320076c0497c5d61dad3ca")  # sebaiknya lewat env var

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
ALL_COLS = ["tahun", "kota_inflasi"] + MONTH_COLS + ["tahunan"]


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


def parse_response(payload: dict, year: int) -> pd.DataFrame:
    if payload.get("status") != "OK" or payload.get("data-availability") != "available":
        print(f"[WARN] {year}: data tidak tersedia -> {payload.get('status')} / {payload.get('data-availability')}")
        return pd.DataFrame(columns=ALL_COLS)

    var_id = str(payload["var"][0]["val"])
    vervar = payload["vervar"]                    # daftar kota
    turvars = payload.get("turvar") or []         # biasanya kosong -> id 0
    tahun_list = payload["tahun"]                 # daftar tahun
    turtahun = payload["turtahun"]                # daftar bulan + tahunan
    datacontent = payload["datacontent"]

    turvar_id = str(turvars[0]["val"]) if turvars else "0"

    # cari id tahun yang sesuai
    tahun_id = None
    for t in tahun_list:
        if str(t["label"]) == str(year):
            tahun_id = str(t["val"])
            break
    if tahun_id is None:
        tahun_id = str(tahun_list[0]["val"])

    # mapping id turtahun -> nama kolom
    turtahun_map = {}
    for t in turtahun:
        label = str(t["label"]).strip().lower()
        if label in MONTH_COLS or label == "tahunan":
            turtahun_map[str(t["val"])] = label

    rows = []
    for v in vervar:
        v_id = str(v["val"])
        row = {"tahun": year, "kota_inflasi": v["label"]}
        for col in MONTH_COLS + ["tahunan"]:
            row[col] = None
        for tt_id, col in turtahun_map.items():
            key = f"{v_id}{var_id}{turvar_id}{tahun_id}{tt_id}"
            row[col] = to_float(datacontent.get(key))
        rows.append(row)

    return pd.DataFrame(rows, columns=ALL_COLS)


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

    df.to_csv("bps_inflasi_mtom.csv", index=False)
    # df.to_json("bps_inflasi_mtom.json", orient="records", force_ascii=False)
    return df


if __name__ == "__main__":
    main()