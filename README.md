# Bigaction - Python Script #

## Getting Started ##
- Masukkan seluruh file python kamu kedalam folder `scripts`
- Untuk menambahkan package, silahkan lakukan `pip freeze > requirements.txt`
- Kemudian, push ke branch yang terhubung dengan pipeline CI/CD (lihat `.gitlab-ci.yml`; job _Build Development_ men-sync `scripts/` dan meng-install `requirements.txt`) dan tunggu hingga instalasi package baru selesai.
- Dependencies dipisah: `requirements.txt` (**prod** — extract + normalize) dan `requirements-dev.txt` (**dev** — loaders/DB sources/docs tooling; berisi `-r requirements.txt`). Untuk package DEV, jangan di-`pip freeze` ke `requirements.txt` — masukkan ke `requirements-dev.txt` agar image prod tetap ramping.

## Bigaction Configuration ##
Untuk mengimplementasi script dalam __Bigaction__, silahkan ikuti petunjuk dibawah:
- Buka & login __Bigaction__: https://bigaction-sitroom.setneg.go.id
- Kemudian, pilih __Processor__ dan ketik/cari `ExecuteStreamCommand`
- Lalu, pada bagian __Properties__, silahkan isi:
  - __Working Directory__: `/opt/nifi/nifi-current/scripts`
  - __Command Path__: `/opt/nifi/nifi-current/venv/bin/python3`
  - __Command Arguments__: `file-python-kamu.py`
- Klik __Apply__ dan script siap digunakan

## Generic Ingestion Framework ##
Selain script standalone, folder `scripts` berisi framework ingestion generik (paket `ingestion/`, entrypoint `run_ingestion.py` / `python -m ingestion`). Framework ini mengikuti konvensi folder `usecases/<usecase>/<publisher>/<source>/<access>/` dan mengeluarkan NDJSON untuk di-load NiFi.

- Dokumentasi lengkap: `scripts/SKILL.md`.
- Menjalankan satu source: `python -m ingestion run --usecase <uc> --source <src> --env dev`.
- Generate docs dari katalog (SharePoint/spreadsheet): `python -m ingestion docs --usecase <uc> --env dev`.
- Scaffold module folders/files dari docs lokal (tanpa sync katalog): `python -m ingestion docs --usecase <uc> --scaffold`.
- Hapus docs + module folders/files usecase: `python -m ingestion docs --usecase <uc> --delete` (batasi ke satu sumber/penerbit dengan `--source` / `--publisher`).
- Wiring NiFi: `scripts/nifi/README.md`.

## Environment Variables ##
Untuk pembuatan dan penggunaan environment variables, dapat dilakukan dengan 2 cara yaitu:
- Non-Confidential variable dapat dimasukkan pada file `./scripts/.env`
- Confidential variable dapat dimasukkan pada processor `ExecuteStreamCommand` dengan cara menambah properti baru

Khusus untuk `.env`, paket `python-dotenv` sudah di-_include_ dalam command python sehingga kamu dapat memanggil env melalui script:
```python
from dotenv import load_dotenv
import os
load_dotenv()

xyz = os.getenv("NAMA_VARIABLE")
```

Untuk variable yang berada pada processor `ExecuteStreamCommand`, dapat dipanggil melalui `os.environ.get('NAMA_VARIABLE')`.