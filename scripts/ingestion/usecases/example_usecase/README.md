# Example Use Case — Reference Template

Use this module as a copy-and-use template when adding a new data source.

## How to create a new use case

1. Copy this directory to `ingestion/usecases/<usecase>/<source>/`.
2. Define the Pydantic schema in `models.py` (class **`Record`**) mirroring the
   SharePoint Data Dictionary. `sharepoint.metadata_parser.to_pydantic_source()`
   can generate a starting point.
3. Implement `normalizer.py` (class **`Normalizer`**) if custom mapping is needed.
   If omitted, the generic normalizer is used and will validate against `Record`.
4. Add one leaf folder per data access method, each exposing class **`Extractor`**:
   - `excel/extractor.py`
   - `api/extractor.py`
   - `scraper/extractor.py`
   - `pdf/extractor.py`
5. Register configuration via environment variables, e.g.
   `EXAMPLE_USECASE__EXAMPLE_SOURCE__EXCEL__URL=...`.
6. Run:
   ```
   python -m ingestion.cli run --usecase example_usecase --source example_source \
       --access excel --mode dev
   ```

## Naming convention (enforced by `ingestion/usecases/registry.py`)

| File | Required class |
|---|---|
| `<access>/extractor.py` | `Extractor` |
| `normalizer.py` | `Normalizer` (optional) |
| `models.py` | `Record` (optional) |

If `<access>/extractor.py` is missing, the generic extractor for that access is
used. No changes to `core/` or `cli.py` are ever required.
