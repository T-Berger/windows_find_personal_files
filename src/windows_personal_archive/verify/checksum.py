"""Archive integrity verification."""

import hashlib
import zipfile
from pathlib import Path

from windows_personal_archive.config.models import EntryStatus
from windows_personal_archive.manifest.models import ManifestEntry
from windows_personal_archive.manifest.writer import read_manifest_header, read_manifest_jsonl


def verify_archive(archive_path: Path) -> tuple[int, int]:
    """Verify manifest entries exist and optional hashes match. Returns (ok, failed)."""
    is_zip = archive_path.suffix.lower() == ".zip"
    meta_dir = (
        archive_path.parent / f"{archive_path.stem}_meta" if is_zip else archive_path / "META"
    )
    manifest_header = read_manifest_header(meta_dir / "manifest.json")
    entries = read_manifest_jsonl(meta_dir / Path(manifest_header.entries_file).name)

    ok = 0
    failed = 0
    for entry in entries:
        if entry.status != EntryStatus.COPIED:
            continue
        try:
            if is_zip:
                if not _zip_member_ok(archive_path, entry):
                    failed += 1
                    continue
            else:
                path = archive_path / entry.archive_path.replace("/", "\\")
                if not path.is_file():
                    failed += 1
                    continue
                if entry.sha256 and _sha256(path) != entry.sha256:
                    failed += 1
                    continue
            ok += 1
        except OSError:
            failed += 1
    return ok, failed


def _zip_member_ok(zip_path: Path, entry: ManifestEntry) -> bool:
    arcname = entry.archive_path.replace("\\", "/")
    with zipfile.ZipFile(zip_path, "r") as zf:
        if arcname not in zf.namelist():
            return False
        if entry.sha256:
            data = zf.read(arcname)
            digest = hashlib.sha256(data).hexdigest()
            return digest == entry.sha256
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
