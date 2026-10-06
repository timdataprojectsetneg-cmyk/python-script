# Generic Ingestion Framework

NiFi-orchestrated, Python-powered ingestion for Setneg use cases. Python handles
extraction and normalization; NiFi handles scheduling, routing, retry and load to
PostgreSQL / Elasticsearch. See `PRD_NiFi_Python_Ingestion.md` (repository root).

> Existing scripts in this directory (`jdih_*.py`, `rpjmn_*.py`, `sample.py`) are
> untouched. The framework lives in the `ingestion/` package and is invoked via
> `run_ingestion.py`.

## Extractor base classes

Each source has a single `extractor.py` that subclasses the generic base matching
its retrieval method. The base class provides the common mechanics; the source
overrides what it needs.

| Base | Module | Output |
|---|---|---|
| `ExcelExtractor` | `core/extractors/excel_extractor.py` | normalized records |
| `ApiExtractor` | `core/extractors/api_extractor.py` | normalized records |
| `WebScraper` | `core/extractors/web_scraper.py` | normalized records |
| `PdfExtractor` | `core/extractors/pdf_extractor.py` | **binary uploaded to MinIO/S3 on-prem**, metadata record emitted |

PDF flow: source/landing URL → resolve PDF URL → download → upload to MinIO →
emit metadata (bucket, object_key, etag, size, sha256).

A source extractor may combine several retrieval steps internally (e.g. scrape a
landing page, then download the Excel it links to). This lives entirely in the
source's `extractor.py`; there is no per-source access chain or config.

The Excel download-link CSS selector is **not hardcoded in core**: each source
declares it (e.g. `usecases/ketenagakerjaan/kemnaker/kasus_perselisihan/extractor.py`
sets `DOWNLOAD_SELECTOR = "bg-satudata-800"`), overridable via the
`{USECASE}__{PUBLISHER}__{SOURCE}__DOWNLOAD_SELECTOR` env var.

JS-rendered pages require resolving the link from an API or a direct download
URL; the extraction runtime performs static HTTP only.

Each Excel has its own layout, so source-specific parsing overrides `_parse_excel`
in the source's `extractor.py`. The generic extractor handles simple
single-header files.

Downloads try the URL as-is first and fall back to the URL-decoded form, so both
`%20`-literal (double-encoded `%2520`) and normally-encoded paths work.

Some sites are behind bot protection (Cloudflare). For those, sources can accept
a saved page via `{USECASE}__{PUBLISHER}__{SOURCE}__SOURCE_FILE` (local HTML) and parse
it offline; see `usecases/ketenagakerjaan/goodstats/umk_sumut/extractor.py`.

## Usage

```bash
# Markdown reference docs from the SharePoint catalog + Data Dictionary
python -m ingestion.cli docs --usecase ketenagakerjaan
python -m ingestion.cli docs --usecase ketenagakerjaan --source "Kasus Perselisihan"
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev --scaffold

# Run one source
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --mode prod

# Run every source under a publisher
python -m ingestion.cli run --usecase ketenagakerjaan --publisher kemnaker --mode prod

# DEV: load directly to local PostgreSQL/Elastic (the profile enables loading)
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --env dev

# Equivalent flat wrapper (NiFi style)
python run_ingestion.py run --usecase ... --source ... --mode prod
```

### Load method (DEV `postgres` / `elastic` target)

Per source, set `{USECASE}__{PUBLISHER}__{SOURCE}__METHOD`:

- `replace` (default) — replace the target content before writing (PostgreSQL
  `TRUNCATE`, Elasticsearch index delete).
- `upsert` — merge existing rows by `{USECASE}__{PUBLISHER}__{SOURCE}__UNIQUE_KEY`
  (comma/semicolon-separated, one or more columns, default empty). `upsert`
  without a unique key is a config error.

```bash
KETENAGAKERJAAN__KEMNAKER__SATU_DATA_KEMNAKER__METHOD=upsert
KETENAGAKERJAAN__KEMNAKER__SATU_DATA_KEMNAKER__UNIQUE_KEY=id
# multi-column:
# KETENAGAKERJAAN__SOME__SRC__UNIQUE_KEY=provinsi,kota,tahun
```

For API sources the HTTP verb is `...__HTTP_METHOD` (legacy configs using
`METHOD=GET`/`POST` still work).

## Layout

```
ingestion/
├── cli.py              # click CLI: run / sharepoint
├── config.py           # {USECASE}__{PUBLISHER}__{SOURCE}__{KEY} env loader
├── exceptions.py       # exceptions + exit codes 0..4
├── core/
│   ├── base/           # Extractor / Normalizer / Loader / Storage ABCs + HttpClient
│   ├── extractors/     # excel, api, web_scraper, pdf
│   ├── normalizers/    # generic normalizer
│   ├── loaders/        # DEV postgres (dlt) / elastic
│   └── storage/        # MinIO / S3
├── sharepoint/         # Graph API client + Data Dictionary parser
└── usecases/           # per-use-case modules (see example_usecase/README.md)
```

