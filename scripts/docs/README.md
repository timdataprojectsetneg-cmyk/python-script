# Reference Docs

Markdown generated from the use case catalog (SharePoint or spreadsheet) and
Data Dictionary files. Docs are grouped **per use case** (`docs/<usecase>/`).

Generate with:

```bash
python -m ingestion.cli docs --usecase ketenagakerjaan --env dev
python -m ingestion.cli docs --usecase ketenagakerjaan --source-name "Kasus Perselisihan" --env dev
```

Catalog source is selected by `DOCS_SOURCE` (loaded from `.env.<profile>`):
`spreadsheet` (default here) or `sharepoint`.

Outputs (per use case):

- `docs/<usecase>/usecase.md` — catalog table, proposed module structure.
- `docs/<usecase>/usecase.env` — generated per-source env vars.
- `docs/<usecase>/dictionary_<source>.md` — field table + generated Pydantic
  model (blueprint for the source's `models.py`).

These files are generated artifacts; regenerate them rather than editing by hand.
