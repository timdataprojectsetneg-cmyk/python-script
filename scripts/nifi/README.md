# NiFi Integration — Generic Ingestion

This is the production orchestration guide. Apache NiFi is the sole scheduler:
it invokes the Python CLI and consumes its output. The CLI does
**extract → normalize**, and either loads directly (when a connection URI is
given) or emits NDJSON for NiFi to load.

```
Python CLI (extract + normalize)  ──►  NDJSON on stdout  ──►  NiFi (load)
                                  └──►  or direct load via --pg-uri/--elasticsearch-url/--minio-uri
```

## Topology — one Process Group per publisher, one Processor per source

Mirror the use case folder layout (`usecases/<usecase>/<publisher>/<source>/`):

```
NiFi Root Process Group
└── Usecase: ketenagakerjaan (optional grouping PG)
    ├── Process Group: kemnaker            ← publisher
    │   ├── Processor: satu_data_kemnaker  ← source
    │   ├── Processor: kasus_perselisihan
    │   ├── Processor: data_mogok_kerja
    │   └── Processor: kemnaker_perusahaan_wlkp
    ├── Process Group: bps                 ← publisher
    │   ├── Processor: bps_consumer_price_index
    │   ├── Processor: bps_inflasi_mom
    │   └── Processor: bps_inflasi_yoy
    ├── Process Group: goodstats           ← publisher
    │   └── Processor: umk_<provinsi> (x37)
    └── Process Group: ma_ri               ← publisher
        └── Processor: direktori_putusan_perkara_pengadilan_hubungan
```

Rules:
- **One Process Group per publisher.** It owns a **Parameter Context** shared by
  its sources (connection URIs + publisher-level secrets).
- **One Processor (or processor group) per source** inside the publisher group.
- Use `python -m ingestion docs --list all` (below) to enumerate what must exist.

## Inventory — build the flow from the CLI

```bash
# All use cases with publisher/source counts
python -m ingestion docs --list usecases

# Publishers inside one use case
python -m ingestion docs --list publishers --usecase ketenagakerjaan

# Sources of a publisher across every use case
python -m ingestion docs --list sources --publisher bps

# Summary + full tree (usecases → publishers → sources)
python -m ingestion docs --list all
```

## The run command

NDJSON mode (recommended for production — NiFi owns the load):

```bash
python -m ingestion run \
  --usecase ketenagakerjaan \
  --source bps_inflasi_mom \
  --mode prod \
  --extra-vars '{"BPS_WEBAPI_KEY":"xxxxxxxx"}'
```

Direct-load mode (Python writes to the sinks itself; any URI switches the run to
the DEV loader). This is the full form you asked to run from NiFi:

```bash
python -m ingestion run \
  --usecase ketenagakerjaan \
  --source bps_inflasi_mom \
  --pg-uri         'postgresql://setneg-user:secret@192.168.15.16:5432/setneg-stage' \
  --elasticsearch-url 'http://bigspider:secret@192.168.15.16:9200' \
  --minio-uri      'minio://access:secret@minio-api-sitroom.setneg.go.id/raw?secure=true' \
  --extra-vars '{"BPS_WEBAPI_KEY":"xxxxxxxx"}'
```

Only the sinks a source actually declares are written: a source with
`POSTGRE_*` loads to PostgreSQL only, even if `--elasticsearch-url`/`--minio-uri`
are passed. Declared via `ES_INDEX` (Elasticsearch) / `MINIO_BUCKET` (MinIO) /
`POSTGRE_SCHEMA`+`POSTGRE_TABLE` (PostgreSQL).

### Flags

| Flag | Purpose |
|---|---|
| `--usecase` | Use case slug (e.g. `ketenagakerjaan`) |
| `--publisher` | Run every source under a publisher (alternative to `--source`) |
| `--source` | Source slug (e.g. `bps_inflasi_mom`) |
| `--mode prod` | Emit NDJSON (no DB connection). Default. |
| `--pg-uri` | PostgreSQL URI → enables loader, target `postgres` |
| `--elasticsearch-url` | Elasticsearch URL → enables loader, target `elastic` |
| `--minio-uri` | MinIO URI → enables loader, target `minio` |
| `--extra-vars` | Extra per-run variables as a **JSON object**, injected into the process env and read by extractors (e.g. `BPS_WEBAPI_KEY`) |
| `--limit` | Limit records (debug) |
| `--env` | Load secrets from `.env.<profile>` (e.g. `dev`) |
| `--log-level` | `INFO` (default) |

### `--extra-vars` (custom variables)

A JSON object of environment variables for the run. Extractor/normalizer code
reads them with `config.get_raw("<KEY>")`; they override the env profile.
Only key names are logged, never values.

```json
{ "BPS_WEBAPI_KEY": "xxxxxxxx" }
```

Per publisher, typical keys:

| Publisher | Extra vars |
|---|---|
| `bps` | `BPS_WEBAPI_KEY` |
| `ma_ri` | `MA_RI_COOKIE`, `IMPERSONATE` (optional) |
| `kemnaker` | `DOWNLOAD_SELECTOR` overrides (rarely needed) |

