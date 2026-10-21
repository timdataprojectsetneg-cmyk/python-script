---
name: nifi-python-ingestion
description: Use when working on the NiFi + Python generic ingestion framework (bigaction/python-script/scripts) — adding or editing use cases, publishers, sources or extractors, configuring env vars, generating catalog docs (SharePoint or spreadsheet, per-use-case under docs/<usecase>/), scaffolding modules, or wiring NiFi ExecuteStreamCommand. Covers the folder conventions, {USECASE}__{PUBLISHER}__{SOURCE}__{KEY} env format, connection URIs (PG_URI/ELASTICSEARCH_URL/MINIO_URI), the run/docs/capture CLIs, and common source-specific quirks (satudata SPA, %2520 download URLs, Cloudflare/SOURCE_FILE, PDF→MinIO).
---

# NiFi + Python Generic Ingestion

Framework: **NiFi orchestrates & loads; Python extracts & normalizes.** Python
outputs NDJSON to stdout in production; NiFi `PutDatabaseRecord` writes to
PostgreSQL/Elasticsearch. DEV can write directly via dlt.

Location: `bigaction/python-script/scripts/` (package `ingestion/`; entrypoints
`python -m ingestion` and `run_ingestion.py`).

## Golden rules

1. **Never edit `core/` or `cli.py` to add a use case/source** — only add files
   under `ingestion/usecases/`.
2. **Convention over configuration**: a source is discovered by folder + class
   names (below).
3. **Secrets never in code/logs.** `.env` is published (non-secret only);
   `.env.<profile>` (e.g. `.env.dev`) is gitignored and loaded with `--env dev`.
   PROD Python holds no DB credentials.
4. **Unit tests are optional**; a pytest suite lives in `scripts/tests/unit`
   (`pytest scripts/tests/unit`).

## Ingestion pipeline (3 steps)

Every `python -m ingestion run` executes **three steps in order**, wired in
`cli.py` (`execute_run`):

```
extractor.py  ──▶  normalizer.py  (Pydantic models.py)  ──▶  loader
  (extract)          (normalize / validate)                  (load)
```

1. **Extract** — `resolve_extractor_class(...).extract()` in
   `<source>/extractor.py` yields raw records (`dict`, NDJSON-shaped). The
   extractor owns the whole retrieval chain (scrape → download → parse).
2. **Normalize** — `resolve_normalizer()` uses `<source>/normalizer.py`
   (`class Normalizer`) when present, otherwise `GenericNormalizer`. The generic
   normalizer cleans each record and, when `<source>/models.py` exposes
   `class Record`, validates it with Pydantic
   (`Record(**record).model_dump()`); records that fail validation are logged and
   skipped. **`models.py` is the schema contract for this step.**
   If a source has **neither** a `Normalizer` nor a `Record` (no dictionary/model),
   normalization is **skipped** (records pass through: extractor → load) and a
   WARNING is logged.
3. **Load** — PROD (default) emits NDJSON to stdout for NiFi
   (`PutDatabaseRecord`). Loading **also** runs when a connection URI is present
   (`PG_URI`/`ELASTICSEARCH_URL`/`MINIO_URI` or `--pg-uri`/`--elasticsearch-url`/
   `--minio-uri`) — each URI = one sink — written via
   `PostgresLoader`/`ElasticLoader`/`MinioLoader` (`--use-dlt` switches postgres
   to dlt). PROD Python holds no DB credentials.

## Folder convention

```
ingestion/usecases/<usecase>/<publisher>/<source>/extractor.py   # class Extractor
ingestion/usecases/<usecase>/<publisher>/<source>/models.py      # class Record (optional)
ingestion/usecases/<usecase>/<publisher>/<source>/normalizer.py  # class Normalizer (optional)
```

- Slugs are lower snake_case derived from names: `Kemnaker → kemnaker`,
  `Kasus Perselisihan → kasus_perselisihan`, `The Signal → the_signal`.
