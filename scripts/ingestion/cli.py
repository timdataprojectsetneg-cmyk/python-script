"""Unified CLI entry point.

Usage:
    python -m ingestion.cli run --usecase ketenagakerjaan \\
        --source kasus_perselisihan --mode prod

    python -m ingestion.cli docs --usecase ketenagakerjaan --env dev [--scaffold]
"""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

import click

from . import __version__
from .config import load_config
from .exceptions import ConfigError, ExitCode, IngestionError, exit_code_for
from .usecases.registry import resolve_extractor_class, resolve_normalizer

logger = logging.getLogger("ingestion")

MODE_CHOICES = ["dev", "prod"]

# Header-row hints used to locate the header inside sheets with title/blank rows.
CATALOG_HEADER_HINTS = ["Source Name", "Nama Sumber", "Nama Source"]


def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.setLevel(lvl)
    logger.handlers = [handler]


ENV_OPTION_HELP = "Load secrets from .env.<profile>, e.g. 'dev' -> .env.dev"


def error_location(exc: BaseException, run_from: str | None = None) -> str:
    """Return ``file:line (function)`` for the deepest traceback frame."""
    tb = exc.__traceback__
    if tb is None:
        return "unknown"
    frame = traceback.extract_tb(tb)[-1]
    filename = frame.filename
    base = run_from or os.getcwd()
    try:
        filename = os.path.relpath(filename, base)
    except ValueError:
        pass
    return f"{filename}:{frame.lineno} ({frame.name})"


def _apply_env(profile: Optional[str]) -> None:
    """Activate the ``--env`` profile and ensure the file exists."""
    from .config import env_profile_file, get_env_profile, set_env_profile

    if profile:
        set_env_profile(profile)
    active = get_env_profile()
    if active and not env_profile_file(active):
        raise ConfigError(
            f"Env profile '.env.{active}' not found. Create it (keep it out of the repo) "
            f"or drop --env."
        )


