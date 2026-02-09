# Bigaction - Python Script #

## Getting Started ##
- Masukkan seluruh file python kamu kedalam folder `scripts`
- Untuk menambahkan package, silahkan lakukan `pip freeze > requirements.txt`
- Kemudian, push ke branch `master` untuk memulai pipeline CI/CD dan tunggu hingga instalasi package baru selesai.

## Bigaction Configuration ##
Untuk mengimplementasi script dalam __Bigaction__, silahkan ikuti petunjuk dibawah:
- Buka & login __Bigaction__: https://bigaction-sitroom.setneg.go.id
- Kemudian, pilih __Processor__ dan ketik/cari `ExecuteStreamCommand`
- Lalu, pada bagian __Properties__, silahkan isi:
  - __Working Directory__: `/opt/nifi/nifi-current/scripts`
  - __Command Path__: `/opt/nifi/nifi-current/venv/bin/python3`
  - __Command Arguments__: `file-python-kamu.py`
- Klik __Apply__ dan script siap digunakan

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