- One extractor per source. It is free to combine several retrieval steps
  internally (e.g. scrape a landing page, then download the Excel it links to).
  There is no per-source data-access dimension.
- Missing `normalizer.py` → generic normalizer validates against `models.Record`.
- Template to copy: `ingestion/usecases/example_usecase/example_publisher/example_source/`.

Relative imports: from any source module (`extractor.py`, `normalizer.py`,
`models.py`) use **`.....core...`** (five dots). Sibling modules use `from .models
import Record`.

## Install

- **PROD** (extract + normalize, NDJSON to stdout; no DB clients):
  `pip install -r requirements.txt`.
- **DEV** (loaders postgres/elastic/minio, DB sources, catalog/docs tooling):
  `pip install -r requirements-dev.txt` — it `-r requirements.txt` and adds
  `dlt[postgres]`, `psycopg2-binary`, `elasticsearch`, `sqlalchemy`,
  `google-api-python-client`, `google-auth`.

## Environment variables

Format: `{USECASE}__{PUBLISHER}__{SOURCE}__{KEY}` (upper snake; no access segment).

```
KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL=...
KETENAGAKERJAAN__BPS__BPS_INFLASI_MOM__PAGINATION_TYPE=page
KETENAGAKERJAAN__GOODSTATS__UMK_SUMUT__SOURCE_FILE=./data/umk_sumut.html
```

Common keys: `URL`, `TABLE`, `SCHEMA`, `POSTGRE_SCHEMA`, `POSTGRE_TABLE`,
`ES_INDEX`, `MINIO_BUCKET`, `MINIO_PREFIX`, `OBJECT_KEY`, `SAVE_RAW`,
`API_KEY`, `TOKEN`, `PAGINATION_TYPE`,
`PAGINATION_PARAM`, `DATA_PATH`, `ITEM_SELECTOR`, `FIELDS`, `DOWNLOAD_SELECTOR`,
`DOWNLOAD_URL`, `SOURCE_FILE`, `SHEET`, `HEADER_ROW`, `METHOD`,
`UNIQUE_KEY`, `HTTP_METHOD`, `IMPERSONATE`, `SOURCE_LINK`.

Load method (DEV `postgres`/`elastic` target): `METHOD` is `replace` (default)
or `upsert`; `upsert` requires `UNIQUE_KEY` (comma/semicolon-separated, one or
more columns, default empty). `replace` **drops the table before recreating it**,
so column types and comments always track the current dictionary/extractor result
(a plain truncate would leave stale metadata). For API sources the HTTP verb is
`HTTP_METHOD` (legacy: `METHOD` is still honored when it is a verb like `GET`/`POST`).

The loader sets metadata comments on every load: column comments come from the
Record model's `Field(description=...)`, and the table comment is `SOURCE_LINK`
(falling back to `URL`) from the generated env, e.g.
`COMMENT ON TABLE schema.table IS 'https://.../sumber'`. Regenerate the env with
`docs` after the catalog gains the Source Link column so `SOURCE_LINK` is emitted.

Global (non-namespaced) secrets live directly in `.env.dev` and are read with
`config.get_raw("KEY")`, e.g. `BPS_WEBAPI_KEY` for the BPS WebAPI extractors.

Global **connection URIs** (names matched case-insensitively). When any is set,
`python -m ingestion run` also runs the loader step — **no `--env dev` needed** —
and loads to every sink whose URI is present:

```
PG_URI=postgresql://user:password@host:5432/db
ELASTICSEARCH_URL=http://user:password@host:9200
MINIO_URI=minio://access:secret@host:9000/bucket?secure=true
```

- `ELASTICSEARCH_URL` must match the server scheme (`http` for ES 8 on :9200
  unless TLS is on). The client pins to `elasticsearch>=8,<9` for an ES 8 server.
