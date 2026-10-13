# Example Use Case — Reference Template

Use this module as a copy-and-use template when adding a new data source.

## Structure

```
usecases/<usecase>/<publisher>/<source>/
├── __init__.py
├── config.py            # optional constants
├── models.py            # Pydantic schema (class Record)
├── normalizer.py        # optional (class Normalizer)
├── excel/extractor.py   # class Extractor
├── api/extractor.py
├── scraper/extractor.py
└── pdf/extractor.py
```

## How to create a new source

1. Copy `example_publisher/example_source/` to
   `usecases/<usecase>/<publisher>/<source>/` (publisher and source slugs are
   derived from the catalog: `Kemnaker` -> `kemnaker`, `Kasus Perselisihan` ->
   `kasus_perselisihan`).
2. Define the Pydantic schema in `models.py` (class **`Record`**) mirroring the
   catalog Data Dictionary. `catalog.metadata_parser.to_pydantic_source()`
   can generate a starting point.
3. Implement `normalizer.py` (class **`Normalizer`**) if custom mapping is needed.
   If omitted, the generic normalizer is used and validates against `Record`.
4. Add one leaf folder per data access method, each exposing class **`Extractor`**:
   `excel/`, `api/`, `scraper/`, `pdf/`.
5. Register configuration via environment variables using the
   `{USECASE}__{PUBLISHER}__{SOURCE}__{ACCESS}__{KEY}` convention.
6. Run one source, or all sources of a publisher:
   ```
   python -m ingestion run --usecase example_usecase --source example_source
   python -m ingestion run --usecase example_usecase --publisher example_publisher
   ```
