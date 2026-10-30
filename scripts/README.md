# Generic Ingestion Framework

NiFi-orchestrated, Python-powered ingestion for Setneg use cases. Python handles
extraction and normalization; NiFi handles scheduling, routing, retry and load to
PostgreSQL / Elasticsearch. Python can also load directly in dev mode (`--env dev` or
`--mode dev`) using the connection URIs (`PG_URI` / `ELASTICSEARCH_URL` / `MINIO_URI`,
or `--pg-uri` / `--elasticsearch-url` / `--minio-uri`), in which case NiFi may instead
just trigger the command. In prod, `PG_URI` only supplies the watermark for incremental
extraction. See `PRD_NiFi_Python_Ingestion.md` (repository root).

> Existing scripts in this directory (`jdih_*.py`, `rpjmn_*.py`, `sample.py`) are
> untouched. The framework lives in the `ingestion/` package and is invoked via
> `run_ingestion.py`.

## Install

Dependencies are split prod vs dev:

```bash
# PROD — extract + normalize (NDJSON to stdout). No DB/loader clients.
pip install -r requirements.txt      # or: uv pip install -r requirements.txt

# DEV — loaders (postgres/elastic/minio), DB sources, catalog/docs tooling.
# Includes prod via `-r requirements.txt`.
pip install -r requirements-dev.txt  # or: uv pip install -r requirements-dev.txt
```

`requirements-dev.txt` adds `dlt[postgres]`, `psycopg2-binary`, `elasticsearch`,
`sqlalchemy`, `google-api-python-client`, `google-auth`.

## Extractor base classes

Each source has a single `extractor.py` that subclasses the generic base matching
its retrieval method. The base class provides the common mechanics; the source
overrides what it needs.

| Base | Module | Output |
|---|---|---|
| `ExcelExtractor` | `core/extractors/excel_extractor.py` | normalized records |
| `ApiExtractor` | `core/extractors/api_extractor.py` | normalized records |
| `WebScraper` | `core/extractors/web_scraper.py` | normalized records |
| `PdfExtractor` | `core/extractors/pdf_extractor.py` | normalized records (table/chart) |
| `LLMExtractor` | `core/extractors/llm_extractor.py` | normalized records (LLM PDF/Excel) |
| `DuckDBExcelExtractor` | `core/extractors/duckdb_extractor.py` | normalized records (manual/curated Excel) |
| `DuckDBJSONExtractor` | `core/extractors/duckdb_extractor.py` | normalized records (manual/curated JSON) |
| `ExcelAutomationExtractor` | `core/extractors/excel_automation_extractor.py` | normalized records (multi-level workbook) |

The PDF engine lives in `core/extractors/pdf/`; the LLM engine in
`core/extractors/llm/`; the DuckDB helpers in `core/extractors/duckdb/`; the
workbook automation engine in `core/extractors/excel_automation/`. The
top-level `*_extractor.py` modules are the stable public/adaptor entry points.

PDF flow: `url`/`pdf_url`/`source_file` (or `minio://bucket/key.pdf`) → download
→ optional raw upload to MinIO (`save_raw=True`) → deterministic table/chart
extraction → records. The engine lives in `core/extractors/pdf/`; every PDF
parameter is passed explicitly (no PDF-specific env vars): a source supplies its
schema (`dictionary=Record`) and a marker, and may override pages/mode:

```python
class Extractor(PdfExtractor):
    def __init__(self, config):
        super().__init__(
            config,                      # optional; only for MinIO settings
            url="https://example.org/handbook.pdf",
            dictionary=Record,           # Pydantic model from models.py
            marker="Primary Energy Supply",
            pages="12",                  # printed or physical (auto-detected)
        )
```

All parameters can also be passed directly (notebooks/scripts):

```python
from ingestion.core.extractors.pdf_extractor import PdfExtractor

extractor = PdfExtractor(
    dictionary="dict.json",              # path, dict, or Pydantic model
    marker="Primary Energy Supply",
    source_file="handbook.pdf",          # or url="https://.../file.pdf"
    pages="12",
    mode="auto",                         # auto|table|chart
    page_numbering="auto",               # auto|physical|printed
)
records = list(extractor.extract())
extractor.result.status                  # success / partial / ...
```

CLI (no env needed, except `--save-raw` which uses MinIO settings):