## Adding a use case

Copy `ingestion/usecases/example_usecase/` and follow its README. Only files
under `usecases/` change — never `core/` or `cli.py`.

## Reference docs

`python -m ingestion.cli docs --usecase <usecase>` writes to `docs/`:

- `usecase_<usecase>.md` — source catalog (incl. Is Official, Eligible, Last Update
  and target columns when present), proposed module structure, env vars.
  The Data Dictionary cell is rendered as a hyperlink when SharePoint stores the
  link. Only sources with **`Eligible = true`** appear in the proposed structure
  and env vars; ineligible sources are listed under "Skipped".
- `dictionary_<usecase>_<source>.md` — field table (Label / snake_case Name /
  Tipe Data / Satuan / Deskripsi) + generated Pydantic model. Dictionary reading
  starts at the header row containing `Label, Tipe Data, Satuan, Deskripsi` and
  stops at the first fully-empty row; column names are normalized to lower
  snake_case. Use it as the blueprint for the source's `models.py`.

Sheet reading is header-aware: title/blank rows before the header are skipped, a
two-row header is merged (blank header cells filled from the row below), empty
rows are dropped, and section-title rows (e.g. "Kategori per Data Kemnaker") are
ignored.

### Scaffolding eligible sources

```bash
# docs only (usecase md + dictionaries for eligible sources)
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev

# also create module folders/files for Eligible sources (existing files are skipped)
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev --scaffold

# explicitly regenerate/overwrite existing scaffold files
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev --scaffold --scaffold-overwrite
```

`--scaffold` writes `ingestion/usecases/<usecase>/<publisher>/<source>/{__init__.py,models.py,normalizer.py,extractor.py}`
for every eligible source (the generic base is chosen from the catalog Data
Access). Use `--include-ineligible` to still emit dictionaries for ineligible
sources, and `--source "Kasus Perselisihan"` to limit dictionary generation.

### Long source names / acronyms

`Module Name` (aliases: Folder Name, Alias, Slug) is an optional catalog column.
When set, it becomes the folder/module name; otherwise the slug is derived from
the Source Name (parentheticals dropped, capped at 48 chars on a word boundary).
For long names like "Direktori Putusan Perkara Pengadilan Hubungan Industrial
(Mahkamah Agung RI)", set `Module Name = putusan_phi` — a human-chosen acronym is
more reliable than auto-abbreviation.

Pass `--source "Kasus Perselisihan"` to emit only that source's dictionary;
omit it to emit dictionaries for eligible sources in the use case.

## Configuration & secrets

- Non-confidential config → `.env` (template in `.env.example`). **This file is published to the repo.**
- Confidential values (SharePoint tenant/client/secret, MinIO keys, DB passwords, API keys) → `.env.dev` (gitignored, never published), loaded with `--env dev`. Template in `.env.dev.example`.
- In production, NiFi `ExecuteStreamCommand` sensitive properties supply secrets; PROD Python never holds DB credentials.

```bash
# Load secrets from .env.dev
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --env dev

# --env also works on the group
python -m ingestion.cli --env dev docs --usecase ketenagakerjaan
```

`.env.<profile>` overrides `.env`, so the published file keeps only non-secret defaults.

### SharePoint file references

The client accepts either a **Graph item id** or a **drive-relative path**:

- Item id (preferred): `SHAREPOINT__FILE_ID=01ABCDEF...`. The URL resolves to
  `sites/{SHAREPOINT__SITE_ID}/drive/items/{SHAREPOINT__FILE_ID}` (then `/content`).
  Falls back to `SHAREPOINT__DRIVE_ID` only when `SHAREPOINT__SITE_ID` is unset.
  (`SHAREPOINT__CATALOG_FILE_ID` remains as a legacy alias.)
- Path: `SHAREPOINT__CATALOG_PATH=Folder/Available Data Source.xlsx`.
- Data Dictionary files are resolved per use-case sheet as
  `{SHAREPOINT__DICTIONARY_BASE_PATH}/Data Dictionary - {sheet}/{Data Dictionary Name}`
  (default base `Sitroom-2026/PROJECT/DATA/1 - Discover`). A cell that already holds
  an item id or a full path is used as-is.
- A catalog Data Dictionary cell may also contain a bare item id.
- Force the interpretation with an `id:` prefix, e.g. `--catalog id:01ABCDEF...`.
