"""Unified CLI entry point.

Usage:
    python -m ingestion.cli run --usecase ketenagakerjaan \\
        --source kasus_perselisihan --access excel --mode prod

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
from .usecases.registry import resolve_normalizer

logger = logging.getLogger("ingestion")

ACCESS_CHOICES = ["excel", "api", "scraper", "pdf"]
MODE_CHOICES = ["dev", "prod"]
TARGET_CHOICES = ["none", "postgres", "elastic"]

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


def _emit_ndjson(records: Iterable[Dict[str, Any]]) -> int:
    count = 0
    for record in records:
        sys.stdout.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
        count += 1
    sys.stdout.flush()
    return count


def _dev_load(records: Iterator[Dict[str, Any]], config: Dict[str, Any], target: str) -> int:
    if target == "none":
        return _emit_ndjson(records)
    if target == "elastic":
        from .core.loaders.elastic_loader import ElasticLoader

        return ElasticLoader(config).load(records)
    from .core.loaders.postgres_loader import PostgresLoader

    return PostgresLoader(config).load(records)


URL_FORWARD_KEYS = ("download_url", "excel_url", "pdf_url", "url", "href")


def _parse_accesses(access: Any, usecase: str, publisher: str, source: str) -> List[str]:
    """Resolve the access chain: explicit values (list/comma string) or source default."""
    from .usecases.registry import default_accesses, normalize_access

    if access is None:
        items: List[str] = []
    elif isinstance(access, str):
        items = [part for part in access.split(",") if part.strip()]
    else:
        items = [part for value in access for part in str(value).split(",") if part.strip()]

    if not items:
        resolved = default_accesses(usecase, publisher, source)
        logger.info("Access not specified; using default: %s", ", ".join(resolved))
        return resolved

    resolved = []
    for item in items:
        normalized = normalize_access(item)
        if normalized not in ACCESS_CHOICES:
            raise ConfigError(
                f"Unsupported --access '{item}'. Choose from: {', '.join(ACCESS_CHOICES)}"
            )
        resolved.append(normalized)
    return resolved


def _first_url(records: List[Dict[str, Any]]) -> Optional[str]:
    for record in records:
        for key in URL_FORWARD_KEYS:
            value = record.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
    return None


def _extract(
    usecase: str,
    publisher: str,
    source: str,
    accesses: List[str],
    configs: List[Dict[str, Any]],
) -> Iterator[Dict[str, Any]]:
    """Run the extractor chain. Later steps receive the URL discovered by earlier ones."""
    from .usecases.registry import resolve_extractor_class

    if len(accesses) == 1:
        extractor = resolve_extractor_class(usecase, publisher, source, accesses[0])(configs[0])
        return extractor.extract()

    records: List[Dict[str, Any]] = []
    step_config = dict(configs[0])
    for index, access in enumerate(accesses):
        extractor = resolve_extractor_class(usecase, publisher, source, access)(step_config)
        if index < len(accesses) - 1:
            produced = list(extractor.extract())
            discovered = _first_url(produced)
            if not discovered:
                raise IngestionError(
                    f"Step '{access}' produced no URL to feed step '{accesses[index + 1]}'"
                )
            logger.info("Step '%s' discovered URL for next step", access)
            step_config = {**configs[index + 1], "url": discovered, "download_url": discovered}
            records = produced
        else:
            records = extractor.extract()
    return iter(records)


def execute_run(
    usecase: str,
    publisher: str,
    source: str,
    access: Any = None,
    mode: str = "prod",
    target: Optional[str] = None,
    limit: int = 0,
) -> int:
    accesses = _parse_accesses(access, usecase, publisher, source)
    if not accesses:
        raise ConfigError("No data access resolved")

    # Build per-step configs; only the first step must have a URL of its own.
    configs = [
        load_config(usecase, publisher, source, step, require_url=(index == 0))
        for index, step in enumerate(accesses)
    ]
    config = configs[-1]
    effective_target = (target or config.get("target") or "none").lower()

    logger.info("Starting ingestion")
    logger.info("Usecase: %s", config["usecase"])
    logger.info("Publisher: %s", config["publisher"])
    logger.info("Source: %s", config["source"])
    logger.info("Access: %s", " -> ".join(accesses))
    logger.info("Mode: %s (target=%s)", mode, effective_target)

    normalizer = resolve_normalizer(config["usecase"], config["publisher"], config["source"], config)
    records = normalizer.normalize(
        _extract(config["usecase"], config["publisher"], config["source"], accesses, configs)
    )
    if limit and limit > 0:
        records = (rec for i, rec in enumerate(records) if i < limit)

    if mode == "dev":
        count = _dev_load(records, config, effective_target)
    else:
        count = _emit_ndjson(records)

    logger.info("Ingestion completed (records=%s, mode=%s, target=%s)", count, mode, effective_target)
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
@click.option(
    "--access",
    "accesses",
    multiple=True,
    help="Data access step(s): repeatable or comma-separated, e.g. "
    "--access scraper --access excel (or --access scraper,excel). "
    "Omit to use the source default.",
)
@click.option("--mode", default="prod", type=click.Choice(MODE_CHOICES), show_default=True)
@click.option("--target", default=None, type=click.Choice(TARGET_CHOICES), help="DEV load target override")
@click.option("--limit", default=0, type=int, help="Limit records (debug)")
@click.option("--env", "env_profile", default=None, help=ENV_OPTION_HELP)
@click.option("--log-level", default="INFO", show_default=True)
def run(
    usecase: str,
    publisher: str,
    source: str,
    accesses: tuple,
    mode: str,
    target: str,
    limit: int,
    env_profile: Optional[str],
    log_level: str,
) -> None:
    """Run data ingestion for a usecase by --publisher and/or --source.

    ``--publisher`` runs every source under that publisher. ``--access`` is
    optional; omit it to use each source's default, or pass one/more steps (in
    order) to chain extractors.
    """
    setup_logging(log_level)
    try:
        _apply_env(env_profile)
        pairs = _resolve_run_targets(usecase, publisher, source)
        logger.info("Targets: %s", ", ".join(f"{pub}/{src}" for pub, src in pairs))
        code = ExitCode.SUCCESS
        for pub, src in pairs:
            try:
                execute_run(usecase, pub, src, accesses, mode, target, limit)
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
@click.option("--usecase", required=True, help="Use case name, e.g. ketenagakerjaan")
@click.option("--publisher", default=None, help="Only generate dictionaries for sources under this publisher")
@click.option("--source", "source_name", default=None, help="Only generate the dictionary for this source")
@click.option("--output", default="./docs", show_default=True, help="Output directory for Markdown docs")
@click.option("--catalog", default=None, help="Catalog reference: item id or path (overrides env)")
@click.option("--scaffold", is_flag=True, help="Create module folders/files for eligible sources")
@click.option(
    "--scaffold-root",
    default="ingestion/usecases",
    show_default=True,
    help="Root directory for scaffolding",
)
@click.option("--include-ineligible", is_flag=True, help="Also emit dictionaries for ineligible sources")
@click.option("--env", "env_profile", default=None, help=ENV_OPTION_HELP)
@click.option("--log-level", default="INFO", show_default=True)
def docs(
    usecase: str,
    publisher: str,
    source_name: str,
    output: str,
    catalog: str,
    scaffold: bool,
    scaffold_root: str,
    include_ineligible: bool,
    env_profile: Optional[str],
    log_level: str,
) -> None:
    """Generate Markdown docs from the SharePoint catalog and Data Dictionary.

    Always writes ``usecase_<usecase>.md``. Writes ``dictionary_<usecase>_<source>.md``
    for eligible sources, or only those under ``--publisher`` / the one given by
    ``--source``. With ``--scaffold``, creates the module folders/files.
    """
    setup_logging(log_level)
    try:
        _apply_env(env_profile)
        _generate_docs(
            usecase,
            source_name,
            output,
            catalog,
            scaffold,
            scaffold_root,
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


def _generate_docs(
    usecase: str,
    source_name: Optional[str],
    output: str,
    catalog: Optional[str],
    scaffold: bool = False,
    scaffold_root: str = "ingestion/usecases",
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
    env_path.write_text("\n".join(env_lines(usecase, sources)) + "\n", encoding="utf-8")
    logger.info("Wrote %s (env vars for eligible sources)", env_path)

    if source_name:
        wanted = normalize_name(source_name)
        targets = [s for s in sources if normalize_name(s["source_name"]) == wanted]
        if not targets:
            targets = [s for s in sources if wanted in normalize_name(s["source_name"])]
        if not targets:
            raise ConfigError(f"Source '{source_name}' not found in sheet '{sheet}'")
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
        from .sharepoint.scaffold import scaffold_usecase

        created, skipped = scaffold_usecase(scaffold_root, usecase, eligible, schemas)
        for path in created:
            logger.info("  created %s", path)
        logger.info(
            "Scaffold complete: %s created, %s skipped (already existed)", len(created), len(skipped)
        )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()