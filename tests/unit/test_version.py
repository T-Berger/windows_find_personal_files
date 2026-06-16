"""Smoke tests for package metadata and CLI."""

import subprocess
import sys


def test_version() -> None:
    from windows_personal_archive import __version__

    assert __version__ == "0.1.0"


def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "windows_personal_archive", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Windows Personal Archive" in result.stdout