- MinIO TLS (server missing its chain / internal CA): `MINIO__CA_CERT=/path/bundle.pem`
  (or `?ca_cert=...`); dev-only skip via `?verify=false` / `MINIO__TLS_VERIFY=false`.
- Discrete `MINIO__*` / `DEV__POSTGRES_*` / `ELASTIC__*` still work as fallbacks
  when no URI is set.

## CLI

```bash
# Run one source
python -m ingestion run --usecase ketenagakerjaan --source kasus_perselisihan
# Run every source under a publisher
python -m ingestion run --usecase ketenagakerjaan --publisher kemnaker
# Run a publisher but skip some sources (comma-separated)
python -m ingestion run --usecase ketenagakerjaan --publisher bps --exclude bps_inflasi_yoy,bps_inflasi_mom
# Run all selected sources concurrently (I/O-bound → threads is the good default)
python -m ingestion run --usecase ketenagakerjaan --publisher kemnaker --thread 4
# PROD NDJSON vs direct load (URI present enables loading; each URI = one sink)
python -m ingestion run --usecase ... --source ... --mode dev --env dev
python -m ingestion run --usecase ... --source ... --pg-uri "$PG_URI" --minio-uri "$MINIO_URI"
# Pass a secret/extra source key (JSON) from the orchestrator
python -m ingestion run --usecase ... --source ... --env dev --extra-vars '{"BPS_WEBAPI_KEY":"..."}'

# Docs from the catalog (DOCS_SOURCE: spreadsheet|sharepoint); grouped per use case
python -m ingestion docs --usecase ketenagakerjaan --env dev
python -m ingestion docs --usecase ketenagakerjaan --publisher kemnaker
python -m ingestion docs --usecase ketenagakerjaan --source "Kasus Perselisihan"
python -m ingestion docs --usecase ketenagakerjaan --scaffold   # from local docs, no catalog sync
python -m ingestion docs --usecase ketenagakerjaan --source "Kasus Perselisihan" --scaffold-overwrite
python -m ingestion docs --usecase ketenagakerjaan --delete     # remove docs + module folders/files
python -m ingestion docs --usecase ketenagakerjaan --source "Direktori Putusan PHI" --delete  # one source only
python -m ingestion docs --list    # bare = all; inventory only, no env/credentials needed
python -m ingestion docs --list sources --usecase ketenagakerjaan
```

- The source's single `extractor.py` owns the whole retrieval pipeline.
- Loading happens when a connection URI is present
  (`--pg-uri`/`--elasticsearch-url`/`--minio-uri` or the `PG_URI`/
  `ELASTICSEARCH_URL`/`MINIO_URI` env) or with `--env dev`; each URI = one sink.
  `--use-dlt` uses dlt instead of the direct writer.
- **Concurrency (multiple sources)**: when more than one source is selected (e.g.
  `--usecase X --publisher Y`), `--thread N` runs them with a thread pool — the
  pipeline is I/O-bound, so threads is the right choice. Output is captured per
  source and emitted in selection order, so PROD NDJSON stays valid.
- `run --exclude a,b` drops comma-separated sources from the `--publisher`/
  `--source` selection (name or slug, substring-tolerant), so
  `run --usecase X --publisher Y --exclude s1,s2` skips those sources.
- `--scaffold` creates missing folders/files; `--scaffold-overwrite` replaces
  existing scaffold files, limited to the `--source`/`--publisher` scope (or the
  whole usecase when neither is given).
- Exit codes: `0` ok, `1` ingestion error, `2` config, `3` auth, `4` source
  unavailable. Errors log `file:line (function)`.

## Adding a source — checklist

1. `python -m ingestion docs --usecase <uc> --env dev` (writes the docs), then
   `python -m ingestion docs --usecase <uc> --scaffold` (creates folders for
   **Eligible = true** sources from those local docs; add `--source`/`--publisher`
   to limit the scope and `--scaffold-overwrite` to replace existing files in that
   scope).
   `--scaffold` also refreshes each `models.py` from the dictionary while keeping
   hand-written code; or copy the example source.
