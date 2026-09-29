"""Allow ``python -m ingestion`` as an alias for ``python -m ingestion.cli``."""

from .cli import main

if __name__ == "__main__":
    main()