def _apply_extra_vars(raw: Optional[str]) -> List[str]:
    """Inject ``--extra-vars`` JSON into the environment (source-specific keys).

    Example: ``--extra-vars '{"BPS_WEBAPI_KEY":"..."}'`` makes the key readable
    by extractors via ``config.get_raw("BPS_WEBAPI_KEY")``. Values override the
    environment profile. Only key names are logged, never values.
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"--extra-vars is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError('--extra-vars must be a JSON object, e.g. \'{"KEY":"value"}\'')
    injected: List[str] = []
    for key, value in data.items():
        if value is None:
            continue
        os.environ[str(key)] = str(value)
        injected.append(str(key))
    return injected


def _list_entities(kind: str, usecase: Optional[str], publisher: Optional[str]) -> None:
    """Print use case / publisher / source inventory (``python -m ingestion docs --list``)."""
    from .usecases.registry import list_publishers, list_sources, list_usecases

    usecases = [usecase] if usecase else list_usecases()
    tree: Dict[str, Dict[str, List[str]]] = {}
    for uc in usecases:
        publishers = list_publishers(uc)
        if publisher:
            publishers = [p for p in publishers if p == publisher]
        tree[uc] = {p: list_sources(uc, p) for p in publishers}

    n_usecases = len(tree)
    n_publishers = sum(len(p) for p in tree.values())
    n_sources = sum(len(s) for p in tree.values() for s in p.values())

    if kind == "usecases":
        print(f"USECASES ({n_usecases})")
        for uc, publishers in tree.items():
            sources = sum(len(s) for s in publishers.values())
            print(f"  {uc:<26} publishers={len(publishers):<3} sources={sources}")
        return

    if kind == "publishers":
        if usecase:
            print(f"PUBLISHERS in '{usecase}' ({n_publishers})")
            for pub, sources in tree.get(usecase, {}).items():
                print(f"  {pub:<26} sources={len(sources)}")
            return
        print(f"PUBLISHERS ({n_publishers})")
        for uc, publishers in tree.items():
            if not publishers:
                continue
            print(f"  [{uc}]")
            for pub, sources in publishers.items():
                print(f"    {pub:<24} sources={len(sources)}")
        return

    if kind == "sources":
        if publisher and not usecase:
            print(f"SOURCES under publisher '{publisher}' (across usecases) ({n_sources})")
            for uc, publishers in tree.items():
                for src in publishers.get(publisher, []):
                    print(f"  {uc}/{publisher}/{src}")
            return
        label = f" in '{usecase}'" if usecase else ""
        print(f"SOURCES{label} ({n_sources})")
        for uc, publishers in tree.items():
            for pub, sources in publishers.items():
                for src in sources:
                    print(f"  {uc}/{pub}/{src}")
        return

    # kind == "all": summary + full tree
    print("SUMMARY")
    print(f"  usecases={n_usecases} publishers={n_publishers} sources={n_sources}")
    print()
    for uc, publishers in tree.items():
        sources = sum(len(s) for s in publishers.values())
        print(f"{uc}  ({len(publishers)} publishers, {sources} sources)")
        for pub, srcs in publishers.items():
            print(f"  {pub}  ({len(srcs)} sources)")
            for src in srcs:
                print(f"    - {src}")


def _emit_ndjson(records: Iterable[Dict[str, Any]]) -> int:
    count = 0
    for record in records:
        sys.stdout.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
        count += 1
    sys.stdout.flush()
    return count


def _dev_load(
    records: Iterator[Dict[str, Any]], config: Dict[str, Any], target: str, use_dlt: bool = False
) -> int:
    if target == "none":
        return _emit_ndjson(records)
    if target == "elastic":
        from .core.loaders.elastic_loader import ElasticLoader

        return ElasticLoader(config).load(records)
    if target == "minio":
        from .core.loaders.minio_loader import MinioLoader

        return MinioLoader(config).load(records)
    from .core.loaders.postgres_loader import DltPostgresLoader, PostgresLoader

    loader = DltPostgresLoader if use_dlt else PostgresLoader
    return loader(config).load(records)


def _extract(
    usecase: str, publisher: str, source: str, config: Dict[str, Any]
) -> Iterator[Dict[str, Any]]:
    """Run the source extractor (it may combine several retrieval steps internally)."""
    extractor = resolve_extractor_class(usecase, publisher, source)(config)
    return extractor.extract()


def _declared_targets(config: Dict[str, Any]) -> List[str]:
    """Sinks a source actually declares, inferred from its target config keys."""
    declared: List[str] = []
    if config.get("es_index"):
        declared.append("elastic")
    if config.get("minio_bucket") or config.get("minio_prefix"):
        declared.append("minio")
    if config.get("postgre_table") or config.get("postgre_schema") or config.get("table"):
        declared.append("postgres")
    return declared


def _effective_targets(requested: List[str], declared: List[str]) -> List[str]:
    """Intersect requested sinks with the ones the source declares.

    A declared source never loads to a sink it does not target (e.g. a
    PostgreSQL-only source must not be pushed into Elasticsearch just because a
    global URI is set). Undeclared sources keep the requested sinks.
    """
    if not declared:
        return requested
    return [t for t in requested if t in declared] or ["none"]


def execute_run(
    usecase: str,
    publisher: str,
    source: str,
    mode: str = "prod",
    limit: int = 0,
    use_dlt: bool = False,
    targets: Optional[List[str]] = None,
) -> int:
    config = load_config(usecase, publisher, source)

    requested = [t.lower() for t in targets] if targets else []
    if not requested:
        requested = [
            t.strip().lower()
            for t in str(config.get("target") or "postgres").split(",")
            if t.strip()
        ]
    # Only load to sinks the source declares; a global URI must not push a
    # non-Elasticsearch source into Elasticsearch (and vice versa).
    declared = _declared_targets(config)
    effective_targets = _effective_targets(requested, declared)
    targets_label = ",".join(effective_targets)

    logger.info("Starting ingestion")
    logger.info("Usecase: %s", config["usecase"])
    logger.info("Publisher: %s", config["publisher"])
    logger.info("Source: %s", config["source"])
    logger.info("Mode: %s (target=%s)", mode, targets_label)
    if mode == "prod" and effective_targets != ["none"]:
        # Production deliberately has no database credentials. The NDJSON
        # stream is consumed by NiFi, which owns the PostgreSQL connection.
        logger.info(
            "Production target '%s' is downstream-only; emitting NDJSON for NiFi (no PostgreSQL connection)",
            targets_label,
        )

    normalizer = resolve_normalizer(config["usecase"], config["publisher"], config["source"], config)
    records = normalizer.normalize(
        _extract(config["usecase"], config["publisher"], config["source"], config)
    )
    if limit and limit > 0:
        records = (rec for i, rec in enumerate(records) if i < limit)

    if mode == "dev":
        rows = list(records)
        count = len(rows)
        for sink in effective_targets:
            _dev_load(iter(rows), config, sink, use_dlt=use_dlt)
    else:
        count = _emit_ndjson(records)

    output = "ndjson" if mode == "prod" else targets_label
    destination = ""
    if "postgres" in effective_targets:
        from .config import get_raw
        from .core.loaders.postgres_loader import _split_schema_table

        default_schema = get_raw("DEV__POSTGRES_DATASET", "ingestion_dev")
        schema, table_name = _split_schema_table(
            config.get("postgre_table") or config.get("table"),
            config.get("postgre_schema") or default_schema,
        )
        destination = f", schema={schema}, table={table_name or config.get('source')}"
    logger.info(
        "Ingestion completed (records=%s, mode=%s, target=%s, output=%s%s)",
        count,
        mode,
        targets_label,
        output,
        destination,
    )
    return ExitCode.SUCCESS


def _resolve_run_targets(
    usecase: str, publisher: Optional[str], source: Optional[str]
) -> List[tuple]:
    """Return (publisher, source) pairs to run, from --publisher and/or --source."""
    from .usecases.registry import find_publisher, list_sources

    pairs: List[tuple] = []
    if publisher and source:
        pairs.append((publisher, source))
        return pairs
    if publisher:
        sources = list_sources(usecase, publisher)
        if not sources:
            raise ConfigError(f"Publisher '{publisher}' has no sources")
        return [(publisher, item) for item in sources]
    if source:
        found = find_publisher(usecase, source)
        if not found:
            raise ConfigError(f"Source '{source}' not found under use case '{usecase}'")
        return [(found, source)]
    raise ConfigError("Provide --publisher and/or --source")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="ingestion")
@click.option("--env", "env_profile", default=None, help=ENV_OPTION_HELP)
def cli(env_profile: Optional[str]) -> None:
    """Generic ingestion CLI (extract -> normalize -> load)."""
    if env_profile:
        from .config import set_env_profile

        set_env_profile(env_profile)


@cli.command()
@click.option("--usecase", required=True, help="Use case name, e.g. ketenagakerjaan")
@click.option("--publisher", default=None, help="Run all sources under this publisher")
@click.option("--source", default=None, help="Source name, e.g. kasus_perselisihan")
@click.option("--mode", default="prod", type=click.Choice(MODE_CHOICES), show_default=True)
@click.option("--pg-uri", default=None, help="PostgreSQL URI (implies the postgres target)")
@click.option("--elasticsearch-url", default=None, help="Elasticsearch URI (implies the elastic target)")
@click.option("--minio-uri", default=None, help="MinIO URI (implies the minio target)")
@click.option("--limit", default=0, type=int, help="Limit records (debug)")
@click.option("--use-dlt", is_flag=True, default=False, help="Use dlt for DEV PostgreSQL loading")
@click.option(
    "--extra-vars",
    default=None,
    help='Extra per-run variables as a JSON object, e.g. \'{"BPS_WEBAPI_KEY":"..."}\'. '
    "Injected into the process env so extractors can read them (overrides the env profile).",
)
@click.option("--env", "env_profile", default=None, help=ENV_OPTION_HELP)
@click.option("--log-level", default="INFO", show_default=True)
def run(
    usecase: str,
    publisher: str,
    source: str,
    mode: str,
    pg_uri: Optional[str],
    elasticsearch_url: Optional[str],
    minio_uri: Optional[str],
    limit: int,
    use_dlt: bool,
    extra_vars: Optional[str],
    env_profile: Optional[str],
    log_level: str,
) -> None:
    """Run data ingestion for a usecase by --publisher and/or --source.

    ``--publisher`` runs every source under that publisher.
    """
    setup_logging(log_level)
    try:
        _apply_env(env_profile)
        # The environment profile is the deployment boundary: the development
        # profile carries local database credentials. A global connection URI
        # (PG_URI / ELASTICSEARCH_URL / MINIO_URI) also enables the loader step
        # without --env dev, loading to every sink whose URI is set.
        from .config import URI_TARGETS, get_env_profile, load_env, load_uri_targets

        # Load the env profile first, then let explicit CLI URIs win over it
        # (profile files are loaded with override=True).
        load_env(usecase)
        for name, uri in (("postgres", pg_uri), ("elastic", elasticsearch_url), ("minio", minio_uri)):
            if uri:
                os.environ[URI_TARGETS[name]] = uri

        active_profile = (get_env_profile() or "").strip().lower()
        uri_targets = sorted(load_uri_targets())

        injected = _apply_extra_vars(extra_vars)
        if injected:
            logger.info("Injected extra variables: %s", ", ".join(injected))
        if active_profile == "dev":
            if mode == "prod":
                logger.info("--env dev selected; enabling DEV loader")
            mode = "dev"
        elif uri_targets:
            logger.info("Connection URI detected (%s); enabling loaders", ", ".join(uri_targets))
            mode = "dev"
        elif mode == "dev":
            raise ConfigError(
                "Loading requires --env dev or a connection URI "
                "(--pg-uri/--elasticsearch-url/--minio-uri, or PG_URI/ELASTICSEARCH_URL/MINIO_URI)"
            )
        targets = uri_targets or None
        pairs = _resolve_run_targets(usecase, publisher, source)
        logger.info("Targets: %s", ", ".join(f"{pub}/{src}" for pub, src in pairs))
        code = ExitCode.SUCCESS
        for pub, src in pairs:
            try:
                execute_run(usecase, pub, src, mode, limit, use_dlt, targets)
            except Exception as exc:  # noqa: BLE001 - continue the remaining sources
                code = exit_code_for(exc)
                logger.error(
                    "Ingestion failed for %s/%s (%s) at %s: %s",
                    pub,
                    src,
                    type(exc).__name__,
                    error_location(exc),
                    exc,
                    exc_info=not isinstance(exc, IngestionError),
                )
    except Exception as exc:  # noqa: BLE001 - mapped to exit codes by design
        code = exit_code_for(exc)
        logger.debug("Ingestion traceback", exc_info=True)
        logger.error(
            "Ingestion failed (%s) at %s: %s",
            type(exc).__name__,
            error_location(exc),
            exc,
            exc_info=not isinstance(exc, IngestionError),
        )
    sys.exit(code)


@cli.command()
@click.option("--usecase", default=None, help="Use case name, e.g. ketenagakerjaan (optional with --list)")
@click.option("--publisher", default=None, help="Only generate dictionaries for sources under this publisher")
@click.option("--source", "source_name", default=None, help="Only generate the dictionary for this source")
@click.option(
    "--list",
    "list_kind",
    default=None,
    type=click.Choice(["usecases", "publishers", "sources", "all"]),
    help="List inventory instead of generating docs: usecases | publishers | sources | all "
    "(combine with --usecase/--publisher to filter).",
)
@click.option("--output", default="./docs", show_default=True, help="Output directory for Markdown docs")
@click.option(
    "--catalog",
    default=None,
    help=(
        "SharePoint catalog workbook reference (item ID or drive-relative path). "
        "Selects a different workbook than the one configured by the environment."
    ),
)
@click.option("--scaffold", is_flag=True, help="Create module folders/files for eligible sources")
@click.option(
    "--scaffold-overwrite",
    is_flag=True,
    help=(
        "Overwrite existing scaffold files (default: skip them). Limited to "
        "--source / --publisher when given, else the whole usecase"
    ),
)
@click.option("--include-ineligible", is_flag=True, help="Also emit dictionaries for ineligible sources")
@click.option("--env", "env_profile", default=None, help=ENV_OPTION_HELP)
@click.option("--log-level", default="INFO", show_default=True)
def docs(
    usecase: str,
    publisher: str,
    source_name: str,
    list_kind: str,
    output: str,
    catalog: str,
    scaffold: bool,
    scaffold_overwrite: bool,
    include_ineligible: bool,
    env_profile: Optional[str],
    log_level: str,
) -> None:
    """Generate Markdown docs from the SharePoint catalog and Data Dictionary.

    Always writes ``usecase_<usecase>.md``. Writes ``dictionary_<usecase>_<source>.md``
    for eligible sources, or only those under ``--publisher`` / the one given by
    ``--source``. With ``--scaffold``, creates the module folders/files.

    With ``--list``, prints an inventory instead: ``--list usecases``,
    ``--list publishers --usecase X``, ``--list sources --publisher Y``,
    or ``--list all`` for a summary.
    """
    setup_logging(log_level)
    try:
        if list_kind:
            _list_entities(list_kind, usecase, publisher)
            sys.exit(ExitCode.SUCCESS)
        if not usecase:
            raise ConfigError("--usecase is required (or use --list to browse the inventory)")
        _apply_env(env_profile)
        _generate_docs(
            usecase,
            source_name,
            output,
            catalog,
            scaffold,
            scaffold_overwrite,
            include_ineligible,
            publisher,
        )
    except Exception as exc:  # noqa: BLE001
        code = exit_code_for(exc)
        logger.debug("Doc generation traceback", exc_info=True)
        logger.error(
            "Doc generation failed (%s) at %s: %s",
            type(exc).__name__,
            error_location(exc),
            exc,
            exc_info=not isinstance(exc, IngestionError),
        )
        sys.exit(code)
    sys.exit(ExitCode.SUCCESS)


def _preserve_env_values(path: Path, keys: tuple) -> Dict[str, str]:
    """Read ``KEY=VALUE`` lines from an existing ``.env`` whose names end with ``__<key>``.

    Used so regenerating docs keeps hand-edited values (e.g. ``__METHOD``,
    ``__UNIQUE_KEY``) instead of resetting them to defaults.
    """
    preserved: Dict[str, str] = {}
    if not path.exists():
        return preserved
    suffixes = tuple(f"__{key}" for key in keys)
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        if name.endswith(suffixes):
            preserved[name] = value
    return preserved


def _generate_docs(
    usecase: str,
    source_name: Optional[str],
    output: str,
    catalog: Optional[str],
    scaffold: bool = False,
    scaffold_overwrite: bool = False,
    include_ineligible: bool = False,
    publisher: Optional[str] = None,
) -> None:
    from .sharepoint.client import SharePointClient
    from .sharepoint.markdown_docs import (
        dictionary_filename,
        env_lines,
        render_dictionary_markdown,
        render_usecase_markdown,
        usecase_filename,
        write_markdown,
    )
    from .sharepoint.metadata_parser import (
        derive_module_name,
        is_eligible,
        is_source_row,
        normalize_name,
        parse_catalog_row,
        parse_dictionary_matrix,
        publisher_slug,
        resolve_sheet_name,
        source_slug,
    )

    client = SharePointClient()
    catalog_ref = client.catalog_ref(catalog)
    logger.info("Catalog reference: %s", catalog_ref)

    sheet_names = client.list_sheets(catalog_ref)
    sheet = resolve_sheet_name(sheet_names, usecase)
    if not sheet:
        raise ConfigError(
            f"Use case '{usecase}' not found in catalog sheets: {', '.join(sheet_names)}"
        )

    rows = client.read_sheet(catalog_ref, sheet, header_hints=CATALOG_HEADER_HINTS)
    logger.info("Rows read from '%s': %s", sheet, len(rows))
    sources = [parse_catalog_row(row) for row in rows]
    sources = [s for s in sources if is_source_row(s)]
    if not sources:
        raise ConfigError(
            f"No usable sources parsed from sheet '{sheet}' ({len(rows)} rows). "
            "Check the catalog header or the --catalog reference."
        )

    eligible = [s for s in sources if is_eligible(s)]
    logger.info("Sources: %s total, %s eligible", len(sources), len(eligible))

    usecase_path = write_markdown(
        render_usecase_markdown(usecase, sources, catalog_ref),
        output,
        usecase_filename(usecase),
    )
    logger.info("Wrote %s (%s sources)", usecase_path, len(sources))

    env_path = Path(output) / f"{usecase_filename(usecase)[:-3]}.env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    preserved = _preserve_env_values(env_path, ("METHOD", "UNIQUE_KEY"))
    env_path.write_text(
        "\n".join(env_lines(usecase, sources, preserved=preserved)) + "\n", encoding="utf-8"
    )
    logger.info("Wrote %s (env vars for eligible sources)", env_path)

    # Dictionary markdown is generated per source; remove stale ineligible
    # dictionaries so the docs directory reflects the current catalog.
    eligible_slugs = {source_slug(source) for source in eligible}
    usecase_slug = usecase_filename(usecase)[len("usecase_") : -len(".md")]
    for stale in Path(output).glob(f"dictionary_{usecase_slug}_*.md"):
        slug = stale.stem.removeprefix(f"dictionary_{usecase_slug}_")
        if slug not in eligible_slugs:
            stale.unlink()
            logger.info("Removed ineligible documentation: %s", stale)

    if source_name:
        wanted = normalize_name(source_name)
        targets = [s for s in sources if normalize_name(s["source_name"]) == wanted]
        if not targets:
            targets = [s for s in sources if wanted in normalize_name(s["source_name"])]
        if not targets:
            raise ConfigError(f"Source '{source_name}' not found in sheet '{sheet}'")
        if not include_ineligible:
            ineligible_targets = [s for s in targets if not is_eligible(s)]
            targets = [s for s in targets if is_eligible(s)]
            for source in ineligible_targets:
                logger.info(
                    "Skipping ineligible source '%s'; use --include-ineligible to generate its dictionary",
                    source.get("source_name"),
                )
    elif publisher:
        wanted = normalize_name(publisher)
        targets = [s for s in sources if normalize_name(s.get("publisher")) == wanted]
        if not targets:
            targets = [s for s in sources if wanted in normalize_name(s.get("publisher"))]
        if not targets:
            raise ConfigError(f"Publisher '{publisher}' not found in sheet '{sheet}'")
        if not include_ineligible:
            targets = [s for s in targets if is_eligible(s)]
    else:
        targets = sources if include_ineligible else eligible

    schemas: Dict[str, Any] = {}
    for source in targets:
        sname = source["source_name"]
        slug = source_slug(source)
        dictionary = source.get("data_dictionary")
        if not dictionary:
            logger.warning("No Data Dictionary for %s; skipping", sname)
            continue

        dict_ref = client.dictionary_ref(dictionary, sheet)
        try:
            dict_sheets = client.list_sheets(dict_ref)
            dict_sheet = resolve_sheet_name(dict_sheets, sname) or (
                dict_sheets[0] if dict_sheets else None
            )
            dict_matrix = (
                client.read_matrix(dict_ref, dict_sheet) if dict_sheet else []
            )
            schema = parse_dictionary_matrix(dict_matrix)
            schemas[slug] = schema
            if not schema:
                logger.warning("No dictionary fields parsed for %s (sheet '%s')", sname, dict_sheet)
        except Exception as exc:  # noqa: BLE001
            if source_name:
                raise
            logger.warning("Could not read dictionary for %s (%s): %s", sname, dict_ref, exc)
            continue

        module_path = (
            f"ingestion/usecases/{derive_module_name(usecase)}/"
            f"{publisher_slug(source)}/{slug}/models.py"
        )
        path = write_markdown(
            render_dictionary_markdown(usecase, sname, schema, source, module_path),
            output,
            dictionary_filename(usecase, slug),
        )
        logger.info("Wrote %s (%s fields)", path, len(schema))

    if scaffold:
        from .sharepoint.scaffold import remove_ineligible_sources, scaffold_usecase

        scaffold_root = "ingestion/usecases"
        scaffold_targets = [s for s in targets if is_eligible(s)]
        if source_name:
            scope_publishers = {publisher_slug(s) for s in targets}
            scope_sources = {source_slug(s) for s in targets}
        elif publisher:
            scope_publishers = {publisher_slug(s) for s in targets}
            scope_sources = None
        else:
            scope_publishers = None
            scope_sources = None
        removed = remove_ineligible_sources(
            scaffold_root, usecase, scaffold_targets, scope_publishers, scope_sources
        )
        for path in removed:
            logger.info("Removed ineligible scaffold: %s", path)
        created, skipped = scaffold_usecase(
            scaffold_root, usecase, scaffold_targets, schemas, overwrite=scaffold_overwrite
        )
        for path in created:
            logger.info("  created %s", path)
        logger.info(
            "Scaffold complete: %s created, %s skipped (already existed)", len(created), len(skipped)
        )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