```bash
python -m ingestion.core.extractors.pdf_extractor handbook.pdf \
  --dictionary dict.json --marker "Primary Energy Supply" --pages 12

# URL + NDJSON output
python -m ingestion.core.extractors.pdf_extractor https://example.org/file.pdf \
  --dictionary dict.json --marker "Indonesia Energy Balance Table 2025" \
  --pages 18-19 --format ndjson -o records.ndjson
```

`save_raw=True` is the only option that reads external settings (MinIO
credentials). PDF files must have a text layer (no OCR). Deterministic extraction
is the default; LLM assistance is optional.

### Manual JSON / Excel sources

Some tables are curated by hand because the PDF/chart is unreliable or would need
an AI pass on every run. Keep the records in a JSON/Excel file and put its
location in the catalog **`Resource URL`** column (it becomes `__URL` in
`usecase.env`). Set **`Data Access`** to `Manual`, `Manual JSON`, `JSON`, etc.;
`docs --scaffold` then generates the extractor from the file extension:

- `.json`/`.jsonl`/`.ndjson` → `DuckDBJSONExtractor`
- `.xlsx`/`.xls`/`.xlsm` → `DuckDBExcelExtractor`
- `.pdf` → `PdfExtractor`

A direct file extension in `Resource URL`/`URL` takes precedence over the
`Data Access` text (so `Web Scraping` + `s3://...json` still uses DuckDB). For
manual sources the dictionary displays the catalog value as-is, e.g.
`Data access: Manual`, even when the engine uses Excel/JSON internally.

Supported locations (handled by `resolve_location`):

- `s3://bucket/key.json` / `minio://bucket/key.json` (MinIO/S3 settings from
  `MINIO_URI` or `MINIO__*`)
- `file:///path/to/data.json`
- local absolute paths, `~`, environment variables, and relative paths
  (macOS, Linux, Windows — `C:\data\x.json` works on Windows)

The file may be an array of objects (the usual manual shape):

```json
[
  {"tahun": 2025, "produk": "Crude Oil", "komponen": "Production", "nilai": 221.2, "satuan": "Million Barrel", "pertumbuhan_yoy_persen": null}
]
```

### LLM document extraction (PDF/Excel)

`core/extractors/llm_extractor.py` (adapter/CLI) and `core/extractors/llm/`
(engine) implement the LLM path. The PDF engine keeps its deterministic first
pass and uses `core/extractors/llm/pdf_assist.py` only for the optional
fallback.

```python
from ingestion.core.extractors.llm import extract_document

result = extract_document(
    "data/energy-statistics-2025.pdf",
    "Ekstrak kapasitas terpasang per jenis pembangkit tahun 2025",
    metadata=Record,          # optional: Pydantic model, dict, or JSON path/string
    page="1-2",               # optional PDF pages (alias: pages="1,3" / "5-8")
)
print(result.status, result.records)
```

- `metadata=None` is permissive: the model proposes a consistent structure.
- With metadata, the contract is sent to the model **and** enforced in Python
  (`validator.py`): required fields, types, enums, nullability.
- Missing values become `null`; values are not guessed or converted without an
  explicit rule. Invalid records are reported and dropped.
- Provider-agnostic: `LLM_MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY` (or
  `OPENAI_MODEL`/`OPENAI_BASE_URL`/`OPENAI_API_KEY` as fallbacks) configure the
  OpenAI-compatible endpoint. `--provider anthropic` (or `LLM_PROVIDER=anthropic`)
  uses the official Anthropic SDK (`from anthropic import Anthropic`,
  `messages.create`) instead; `LLM_BASE_URL` may then point at an
  Anthropic-compatible gateway, the key falls back to `ANTHROPIC_API_KEY`,
  output length is `LLM_MAX_TOKENS`/`--max-tokens` (default 16000), and
  `--temperature`/`--json-mode` are not sent. `--render-images`
  sends rendered pages to a vision-capable model for scanned PDFs.
- Files may be local, `file://`, `s3://`, `minio://`, or HTTP(S); `.xlsx`/`.xls`
  are read per sheet.

CLI — the result is always written (default directory `scripts/out/`):

