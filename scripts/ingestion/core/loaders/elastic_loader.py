"""DEV-only Elasticsearch loader (re-exported for symmetry)."""

from .postgres_loader import ElasticLoader, PostgresLoader

__all__ = ["PostgresLoader", "ElasticLoader"]
