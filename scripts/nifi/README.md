# NiFi Integration — Generic Ingestion

This is the production orchestration guide. Apache NiFi is the sole scheduler:
it invokes the Python CLI and consumes its output. The CLI does
**extract → normalize**, then either **loads directly** (when a sink URI is
given) or **emits NDJSON** for NiFi to load.

```
Python CLI (extract + normalize)
  ├─ with --pg-uri / --elasticsearch-url / --minio-uri ──►  direct load  (no PutDatabaseRecord)
  └─ without sink URIs ─────────────────────────────────►  NDJSON stdout ──►  NiFi load (PutDatabaseRecord/…)
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

## Integration options

Pick **one** per source. The deciding factor is whether a sink URI is passed to
the CLI:

| | Option A — Direct execute | Option B — NiFi load |
|---|---|---|
| CLI arguments | `--pg-uri` / `--elasticsearch-url` / `--minio-uri` present | no sink URIs (`--mode prod`) |
| Who writes the sinks | the Python CLI (its own loaders) | NiFi processors |
| NiFi load processors | **none** — no `ConvertRecord`, `PutDatabaseRecord`, `PutElasticsearch*`, `DBCPConnectionPool` | `ConvertRecord` + `PutDatabaseRecord` (or `PutElasticsearchJson`/`PutS3Object` for MinIO) |
| Flow after `ExecuteStreamCommand` | `RouteOnAttribute` (route on `exit.code`) only | `RouteOnAttribute` → load processors |

> **Rule of thumb:** if you pass `--pg-uri`, `--elasticsearch-url` and/or
> `--minio-uri`, the CLI already loads the data, so the flow only needs to
> **execute the Python command** — do **not** add `PutDatabaseRecord` or
> similar. Without any credential argument the CLI just prints NDJSON, so NiFi
> **must** provide `PutDatabaseRecord` (or the equivalent) to load it.

### Option A — Direct execute (Python loads, no PutDatabaseRecord)

The CLI loads the sinks itself, so the NiFi flow only runs the command and routes
on the exit code. Target command (as run by hand):

```bash
python -m ingestion run \
  --usecase ketenagakerjaan \
  --source bps_inflasi_mom \
  --pg-uri         'postgresql://setneg-user:secret@192.168.15.16:5432/setneg-stage' \
  --elasticsearch-url 'http://bigspider:secret@192.168.15.16:9200' \
  --minio-uri      'minio://access:secret@minio-api-sitroom.setneg.go.id/raw?secure=true' \
  --extra-vars '{"BPS_WEBAPI_KEY":"xxxxxxxx"}'
```

Only the sinks a source actually declares are written (a PostgreSQL-only source
stays PostgreSQL-only even if Elasticsearch/MinIO URIs are passed), and the NiFi
host must be able to reach those endpoints. In this mode the CLI writes the sinks
directly and does **not** print NDJSON, so NiFi's stdout handling is irrelevant.

#### Step 1 — Where the secrets live

NiFi rule: **a sensitive parameter can only be referenced from a property that is
itself marked sensitive.** `Command Arguments` is *not* sensitive, so it **cannot**
contain `#{PG_URI}` while `PG_URI` is a sensitive parameter — NiFi rejects the
processor with:

> *'Command Arguments' is invalid … cannot reference Parameter 'PG_URI' because the
> Sensitivity of the parameter does not match the Sensitivity of the property.*

So pick one of these:

**A1 — Non-sensitive parameters (simplest).** Create Parameter Context `pc-bps` with
the parameters **not** marked Sensitive, then reference them with `#{}`:

| Parameter | Sensitive | Example value |
|---|---|---|
| `USECASE` | no | `ketenagakerjaan` |
| `PG_URI` | no | `postgresql://setneg-user:secret@192.168.15.16:5432/setneg-stage` |
| `ELASTICSEARCH_URL` | no | `http://bigspider:secret@192.168.15.16:9200` |
| `MINIO_URI` | no | `minio://access:secret@minio-api-sitroom.setneg.go.id/raw?secure=true` |
| `EXTRA_VARS` | no | `{"BPS_WEBAPI_KEY":"xxxxxxxx"}` |

Assign it to the publisher Process Group (right-click the **bps** Process Group →
**Configure** → **Parameter Context** → `pc-bps` → **Apply**). Trade-off: the values
are stored in the flow configuration in clear text (readable by anyone who can read
the flow).