```bash
# settings from .env.dev (LLM_API_KEY, LLM_MODEL, LLM_BASE_URL, MINIO_URI)
python -m ingestion.core.extractors.llm_extractor report.pdf --env dev \
  --instruction "Ekstrak kapasitas terpasang per jenis pembangkit 2025" \
  --metadata schema.json --page 1-2

# explicit file, local directory, or S3/MinIO prefix
python -m ingestion.core.extractors.llm_extractor report.xlsx --env dev \
  --instruction "Ekstrak tabel ringkasan" -o out/review.json
python -m ingestion.core.extractors.llm_extractor report.pdf --env dev \
  --instruction "Ekstrak ..." -o s3://raw/esdm/

# official Anthropic SDK instead of the OpenAI-compatible client
python -m ingestion.core.extractors.llm_extractor report.pdf --env dev \
  --provider anthropic --instruction "Ekstrak ..." --pages 40
```

`-o/--output` is a single option: a directory (local, or `s3://bucket/prefix/`
/ `minio://bucket/prefix/`) gets `<source-stem>_<UTC timestamp>.<format>`; a
path with an extension is used as-is. S3 output is written with DuckDB
(`core/extractors/duckdb/`, `COPY ... TO 's3://...'`) using the MinIO settings
from `MINIO_URI` or `MINIO__*`. `--env dev` loads `.env` plus `.env.dev`
before reading `LLM_*`. The JSON contains `status`, `records`, `warnings`,
`errors`, and run metadata (model, usage, page count, output path).

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

### Excel automation (multi-level headers + metadata sheets)

`ExcelExtractor` only downloads/reads a file. For workbooks with multi-level or
merged headers, a `Standar Data & Metadata` sheet, and wide/long outputs, use
`ExcelAutomationExtractor`:

```python
class Extractor(ExcelAutomationExtractor):
    def __init__(self, config):
        super().__init__(
            config,
            source=config["url"],     # local, s3://, minio://, http(s)
            output="data",            # data | data_long | ...
            prefix="kemnaker",
        )
```

The parsing engine is split under `core/extractors/excel_automation/` (`grid`,
`metadata`, `tables`, `extraction`, `writers`, `cli`). Historical imports and the
CLI still work:

```python
from ingestion.core.extractors.excel_automation import extract_workbook, tables_to_records
```

```bash
python -m ingestion.core.extractors.excel_automation file.xlsx --out-dir ./out
```

## Usage

```bash
# Markdown reference docs (catalog source via DOCS_SOURCE: spreadsheet|sharepoint).
# Docs are grouped per use case under docs/<usecase>/.
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev
python -m ingestion.cli docs --usecase ketenagakerjaan --source "Kasus Perselisihan" --env dev
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev --scaffold
# Fetch the per-source Data Dictionaries concurrently (I/O-bound)
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev --thread 4
python -m ingestion.cli docs --list    # inventory only (bare = all; no env/credentials needed)
python -m ingestion.cli docs --list sources --usecase ketenagakerjaan

`docs --thread N` fetches dictionaries concurrently; `Fetching dictionary for ...`
and `Wrote ...` are logged as each source finishes (not batched at the end). Only
eligible sources are slugged, so long names on ineligible rows do not emit
truncation warnings.

# Run one source (PROD: NDJSON to stdout for NiFi)
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --mode prod

# Run every source under a publisher
python -m ingestion.cli run --usecase ketenagakerjaan --publisher kemnaker --mode prod
# Run all selected sources concurrently (threads recommended: I/O-bound)
python -m ingestion.cli run --usecase ketenagakerjaan --publisher kemnaker --thread 4

# DEV: load directly (--env dev or --mode dev); each URI adds a sink. There is no --target.
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --env dev
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --mode dev \
  --pg-uri "postgresql://user:pass@postgres:5432/mydb" \
  --minio-uri "minio://access:secret@host:9000/raw?secure=true"

# PROD with PG_URI: NDJSON to stdout; the watermark is read from the target table
python -m ingestion.cli run --usecase ketenagakerjaan --source kasus_perselisihan --mode prod \
  --pg-uri "postgresql://user:pass@postgres:5432/mydb"

# Pass a secret/extra source key from the orchestrator (survives arg quoting)
python -m ingestion.cli run --usecase ketenagakerjaan --source bps_inflasi_mom \
  --env dev --extra-vars '{"BPS_WEBAPI_KEY":"..."}'

# Equivalent flat wrapper (NiFi style)
python run_ingestion.py run --usecase ... --source ... --mode prod
```

### Connection URIs (load targets)

