"""Restore archived files to target Windows paths."""

import shutil
import zipfile
from pathlib import Path

from windows_personal_archive.config.models import EntryStatus
from windows_personal_archive.manifest.writer import read_manifest_header, read_manifest_jsonl
from windows_personal_archive.scan.path_map import archive_to_target_path


def restore_archive(
    archive_path: Path,
    user_map: dict[str, str],
    target_drive: str = "C:",
    dry_run: bool = False,
) -> tuple[int, int]:
    """Restore copied entries. Returns (restored_count, error_count)."""
    is_zip = archive_path.suffix.lower() == ".zip"
    meta_dir = (
        archive_path.parent / f"{archive_path.stem}_meta" if is_zip else archive_path / "META"
    )
    manifest_header = read_manifest_header(meta_dir / "manifest.json")
    entries = read_manifest_jsonl(meta_dir / Path(manifest_header.entries_file).name)

    restored = 0
    errors = 0
    for entry in entries:
        if entry.status != EntryStatus.COPIED:
            continue
        target = archive_to_target_path(entry.archive_path, user_map, target_drive)
        if dry_run:
            restored += 1
            continue
        try:
            if is_zip:
                _extract_zip_member(archive_path, entry.archive_path, target)
            else:
                source = archive_path / entry.archive_path.replace("/", "\\")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            restored += 1
        except OSError:
            errors += 1
    return restored, errors


def _extract_zip_member(zip_path: Path, archive_rel: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with (
        zipfile.ZipFile(zip_path, "r") as zf,
        zf.open(archive_rel.replace("\\", "/")) as src,
        target.open("wb") as dst,
    ):
        shutil.copyfileobj(src, dst)
