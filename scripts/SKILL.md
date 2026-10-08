---
name: nifi-python-ingestion
description: Use when working on the NiFi + Python generic ingestion framework (bigaction/python-script/scripts) — adding or editing use cases, publishers, sources or extractors, configuring env vars, generating SharePoint/module docs, scaffolding modules, or wiring NiFi ExecuteStreamCommand. Covers the folder conventions, {USECASE}__{PUBLISHER}__{SOURCE}__{KEY} env format, the run/docs/capture CLIs, and common source-specific quirks (satudata SPA, %2520 download URLs, Cloudflare/SOURCE_FILE, PDF→MinIO).
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
3. **Load** — PROD (default) emits NDJSON to stdout for NiFi
   (`PutDatabaseRecord`); DEV (`--env dev`) writes directly via
   `PostgresLoader`/`ElasticLoader` (`--use-dlt` switches to dlt). PROD Python
   holds no DB credentials.

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

## Environment variables

Format: `{USECASE}__{PUBLISHER}__{SOURCE}__{KEY}` (upper snake; no access segment).

```
KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL=...
KETENAGAKERJAAN__BPS__BPS_INFLASI_MOM__PAGINATION_TYPE=page
KETENAGAKERJAAN__GOODSTATS__UMK_SUMUT__SOURCE_FILE=./data/umk_sumut.html
```

Common keys: `URL`, `TABLE`, `SCHEMA`, `POSTGRE_SCHEMA`, `POSTGRE_TABLE`,
`ES_INDEX`, `MINIO_BUCKET`, `API_KEY`, `TOKEN`, `PAGINATION_TYPE`,
`PAGINATION_PARAM`, `DATA_PATH`, `ITEM_SELECTOR`, `FIELDS`, `DOWNLOAD_SELECTOR`,
`DOWNLOAD_URL`, `SOURCE_FILE`, `SHEET`, `HEADER_ROW`, `METHOD`,
`UNIQUE_KEY`, `HTTP_METHOD`, `IMPERSONATE`.

Load method (DEV `postgres`/`elastic` target): `METHOD` is `replace` (default)
or `upsert`; `upsert` requires `UNIQUE_KEY` (comma/semicolon-separated, one or
one or
more columns, default empty). `replace` truncates/recreates the target before
writing. For API sources the HTTP verb is `HTTP_METHOD` (legacy: `METHOD` is
still honored when it is a verb like `GET`/`POST`).

Global (non-namespaced) secrets live directly in `.env.dev` and are read with
`config.get_raw("KEY")`, e.g. `BPS_WEBAPI_KEY` for the BPS WebAPI extractors.

## CLI

```bash
# Run one source
python -m ingestion run --usecase ketenagakerjaan --source kasus_perselisihan
# Run every source under a publisher
python -m ingestion run --usecase ketenagakerjaan --publisher kemnaker
# DEV direct-write vs PROD NDJSON
python -m ingestion run --usecase ... --source ... --mode dev --env dev

# Docs from SharePoint catalog + Data Dictionary; optional scaffolding
python -m ingestion docs --usecase ketenagakerjaan --env dev
python -m ingestion docs --usecase ketenagakerjaan --publisher kemnaker
python -m ingestion docs --usecase ketenagakerjaan --source "Kasus Perselisihan"
python -m ingestion docs --usecase ketenagakerjaan --env dev --scaffold
python -m ingestion docs --usecase ketenagakerjaan --source "Kasus Perselisihan" --scaffold-overwrite
```

- The source's single `extractor.py` owns the whole retrieval pipeline.
- DEV loading requires `--env dev` (sets `--mode dev`); `--target` picks the DEV
  sink and `--use-dlt` uses dlt instead of the direct writer.
- `--scaffold` creates missing folders/files; `--scaffold-overwrite` replaces
  existing scaffold files, limited to the `--source`/`--publisher` scope (or the
  whole usecase when neither is given).
- Exit codes: `0` ok, `1` ingestion error, `2` config, `3` auth, `4` source
  unavailable. Errors log `file:line (function)`.

## Adding a source — checklist

1. `python -m ingestion docs --usecase <uc> --scaffold --env dev` (creates
   folders for **Eligible = true** sources; add `--source`/`--publisher` to limit
   the scope and `--scaffold-overwrite` to replace existing files in that scope).
   `--scaffold` also refreshes each `models.py` from the dictionary while keeping
   hand-written code; or copy the example source.
2. Fill `models.py` (`class Record`) from the generated
   `docs/dictionary_<usecase>_<source>.md`; map source column names to canonical
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

- Writes `docs/usecase_<usecase>.md` (Sources table + Targets table) and
  `docs/dictionary_<usecase>_<source>.md` per source.
- Dictionary reading **starts** at the header row containing
  `Label, Tipe Data, Satuan, Deskripsi` and **ends** at the first fully-empty
  row; column names are normalized to lower snake_case (`name`).
- Also writes `docs/usecase_<usecase>.env` with
  `POSTGRE_SCHEMA`, `POSTGRE_TABLE` (`schema.table`), `ES_INDEX`, `MINIO_BUCKET`.
- Only `Eligible = true` sources are structured/scaffolded/env-emitted;
  `--include-ineligible` overrides for dictionaries.
- `--scaffold` scaffolds only the selected scope (`--source` / `--publisher` /
  whole usecase) and refreshes `models.py` from the dictionary field-by-field,
  preserving hand-written code (imports, extra classes, methods, custom field
  aliases). `--scaffold-overwrite` fully replaces existing scaffold files, also
  limited to that scope.
- `docs/usecase_<usecase>.env` is auto-loaded by `load_env()` when running that
  usecase (the generated fragment stays under `docs/`).

## SharePoint

Read-only via Microsoft Graph. `SHAREPOINT__FILE_ID` (or `CATALOG_PATH`) for the
catalog; Data Dictionary files resolve as
`{SHAREPOINT__DICTIONARY_BASE_PATH}/Data Dictionary - {sheet}/{name}`. Secrets
(`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`) go in `.env.dev`.

## NiFi wiring

`ExecuteStreamCommand`: command path the venv python, args
`run_ingestion.py run --usecase ${USECASE} --source ${SOURCE} --mode prod`,
`Ignore STDIN=false`; stdout NDJSON → `ConvertRecord`/`JsonTreeReader` →
`PutDatabaseRecord` + `DBCPConnectionPool`. Route on `exit.code` (0 ok,
1/4 retry, 2/3 alert). See `scripts/nifi/README.md`.
