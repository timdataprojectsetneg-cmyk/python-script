# Reference Docs

Markdown generated from the SharePoint use case catalog and Data Dictionary files.

Generate with:

```bash
python -m ingestion.cli docs --usecase ketenagakerjaan
python -m ingestion.cli docs --usecase ketenagakerjaan --source-name "Kasus Perselisihan"
```

Outputs:

- `usecase_<usecase>.md` — catalog table, proposed module structure, env vars
  (blueprint for scaffolding a use case's folders/files).
- `dictionary_<usecase>_<source>.md` — field table + generated Pydantic model
  (blueprint for the source's `models.py`).

These files are generated artifacts; regenerate them from SharePoint rather than
editing by hand.
