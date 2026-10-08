"""Custom exceptions and exit codes shared by the ingestion framework."""


class ExitCode:
    SUCCESS = 0
    INGESTION_ERROR = 1
    CONFIG_ERROR = 2
    AUTH_ERROR = 3
    SOURCE_UNAVAILABLE = 4


class IngestionError(Exception):
    """Runtime error during extraction / normalization / loading (exit 1)."""


class ConfigError(IngestionError):
    """Missing parameter, env var not set, schema mismatch (exit 2)."""


class AuthError(IngestionError):
    """API token invalid/expired, SharePoint auth failed (exit 3)."""


class SourceUnavailable(IngestionError):
    """Target URL unreachable, HTTP 5xx, timeout (exit 4)."""


class ItemNotFound(SourceUnavailable):
    """Target item does not exist (HTTP 404). Subclass so exit code stays 4."""


EXIT_CODE_BY_EXCEPTION = (
    (ConfigError, ExitCode.CONFIG_ERROR),
    (AuthError, ExitCode.AUTH_ERROR),
    (SourceUnavailable, ExitCode.SOURCE_UNAVAILABLE),
    (IngestionError, ExitCode.INGESTION_ERROR),
)


def exit_code_for(exc: BaseException) -> int:
    for exc_type, code in EXIT_CODE_BY_EXCEPTION:
        if isinstance(exc, exc_type):
            return code
    return ExitCode.INGESTION_ERROR