Set `PG_URI`, `ELASTICSEARCH_URL`, `MINIO_URI` (env, case-insensitive) or pass
`--pg-uri` / `--elasticsearch-url` / `--minio-uri`. A URI selects its sink but does not
switch the run to loading. Loading happens in dev mode (`--env dev` or `--mode dev`) and
goes to **every** sink whose URI is present. In prod (default `--mode prod`) the run
emits NDJSON; `PG_URI` there is used only to read the watermark for incremental
extraction (see below).

```
PG_URI=postgresql://user:password@host:5432/db
ELASTICSEARCH_URL=http://user:password@host:9200
MINIO_URI=minio://access:secret@host/bucket?secure=true
```

- `ELASTICSEARCH_URL` must match the server scheme (`http` for ES 8 on :9200
  unless TLS is enabled). The Python client pins to `elasticsearch>=8,<9` to
  match an Elasticsearch 8 server.
- MinIO TLS: if the server does not serve its full chain, set
  `MINIO__CA_CERT=/path/bundle.pem` (or `?ca_cert=...`), or `?verify=false`
  (`MINIO__TLS_VERIFY=false`) for dev.
- Legacy discrete envs (`MINIO__*`, `DEV__POSTGRES_*`, `ELASTIC__*`) still work
  as fallbacks when a URI is not set.

### Load method (DEV `postgres` / `elastic` target)

Per source, set `{USECASE}__{PUBLISHER}__{SOURCE}__METHOD`:

- `replace` (default) — replace the target content before writing (PostgreSQL
  drops/recreates the table, Elasticsearch index delete).
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

### Incremental load (`TIMESTAMP_KEY`)

Optional `{USECASE}__{PUBLISHER}__{SOURCE}__TIMESTAMP_KEY` (default empty; `docs`
preserves it, like `UNIQUE_KEY`).

- Before extraction, the dev loader reads `max(TIMESTAMP_KEY)` from the target table and
  passes it to the extractor as `watermark`. Extractors that support it fetch rows `>=`
  that value, and the upsert merges them by `UNIQUE_KEY`. Currently only the shared CEIC
  extractor (`ceicdata/_ceic.py`) does.
- No `TIMESTAMP_KEY`, `METHOD=replace`, `--full-refresh`, or a missing or empty target
  table means no filter: the full source is fetched.
- The watermark is read in dev mode, or in prod when `PG_URI` is set.
- When `UNIQUE_KEY` and `TIMESTAMP_KEY` are set, their columns are indexed on the target
  table (`CREATE INDEX IF NOT EXISTS`). The unique index is created for `upsert`.
- Date-only timestamps (CEIC `last_update_time` is `YYYY-MM-DD`) re-fetch the boundary
  day on every run; the unique key absorbs the duplicates.

```bash
KETENAGAKERJAAN__CEICDATA__TABEL_ID_GBA_PENGANGGURAN_MENURUT_USIA__METHOD=upsert
KETENAGAKERJAAN__CEICDATA__TABEL_ID_GBA_PENGANGGURAN_MENURUT_USIA__UNIQUE_KEY=series_id,date
KETENAGAKERJAAN__CEICDATA__TABEL_ID_GBA_PENGANGGURAN_MENURUT_USIA__TIMESTAMP_KEY=last_update_time
```

### PostgreSQL metadata columns

`PostgresLoader` (and `DltPostgresLoader`) always adds these lineage columns:

| Column | Type | Source / rule |
|---|---|---|
| `_source` | TEXT | Publisher from `docs/<usecase>/usecase.md` (fallback: publisher slug) |
| `_source_url` | TEXT | Source Link → Resource URL from `usecase.md` (fallback: `source_link`/`url` config) |
| `_published_date` | DATE | Last Update: `YYYY` → `YYYY-01-01`, `YYYY-MM` → `YYYY-MM-01`, full date kept; empty/free text → `NULL` |
| `_created_at` | TIMESTAMP | `CURRENT_TIMESTAMP` on first insert |
| `_modified_at` | TIMESTAMP | `CURRENT_TIMESTAMP` on every load/update |

- On `METHOD=upsert`, `_created_at` is **not** updated; `_modified_at` is.
- `--full-refresh` drops/recreates the table and resets `_created_at`.
- `_loaded_at` and `LOAD_TIMESTAMP_COLUMN` were removed.
- Publisher/Last Update/Source URL are read from `usecase.md`, not duplicated in
  `usecase.env` (only `URL` remains, because extractors need it).