2. Fill `models.py` (`class Record`) from the generated
   `docs/<usecase>/dictionary_<source>.md`; map source column names to canonical
   fields with Pydantic `validation_alias=AliasChoices(...)`; add
   `@model_validator(mode="before")` for value transforms (e.g. period→year).
3. Implement `extractor.py` (`class Extractor`) — subclass the generic base
   matching the catalog Data Access (`ExcelExtractor`/`ApiExtractor`/`WebScraper`/
   `PdfExtractor`) and override as needed. For a different sheet layout, override
   `_parse_excel`; to resolve a download link (scrape → download), override
   `_resolve_download_url`.
4. Keep source-specific parsing/selector logic in the source module
   (never in `core/`).
5. Verify: `python -m ingestion run --usecase <uc> --source <src> --limit 5`.

## Example prompts

Setiap permintaan dikerjakan **per modul `usecase/publisher/source`** dan
**tidak menyentuh `core/` atau modul source lain**, sehingga satu source tidak
akan konflik dengan source lain. Semua kode kustom hidup di dalam folder source
itu sendiri (`extractor.py`, `models.py`, `normalizer.py`). Flow selalu 3 langkah:

| Tahap | Pilihan |
|---|---|
| **extractor** | scrapping (landing page → ambil link), download/baca Excel, download PDF → MinIO, panggil API |
| **normalize** | validasi Pydantic lewat `models.py` (field dari `docs/<usecase>/dictionary_<source>.md`) |
| **loaders** | postgres, elastic, minio |

### Template

```
Kerjakan source <usecase>/<publisher>/<source>
(folder: scripts/ingestion/usecases/<usecase>/<publisher>/<source>).
Semua kode kustom HANYA di folder source ini — jangan ubah core/ atau source lain.

1. extractor.py (class Extractor): <scrapping URL landing lalu ambil link excel |
   download & baca Excel | download PDF ke MinIO | panggil API> — <detail selektor/kolom/header>.
2. models.py (class Record): validasi via Pydantic; map kolom sumber → field kanonik
   (AliasChoices). Acuan field: docs/<usecase>/dictionary_<source>.md
   (hasilkan dengan: python -m ingestion docs --usecase <uc> --env dev).
3. loader: <postgres | elastic | minio>.

Verifikasi: python -m ingestion run --usecase <uc> --source <source> --limit 5
```

### Contoh — `ketenagakerjaan/kemnaker/data_mogok_kerja`

```
Kerjakan source bigaction/python-script/scripts/ingestion/usecases/ketenagakerjaan/kemnaker/data_mogok_kerja.
Semua kode kustom HANYA di folder ini — jangan ubah core/ atau source lain.

1. extractor : scrapping URL, kemudian membaca Excel.
2. normalize : validasi dengan models.py
   (bigaction/python-script/scripts/ingestion/usecases/ketenagakerjaan/kemnaker/data_mogok_kerja/models.py),
   field di-consume dari markdown docs/ketenagakerjaan/dictionary_data_mogok_kerja.md
   lewat `python -m ingestion docs --usecase ketenagakerjaan --source data_mogok_kerja --env dev`.
3. loaders : insert PostgreSQL.

Verifikasi: python -m ingestion run --usecase ketenagakerjaan --source data_mogok_kerja --limit 5
```

## Extractor patterns & gotchas

- **Excel (satudata SPA)**: the source sets `DOWNLOAD_SELECTOR` (e.g.
  `bg-satudata-800`); the generic extractor fetches the landing page and finds
  the download link via that selector, with a fallback that scans anchors,
  `data-href` and embedded `.xlsx` URLs. If the page is a JS SPA with no static
  link, set `DOWNLOAD_URL` to the file URL directly.