**A2 — Secrets in the process environment (recommended).** Keep them out of both the
flow and the command line. `python -m ingestion run` already reads `PG_URI`,
`ELASTICSEARCH_URL` and `MINIO_URI` **from the environment** and enables the loaders
automatically, so no `--pg-uri`/… arguments are required. Set them for the NiFi
process on the host (e.g. `conf/nifi-env.sh`, or a small wrapper script):

```sh
export PG_URI='postgresql://setneg-user:secret@192.168.15.16:5432/setneg-stage'
export ELASTICSEARCH_URL='http://bigspider:secret@192.168.15.16:9200'
export MINIO_URI='minio://access:secret@minio-api-sitroom.setneg.go.id/raw?secure=true'
export BPS_WEBAPI_KEY='xxxxxxxx'
```

*Command Arguments* then carries no secret (see Step 3):
`-m ingestion run --usecase #{USECASE} --source ${source}` with `USECASE` left
**non-sensitive**. This is also safer: secrets never appear in the process arguments
(`ps`). (Alternatively drop a `.env` on the host and pass `--env <profile>`; the CLI
loads it at startup.)

Reference a parameter with `#{NAME}` (e.g. `#{USECASE}`). **`${...}` is Expression
Language for FlowFile attributes, not parameters** — mixing them up is the usual
cause of "parameter not found".

#### Step 2 — Per-source attribute

The source name differs per processor, so set it as an attribute with
`UpdateAttribute` rather than a shared parameter:

```
UpdateAttribute → source = bps_inflasi_mom
```

#### Step 3 — ExecuteStreamCommand properties

| Property | Value |
|---|---|
| Command Path | `/opt/nifi/nifi-current/venv/bin/python3` |
| Command Arguments Strategy | `Command Arguments Property` (default) |
| Command Arguments | **A1:** `-m ingestion run --usecase #{USECASE} --source ${source} --pg-uri #{PG_URI} --elasticsearch-url #{ELASTICSEARCH_URL} --minio-uri #{MINIO_URI} --extra-vars #{EXTRA_VARS}` · **A2:** `-m ingestion run --usecase #{USECASE} --source ${source}` |
| Command Arguments Delimiter | **leave the default** — a single space (the UI shows it as `\ `). Do **not** type just `\`. |
| Working Directory | `/data/nifi-scripts` |
| Ignore STDIN | `true` |
| Output Destination Attribute | *(leave empty)* |
| Output MIME Type | *(leave empty)* |
| Max Attribute Length | default |

`#{...}` pulls Parameter Context values (in A2 the secrets are **not** here — they
come from the process environment); `${source}` is the FlowFile attribute from Step 2.

**Connections.** `ExecuteStreamCommand` is not a source: it needs an incoming
FlowFile, so put the `GenerateFlowFile` CRON trigger upstream. Set the **`output
stream`** relationship to *auto-terminate* (Option A ignores stdout) — or route it
to `LogAttribute` — and connect **`nonzero status`** to the failure path
(`RetryFlowFile`/`LogAttribute`), or auto-terminate it while testing.

> **No shell, no quotes.** `ExecuteStreamCommand` splits *Command Arguments* on the
> delimiter and passes them straight to the process — it does **not** run a shell,
> so `--pg-uri "${PG_URI}"` would pass the quote characters literally. Keep the
> parameter values **space-free** (the URIs and the compact JSON above are) and
> write the arguments unquoted. If a value must contain a space, change *Command
> Arguments Delimiter* (e.g. to `;`) and join the arguments with that character.

#### Troubleshooting the processor

- **`'Command Arguments' is invalid … Sensitivity of the parameter does not match`** —
  a **sensitive** parameter (e.g. `#{PG_URI}`) is referenced from the non-sensitive
  *Command Arguments* property. Either make those parameters non-sensitive (A1) or move
  the secrets to the process environment and drop them from the arguments (A2). See
  Step 1.
- **`Processor requires an upstream connection but currently has none`** — add a
  `GenerateFlowFile` (the CRON trigger) upstream; `ExecuteStreamCommand` is not a source.
- **`Relationship 'output stream'/'nonzero status' is not connected`** — auto-terminate
  `output stream` (Option A ignores stdout) and connect `nonzero status` to the failure
  path (`RetryFlowFile`/`LogAttribute`); auto-terminate it while testing.