- Existing `usecase.env` files should be regenerated after catalog changes.

## Layout

```
ingestion/
├── cli.py              # click CLI: run / docs (+ --list inventory, --extra-vars)
├── config.py           # {USECASE}__{PUBLISHER}__{SOURCE}__{KEY} env loader + URI helpers
├── exceptions.py       # exceptions + exit codes 0..4
├── catalog/            # source-neutral catalog parsing, doc rendering, scaffolding
├── core/
│   ├── base/           # Extractor / Normalizer / Loader / Storage ABCs + HttpClient
│   ├── extractors/     # excel/api/web_scraper/pdf/text + duckdb/, excel_automation/, llm/
│   ├── normalizers/    # generic normalizer
│   ├── loaders/        # DEV postgres (dlt) / elastic / minio
│   └── storage/        # MinIO / S3 (URI or discrete keys; CA/insecure options)
├── sharepoint/         # Graph API client (catalog source: sharepoint)
├── spreadsheet/        # Google Sheets catalog client (catalog source: spreadsheet)
└── usecases/           # per-use-case modules (see example_usecase/README.md)
```

The catalog **source** is selected by `DOCS_SOURCE` (`sharepoint` | `spreadsheet`),
read only when a profile is loaded (run docs with `--env dev`).

## Adding a use case

Copy `ingestion/usecases/example_usecase/` and follow its README. Only files
under `usecases/` change — never `core/` or `cli.py`.

## Reference docs

`python -m ingestion.cli docs --usecase <usecase> --env dev` writes **per use
case** under `docs/<usecase>/` (the flat layout grew too large):

- `usecase.md` — source catalog (incl. Is Official, Eligible, Last Update and
  target columns when present), proposed module structure, env vars.
  The Data Dictionary cell is rendered as a hyperlink when the catalog stores the
  link. Only sources with **`Eligible = true`** appear in the proposed structure
  and env vars; ineligible sources are listed under "Skipped".
- `usecase.env` — generated `{USECASE}__{PUBLISHER}__{SOURCE}__{KEY}` lines for
  eligible sources (`URL`, targets, `METHOD`, `UNIQUE_KEY`); auto-loaded by
  `load_env()` when running that use case. Publisher, Last Update and Source Link
  are **not** duplicated here — the PostgreSQL loader reads them from
  `usecase.md`.
- `dictionary_<source>.md` — field table (Label / snake_case Name / Tipe Data /
  Satuan / Deskripsi) + generated Pydantic model. Dictionary reading starts at the
  header row containing `Label, Tipe Data, Satuan, Deskripsi` and stops at the
  first fully-empty row; column names are normalized to lower snake_case. Use it
  as the blueprint for the source's `models.py`.

The catalog source is chosen by `DOCS_SOURCE` (`spreadsheet` | `sharepoint`),
which lives in `.env.<profile>` (so run docs with `--env dev`). `docs --list`
prints an inventory **without generating anything and without credentials/env**
(bare `--list` = `all`, or `--list usecases|publishers|sources|all`).

Sheet reading is header-aware: title/blank rows before the header are skipped,
a two-row header is merged (sub-headers win for merged groups, so `Data Engineer`
→ `Raw Data`, `Raw Minio (Bucket)`, …), empty rows are dropped, and section-title
rows (e.g. "Kategori per Data Kemnaker") are ignored.

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
the Source Name: parentheticals dropped, leading section/table numbers removed
(`6.2.9 LPG Supply and Demand` → `lpg_supply_and_demand`), names longer than 8
words summarized, and the result capped at 63 characters on a word boundary. A
warning is logged whenever truncation happens. For long names like
"Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)",
set `Module Name = putusan_phi` — a human-chosen acronym is more reliable than
auto-abbreviation.

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

### MinIO as a source / raw landing

- **Read from MinIO**: `ExcelExtractor` accepts a `minio://<bucket>/<key>.xlsx`
  URL (connection from `MINIO_URI` / `MINIO__*`), reading the object bytes
  directly instead of HTTP.
- **Land the downloaded raw file in MinIO**: set `{...}__SAVE_RAW=true`; the file
  is uploaded under `<MINIO_PREFIX|source>/<filename>` while the parsed records
  continue to the loader.

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