> **NiFi note:** `ExecuteStreamCommand` splits arguments on spaces (no shell), so
> write the JSON **without spaces**: `{"BPS_WEBAPI_KEY":"xxxxxxxx"}`. Store it in
> a Parameter Context parameter and reference `${EXTRA_VARS}`.

## ExecuteStreamCommand properties

```
Working Directory : /data/nifi-scripts
Command Path      : /opt/nifi/nifi-current/venv/bin/python3
Command Arguments : -m ingestion run --usecase ${USECASE} --source ${SOURCE} --mode prod --extra-vars "${EXTRA_VARS}"
Ignore STDIN      : false
Argument Delimiter: ' '   (default)
```

The equivalent wrapper entrypoint is `run_ingestion.py`:

```
Command Arguments : run_ingestion.py run --usecase ${USECASE} --source ${SOURCE} --mode prod --extra-vars "${EXTRA_VARS}"
```

`ExecuteStreamCommand` maps the process exit code onto the `exit.code`
attribute, which `RouteOnAttribute` consumes.

## Per-publisher Parameter Context

Create one Parameter Context (assigned to the publisher Process Group) holding
the shared values, e.g. for **bps**:

| Parameter | Sensitive | Value |
|---|---|---|
| `USECASE` | no | `ketenagakerjaan` |
| `PUBLISHER` | no | `bps` |
| `PG_URI` | yes | `postgresql://...` |
| `ELASTICSEARCH_URL` | yes | `http://...` |
| `MINIO_URI` | yes | `minio://...` |
| `EXTRA_VARS` | yes | `{"BPS_WEBAPI_KEY":"xxxxxxxx"}` |

Per-source processors override `SOURCE` in an `UpdateAttribute` (or set it in the
`ExecuteStreamCommand` arguments directly). This lets all sources in a publisher
group share the same Parameter Context.

## Processor chain (inside each source processor)

| Step | Processor | Purpose |
|---|---|---|
| 1 | `GenerateFlowFile` (CRON) | Trigger per Update Frequency (daily/monthly) |
| 2 | `UpdateAttribute` | Set `usecase`, `publisher`, `source`, `ingestion_ts` |
| 3 | `ExecuteStreamCommand` | Invoke the CLI (see above) |
| 4 | `RouteOnAttribute` | Route by `exit.code` |
| 5a | `ConvertRecord` (`JsonTreeReader`/`JsonRecordSetWriter`) | NDJSON → Record |
| 6a | `PutDatabaseRecord` + `DBCPConnectionPool` | Load to PostgreSQL |
| 5b | `RetryFlowFile` / `LogAttribute` | Failure path (retry + Bulletin) |

## RouteOnAttribute rules

```
success : ${exit.code:equals('0')}
retry   : ${exit.code:or(${exit.code:equals('1')}, ${exit.code:equals('4')})}
alert   : ${exit.code:or(${exit.code:equals('2')}, ${exit.code:equals('3')})}
```

## Exit codes

| Code | Meaning | Strategy |
|---|---|---|
| 0 | Success | → ConvertRecord → PutDatabaseRecord |
| 1 | Ingestion error | RetryFlowFile, exponential backoff, 3x |
| 2 | Config error (bad/missing config, e.g. missing API key) | Bulletin alert, no retry |
| 3 | Auth error | Bulletin alert, check token/cookie |
| 4 | Source unavailable | RetryFlowFile, delayed retry, 5x @ 10 min |

## Worked example — `bps/bps_inflasi_mom`

1. Process Group **bps** with Parameter Context `pc-bps`:
   `PG_URI`, `ELASTICSEARCH_URL`, `MINIO_URI`, `EXTRA_VARS={"BPS_WEBAPI_KEY":"..."}`.
2. Inside, processor **bps_inflasi_mom**:
   - `GenerateFlowFile` cron `0 0 1 * *` (monthly).
   - `UpdateAttribute`: `usecase=ketenagakerjaan`, `source=bps_inflasi_mom`.
   - `ExecuteStreamCommand`:
     ```
     Command Arguments: -m ingestion run --usecase ${usecase} --source ${source} --mode prod --extra-vars "${EXTRA_VARS}"
     ```
   - `RouteOnAttribute` → `PutDatabaseRecord` (`raw_bps.inflasi_bulanan`).

If `BPS_WEBAPI_KEY` is missing, the CLI exits **2** with
`Missing BPS WebAPI key...` instead of silently returning 0 rows.

## Direct-load vs NiFi-load

- **Direct-load** (`--pg-uri/--elasticsearch-url/--minio-uri` given): Python writes
  to the sinks; NiFi just triggers and routes on `exit.code`. Simple, but the
  NiFi host must reach the databases.
- **NiFi-load** (`--mode prod` only): Python emits NDJSON to stdout; NiFi parses
  and writes. Keeps DB credentials in NiFi. Recommended for production.

## PDF sources

PDF extractors download the PDF, upload it to MinIO, and emit a metadata record
(bucket, object_key, etag, size, sha256). Route that record to a metadata table
or catalog index.

## Templates

Export the built flows as `templates/ingestion_flow.xml` and
`templates/error_handler_flow.xml` from the NiFi UI once assembled.