- **Warning / args not split** — *Argument Delimiter* is not the default space. A
  bare `\` (or any character that does not occur in *Command Arguments*) leaves the
  whole line as **one** argument, so `python3` prints an argparse error and exits
  **2**. Reset the field to the default (a single space, shown as `\ `).
- **Processor invalid, `#{PG_URI}` unresolved** — the Parameter Context is missing,
  a parameter name does not match exactly, or it is not **assigned** to the Process
  Group (and any parent group). Sensitive parameters also need a value set; until
  then the literal text `#{PG_URI}` is passed to Python.
- **`RouteOnAttribute` never matches** — confirm the exit-code attribute name in the
  processor's **Help/Documentation** (it is version-specific) and use that name in
  the `${...}` rules; inspect a FlowFile's attributes via *View provenance* / *List
  queue* to see the exact key.

#### Step 4 — RouteOnAttribute

Route on the exit code NiFi captured from the process (`exit.code`):

```
success : ${exit.code:equals('0')}
retry   : ${exit.code:or(${exit.code:equals('1')}, ${exit.code:equals('4')})}
alert   : ${exit.code:or(${exit.code:equals('2')}, ${exit.code:equals('3')})}
```

- `success` → `LogAttribute` (nothing to load — the CLI already wrote the sinks;
  use it for the audit trail).
- `retry` → `RetryFlowFile` (exponential backoff: 3× for code 1, 5× @10 min for code 4).
- `alert` → `LogAttribute` on the monitoring/Bulletin path (no retry).

### Option B — NDJSON to NiFi (NiFi loads)

No credential arguments; the CLI writes NDJSON to stdout and NiFi loads it:

```bash
python -m ingestion run \
  --usecase ketenagakerjaan \
  --source bps_inflasi_mom \
  --mode prod \
  --extra-vars '{"BPS_WEBAPI_KEY":"xxxxxxxx"}'
```

`ExecuteStreamCommand` arguments (same `#{}` parameters and `${source}` attribute as Option A):

```
-m ingestion run --usecase #{USECASE} --source ${source} --mode prod --extra-vars #{EXTRA_VARS}
```

## The run command

Two forms (see *Integration options* for the NiFi wiring):

```bash
# Option B — NDJSON to stdout (NiFi loads)
python -m ingestion run \
  --usecase ketenagakerjaan \
  --source bps_inflasi_mom \
  --mode prod \
  --extra-vars '{"BPS_WEBAPI_KEY":"xxxxxxxx"}'

# Option A — the CLI loads the sinks itself (any URI switches the run to the DEV loader)
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
| `--exclude` | Comma-separated source names to skip from the `--publisher`/`--source` selection (e.g. `--exclude bps_inflasi_yoy,bps_inflasi_mom`) |
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

> **NiFi note:** `ExecuteStreamCommand` splits *Command Arguments* on the delimiter
> (default space) and does **not** run a shell, so quotes are not stripped. Write
> the JSON **without spaces** (`{"BPS_WEBAPI_KEY":"xxxxxxxx"}`), store it in a
> Parameter Context parameter, and reference it as `#{EXTRA_VARS}` — unquoted.

## ExecuteStreamCommand (shared settings)

| Property | Value |
|---|---|
| Working Directory | `/data/nifi-scripts` |
| Command Path | `/opt/nifi/nifi-current/venv/bin/python3` |
| Command Arguments | see *Option A* (Step 3) / *Option B* — **no quotes**, `#{}` for parameters, `${}` for attributes |
| Command Arguments Delimiter | `\ ` (single space — the default) |
| Ignore STDIN | `true` (the CLI reads no stdin) |

The equivalent wrapper entrypoint is `run_ingestion.py`:

```
Command Arguments : run_ingestion.py run --usecase #{USECASE} --source ${source} --mode prod --extra-vars #{EXTRA_VARS}
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
| `PG_URI` | no | `postgresql://...` |
| `ELASTICSEARCH_URL` | no | `http://...` |
| `MINIO_URI` | no | `minio://...` |
| `EXTRA_VARS` | no | `{"BPS_WEBAPI_KEY":"xxxxxxxx"}` |

They must be **non-sensitive** to be referenced from *Command Arguments* (`#{NAME}`):
a sensitive parameter may only be used by a property that is itself sensitive. To keep
credentials encrypted instead, put them in the process environment and leave them out
of the arguments — see *Option A → Step 1*.

Per-source processors set `source` in an `UpdateAttribute` (or inline it in the
`ExecuteStreamCommand` arguments). This lets all sources in a publisher group share
the same Parameter Context.

