"""Integration test for the CLI in prod mode."""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2]

# Port 9 (discard) is closed locally, so connections fail fast without network.
# Use a direct .xlsx URL so no landing page is fetched.
UNREACHABLE_URL = "http://127.0.0.1:9/unreachable.xlsx"


def test_cli_prod_maps_source_error(tmp_path):
    env = {
        "PYTHONPATH": str(SCRIPTS_DIR),
        "EXAMPLE_USECASE__EXAMPLE_PUBLISHER__EXAMPLE_SOURCE__URL": UNREACHABLE_URL,
        "PATH": "/usr/bin:/bin:/usr/local/bin",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ingestion.cli",
            "run",
            "--usecase",
            "example_usecase",
            "--source",
            "example_source",
            "--mode",
            "prod",
            "--limit",
            "1",
        ],
        cwd=str(SCRIPTS_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    # Unreachable source must exit 4 (never crash with an unhandled traceback).
    assert result.returncode == 4
    assert "Traceback" not in result.stderr
