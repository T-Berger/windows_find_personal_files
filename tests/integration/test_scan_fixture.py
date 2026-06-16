"""Integration scan against fixture tree."""

from pathlib import Path

import pytest

from windows_personal_archive.config.models import ArchiveConfig, OutputFormat, ScanConfig
from windows_personal_archive.scan.planner import run_scan

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "minimal_tree"


@pytest.fixture(autouse=True)
def _set_fixture_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WPA_TEST_FIXTURE_ROOT", str(FIXTURE_ROOT))


def test_scan_fixture_tree(tmp_path: Path) -> None:
    config = ArchiveConfig(
        output_format=OutputFormat.FOLDER,
        scan=ScanConfig(full_drive_scan=True),
    )
    output = tmp_path / "out"
    result = run_scan(config, output, copy_files=False)
    paths = {e.source_path.replace("\\", "/") for e in result.entries}
    assert any("alice/Documents/notes.txt" in p for p in paths)
    assert not any("Windows" in p for p in paths)


def test_archive_fixture_to_zip(tmp_path: Path) -> None:
    from windows_personal_archive.archive.writer import create_archive_writer

    config = ArchiveConfig(output_format=OutputFormat.ZIP)
    zip_path = tmp_path / "migration.zip"
    writer = create_archive_writer(zip_path, "zip")
    try:
        result = run_scan(config, zip_path, copy_files=True, archive_writer=writer)
    finally:
        writer.close()
    assert result.manifest.stats.files_copied >= 1
    assert zip_path.is_file()