## Processor chain (inside each source processor)

| Step | Processor | Purpose |
|---|---|---|
| 1 | `GenerateFlowFile` (CRON) | Trigger per Update Frequency (daily/monthly) |
| 2 | `UpdateAttribute` | Set `usecase`, `publisher`, `source`, `ingestion_ts` |
| 3 | `ExecuteStreamCommand` | Invoke the CLI (see *Integration options*) |
| 4 | `RouteOnAttribute` | Route by `exit.code` |
| 5 | **Option A:** `LogAttribute` | Direct execute — the CLI already loaded the sinks; nothing to load in NiFi |
| 5 | **Option B:** `ConvertRecord` → `PutDatabaseRecord` (+ `DBCPConnectionPool`) | NDJSON → Record → load to PostgreSQL |
| 6 | `RetryFlowFile` / `LogAttribute` | Failure path (retry + Bulletin) |

## RouteOnAttribute rules

```
success : ${exit.code:equals('0')}
retry   : ${exit.code:or(${exit.code:equals('1')}, ${exit.code:equals('4')})}
alert   : ${exit.code:or(${exit.code:equals('2')}, ${exit.code:equals('3')})}
```

## Exit codes

| Code | Meaning | Strategy |
|---|---|---|
| 0 | Success | Option A → `LogAttribute`; Option B → `ConvertRecord` → `PutDatabaseRecord` |
| 1 | Ingestion error | RetryFlowFile, exponential backoff, 3x |
| 2 | Config error (bad/missing config, e.g. missing API key) | Bulletin alert, no retry |
| 3 | Auth error | Bulletin alert, check token/cookie |
| 4 | Source unavailable | RetryFlowFile, delayed retry, 5x @ 10 min |

## Worked example — `bps/bps_inflasi_mom`

1. Process Group **bps** with (sensitive) Parameter Context `pc-bps`:
   `PG_URI`, `ELASTICSEARCH_URL`, `MINIO_URI`, `EXTRA_VARS={"BPS_WEBAPI_KEY":"..."}`,
   referenced as `#{PG_URI}` / `#{ELASTICSEARCH_URL}` / `#{MINIO_URI}` / `#{EXTRA_VARS}`.
2. Inside, processor **bps_inflasi_mom**:
   - `GenerateFlowFile` cron `0 0 1 * *` (monthly).
   - `UpdateAttribute`: `source=bps_inflasi_mom`.
   - `ExecuteStreamCommand` (**Option A — direct execute**, since the context
     holds the URIs):
     ```
     Command Arguments: -m ingestion run --usecase #{USECASE} --source ${source} --pg-uri #{PG_URI} --elasticsearch-url #{ELASTICSEARCH_URL} --minio-uri #{MINIO_URI} --extra-vars #{EXTRA_VARS}
     ```
   - `RouteOnAttribute` → `LogAttribute` on success. **No `PutDatabaseRecord`** —
     the CLI already loaded the declared sinks.
   - *(Option B variant: drop the URI arguments, keep `--mode prod`, then
     `RouteOnAttribute` → `PutDatabaseRecord` `raw_bps.inflasi_bulanan`.)*

If `BPS_WEBAPI_KEY` is missing, the CLI exits **2** with
`Missing BPS WebAPI key...` instead of silently returning 0 rows.

## Direct-load vs NiFi-load

- **Direct execute (Option A)** — any of `--pg-uri` / `--elasticsearch-url` /
  `--minio-uri` is passed: the Python CLI writes to the sinks itself, so NiFi
  needs **no** `ConvertRecord`/`PutDatabaseRecord`/`PutElasticsearch*` — just
  `ExecuteStreamCommand` + `RouteOnAttribute`. Simple, but the NiFi host must be
  able to reach the databases.
- **NiFi-load (Option B)** — `--mode prod` only (no credential arguments): the CLI
  emits NDJSON to stdout, and NiFi parses and writes it with `ConvertRecord` +
  `PutDatabaseRecord` (or the Elasticsearch/MinIO equivalents). Keeps DB
  credentials in NiFi.

## PDF sources

PDF extractors download the PDF, upload it to MinIO, and emit a metadata record
(bucket, object_key, etag, size, sha256). Route that record to a metadata table
or catalog index.

## Templates

Export the built flows as `templates/ingestion_flow.xml` and
`templates/error_handler_flow.xml` from the NiFi UI once assembled.