- **Download URLs with `%2520`**: keep the href **as-is** (raw); `_download()`
  tries raw first then URL-decoded (`%20`). Decoding up-front returns 404.
- **Multi-row / merged headers**: override `_parse_excel` in the source and
  forward-fill merged header cells (see `kemnaker/kasus_perselisihan`,
  `kemnaker/data_mogok_kerja`).
- **Cloudflare-protected sites (e.g. putusan3.mahkamahagung.go.id, goodstats.id)**:
  plain `requests` gets a managed challenge (403 + "Just a moment...") even with a
  fresh `cf_clearance` cookie, because Cloudflare binds the cookie to the browser
  TLS fingerprint. Set `{...}__IMPERSONATE=chrome` (needs `curl_cffi`) so
  the request uses a browser TLS/HTTP2 fingerprint; the MA PHI extractor defaults
  to `chrome` already. Alternatively support `SOURCE_FILE` (saved HTML) and parse a
  scoped container (e.g. `div.statistic-content ol li`).
- **PDF**: the source `extractor.py` downloads and uploads to MinIO/S3, emitting a
  metadata record (bucket, object_key, etag, size, sha256).

## `docs` command behavior

Docs are grouped **per use case** under `docs/<usecase>/` (the flat layout grew
too large). The catalog source is `DOCS_SOURCE` (`spreadsheet` | `sharepoint`),
read from `.env.<profile>` — so run docs with `--env dev` (or set `DOCS_SOURCE`
in `.env`). `docs --list` prints an inventory **without generating anything and
without any credentials/env** (bare `--list` = `all`; or
`--list usecases|publishers|sources|all`).

- Writes `docs/<usecase>/usecase.md` (Sources table + Targets table) and
  `docs/<usecase>/dictionary_<source>.md` per source.
- Dictionary reading **starts** at the header row containing
  `Label, Tipe Data, Satuan, Deskripsi` and **ends** at the first fully-empty
  row; column names are normalized to lower snake_case (`name`).
- One worksheet may stack several dictionary tables: a later table titled
  `Data Dictionary <field>` (with or without a colon) becomes the nested fields
  of that JSON column, e.g. `Data Dictionary Putusan` fills `putusan`. A shared
  workbook may lead with an empty `Summary` sheet; the first sheet holding a
  dictionary is used instead.
- Also writes `docs/<usecase>/usecase.env` with
  `POSTGRE_SCHEMA`, `POSTGRE_TABLE` (`schema.table`), `ES_INDEX`, `MINIO_BUCKET`.
- Only `Eligible = true` sources are structured/scaffolded/env-emitted;
  `--include-ineligible` overrides for dictionaries.
- `--scaffold` / `--scaffold-overwrite` work from the **local** docs
  (`docs/<usecase>/usecase.md` + `dictionary_*.md`): no catalog sync and no
  credentials, so run `docs --usecase <uc> --env dev` first. They scaffold only
  the selected scope (`--source` / `--publisher` / whole usecase) and refresh
  `models.py` from the dictionary field-by-field, preserving hand-written code
  (imports, extra classes, methods, custom field aliases);
  `--scaffold-overwrite` fully replaces existing scaffold files in that scope.
- `--delete` removes the use case docs (`docs/<usecase>/`) and its module folders
  (`ingestion/usecases/<usecase>/`), including hand-written code. With
  `--source` / `--publisher` only the matching `dictionary_<source>.md` and module
  folders/files are removed; `usecase.md` / `usecase.env` stay untouched (source
  matching reads them, so the docs must exist).
- `docs/<usecase>/usecase.env` is auto-loaded by `load_env()` when running that
  use case.

## SharePoint

Read-only via Microsoft Graph. `SHAREPOINT__FILE_ID` (or `CATALOG_PATH`) for the
catalog; Data Dictionary files resolve as
`{SHAREPOINT__DICTIONARY_BASE_PATH}/Data Dictionary - {sheet}/{name}`. Secrets
(`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`) go in `.env.dev`.

