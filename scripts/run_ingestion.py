#!/usr/bin/env python3
"""NiFi ExecuteStreamCommand entry point.

NiFi invokes this wrapper from the scripts working directory, e.g.:

    Command Path       : /opt/nifi/nifi-current/venv/bin/python3
    Command Arguments  : run_ingestion.py run --usecase ${USECASE} --source ${SOURCE} --access ${ACCESS} --mode prod

Equivalent to ``python -m ingestion.cli`` so the same flat invocation style as
the existing scripts keeps working.
"""

from ingestion.cli import main

if __name__ == "__main__":
    main()
