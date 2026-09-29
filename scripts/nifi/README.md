# NiFi Flow — Generic Ingestion

The NiFi flow is the sole scheduling/orchestration entry point in production.
It invokes the Python CLI via `ExecuteStreamCommand`, captures NDJSON on stdout,
and loads it with `PutDatabaseRecord`.

## Processor chain

| Step | Processor | Purpose |
|---|---|---|
| 1 | `GenerateFlowFile` (CRON) | Trigger per Update Frequency (daily/monthly/yearly) |
| 2 | `UpdateAttribute` | Inject `usecase`, `source`, `access`, `ingestion_ts` |
| 3 | `ExecuteStreamCommand` | Invoke `run_ingestion.py run --usecase ${USECASE} --source ${SOURCE} --access ${ACCESS} --mode prod` |
| 4 | `RouteOnAttribute` | Route by `exit.code` (see below) |
| 5a | `ConvertRecord` + `JsonTreeReader` | NDJSON → Record |
| 6a | `PutDatabaseRecord` + `DBCPConnectionPool` | Write to PostgreSQL / Elasticsearch |
| 5b | `RetryFlowFile` / `LogAttribute` | Failure path: retry + Bulletin alert |

## ExecuteStreamCommand properties

```
Working Directory : /opt/nifi/nifi-current/scripts
Command Path      : /opt/nifi/nifi-current/venv/bin/python3
Command Arguments : run_ingestion.py run --usecase ${USECASE} --source ${SOURCE} --access ${ACCESS} --mode prod
Ignore STDIN      : false
```

`ExecuteStreamCommand` maps the process exit code onto the `exit.code`
attribute automatically, which `RouteOnAttribute` consumes.

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
| 2 | Config error | Bulletin alert, no retry |
| 3 | Auth error | Bulletin alert, manual token check |
| 4 | Source unavailable | RetryFlowFile, delayed retry, 5x @ 10 min |

## PDF data access

For `--access pdf`, the Python CLI downloads the PDF and uploads it to
MinIO/S3 on-prem, then emits a single metadata record (bucket, object_key,
etag, size, sha256). Point `PutDatabaseRecord` at a metadata table, or route the
metadata to a catalog index.

## Parameter Context

Non-confidential values map 1:1 to the `.env` keys (`{USECASE}__{SOURCE}__{ACCESS}__{KEY}`).
Define separate DEV and PROD Parameter Contexts and reuse the same flow; DEV
points at local PostgreSQL/MinIO, PROD at the production instances.

## Templates

`templates/ingestion_flow.xml` and `templates/error_handler_flow.xml` are
exported from the NiFi UI once the flow above is built (Milestone M4).