Dictionary resolution order (first that works): the cell **hyperlink** when the
catalog has one (decoded to a drive path, else resolved via Graph `/shares`),
then an **item id / explicit path**, then the **cell name** per sheet above.
A link is shared by every source with the same `Data Dictionary` cell text
(e.g. all UMK rows reuse UMK Aceh's link), and the link's `nav` anchor selects
the target worksheet when the source name matches no sheet.

## Spreadsheet

Read-only via the Google Sheets API using a service-account JSON
(`SPREADSHEET__CREDENTIALS_JSON`); `SPREADSHEET__FILE_ID` (or
`GOOGLE__SPREADSHEET_ID`) for the catalog. The `Data Dictionary` cell hyperlink
(a Google Sheets URL) is captured from the grid data and the linked workbook is
read, so one tab may hold several dictionary tables (a `Data Dictionary <field>`
table fills that JSON column) — same behavior as SharePoint.

The linked workbook **must be shared with the service account** (`client_email`
in the credentials JSON, e.g. `python-sheets-reader@<project>.iam.gserviceaccount.com`).
A link that opens in your browser is not enough: API calls run as the
service-account identity, so an unshared workbook fails with `HttpError 403`.

## Combining source & sinks

Source (extractor) and sinks (loaders) are independent; each connection URI adds
a sink, and the same normalized records go to every sink.

- **MinIO → Postgres** (file already in MinIO): set
  `{...}__URL=minio://<bucket>/<key>.xlsx` (connection from `MINIO_URI` or
  `MINIO__*`), then pass `--pg-uri`/`PG_URI` to insert. `ExcelExtractor` reads the
  object bytes directly instead of HTTP.
- **Scrape → download → MinIO + Postgres**: set `{...}__SAVE_RAW=true` so the
  downloaded raw file lands in MinIO (`<minio_prefix|source>/<filename>`), and
  pass `--minio-uri` + `--pg-uri` to land the file and insert the records.
- **Multiple sinks**: pass several URIs (`--pg-uri`, `--minio-uri`,
  `--elasticsearch-url`, or the matching env vars); each one is loaded.

## NiFi wiring

`ExecuteStreamCommand` runs the Python entrypoint. Pass connection URIs **either**
as CLI options (recommended: works directly with NiFi Parameters `#{pg.uri}`)
**or** as process environment variables.

NiFi `ExecuteStreamCommand` properties (Parameters from the Parameter Context,
referenced with `#{...}`):

- Command Path: the venv python
- Command Arguments:
  `run_ingestion.py run --usecase #{usecase} --source #{source} --pg-uri #{pg.uri} --minio-uri #{minio.uri}`
- `Ignore STDIN=true` (the `run` command does not read stdin)

Notes:

- `--pg-uri` / `--elasticsearch-url` / `--minio-uri` **imply their target** (there
  is no `--target`). When any is given the run **also loads** — no `--env dev`
  required. To restrict to a subset, pass only the URIs you want.
- Same URIs also work as env vars `PG_URI`, `ELASTICSEARCH_URL`, `MINIO_URI`
  (case-insensitive). Set them on the NiFi service to keep secrets out of argv.
- Keep secrets out of the repo: use sensitive Parameters (`#{pg.uri}`), pass via
  service env, or an inline `env` wrapper.
- When NiFi owns the load instead, drop the URIs and consume stdout NDJSON →
  `ConvertRecord`/`JsonTreeReader` → `PutDatabaseRecord` + `DBCPConnectionPool`.
- Route on `exit.code` (0 ok, 1/4 retry, 2/3 alert). See `scripts/nifi/README.md`.

Concrete `ExecuteStreamCommand` Command Arguments:

```
run_ingestion.py run --usecase #{usecase} --source #{source} \
  --pg-uri #{pg.uri} --minio-uri #{minio.uri}
```
