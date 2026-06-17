"""Archive writer tests."""

import os
import zipfile
from pathlib import Path

from windows_personal_archive.archive.writer import ZipArchiveWriter


def test_zip_accepts_pre_1980_timestamp(tmp_path: Path) -> None:
    source = tmp_path / "old.txt"
    source.write_text("legacy", encoding="utf-8")
    # 1970-01-01 — valid on disk but invalid for strict ZIP timestamps
    os.utime(source, (0, 0))

    zip_path = tmp_path / "archive.zip"
    writer = ZipArchiveWriter(zip_path)
    try:
        writer.add_file(source, "USERS/alice/PROFILE/old.txt", hash_file=False)
    finally:
        writer.close()

    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "USERS/alice/PROFILE/old.txt" in zf.namelist()
        assert zf.read("USERS/alice/PROFILE/old.txt") == b"legacy"
