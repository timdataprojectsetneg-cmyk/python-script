# Use Case: pertahanan_dan_keamanan

> Generated from SharePoint catalog `1l7_QKUO57nuvwBqUYqzCondTC_7iccK76Vbryz9mIHI`. Do not edit manually — regenerate with `python -m ingestion.cli docs --usecase pertahanan_dan_keamanan --env <profile>`.

Source count: **3** · eligible for implementation: **3**

## Sources

| # | Source Name | Publisher | Data Access | Update Frequency | Is Official | Eligible | Last Update | Source Link | Resource URL | Data Dictionary |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI) | MA RI | Web Scraping | Daily | Yes | TRUE | 25 Sep 26 | [https://putusan3.mahkamahagung.go.id/search.html?q=PHI&obf=TANGGAL_PUTUS&obm=asc](https://putusan3.mahkamahagung.go.id/search.html?q=PHI&obf=TANGGAL_PUTUS&obm=asc) | - | Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx |
| 2 | Kasus Perselisihan | Kemnaker | Download Excel | Monthly | Yes | TRUE | Juli 2026 | [https://satudata.kemnaker.go.id/data/kumpulan-data/3674](https://satudata.kemnaker.go.id/data/kumpulan-data/3674) | - | Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx |
| 3 | Data Mogok Kerja | Kemnaker | Download Excel | Monthly | Yes | TRUE | Maret 2026 | [https://satudata.kemnaker.go.id/data/kumpulan-data/3616](https://satudata.kemnaker.go.id/data/kumpulan-data/3616) | - | Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx |

## Next steps

1. Scaffold eligible sources: `python -m ingestion.cli docs --usecase pertahanan_dan_keamanan --scaffold`
2. For each source, open `docs/pertahanan_dan_keamanan/dictionary_<source>.md` and copy the Pydantic model into `models.py`.
3. Implement `normalizer.py` (or rely on the generic normalizer validating against `Record`).
4. Implement `<source>/extractor.py` (class `Extractor`), subclassing the generic base.
5. Register the source environment variables and run in DEV mode.
