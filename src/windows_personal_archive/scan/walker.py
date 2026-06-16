"""Filesystem walking — Rust binary with Python fallback."""

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from windows_personal_archive.scan.rules import is_excluded


@dataclass(frozen=True)
class RawScanEntry:
    path: Path
    size_bytes: int
    modified_at: str


def find_scan_binary() -> Path | None:
    env = os.environ.get("WPA_SCAN_BINARY")
    if env:
        candidate = Path(env)
        if candidate.is_file():
            return candidate

    repo_root = Path(__file__).resolve().parents[3]
    names = ["wpa-scan.exe", "wpa-scan"]
    for sub in ("release", "debug"):
        for name in names:
            candidate = repo_root / "target" / sub / name
            if candidate.is_file():
                return candidate
    return None


def walk_files(
    roots: list[Path],
    exclusions: list[str],
    exclude_file: Path | None = None,
) -> list[RawScanEntry]:
    binary = find_scan_binary()
    if binary is not None:
        return _walk_rust(binary, roots, exclusions, exclude_file)
    return _walk_python(roots, exclusions)


def _walk_rust(
    binary: Path,
    roots: list[Path],
    exclusions: list[str],
    exclude_file: Path | None,
) -> list[RawScanEntry]:
    temp_exclude = exclude_file
    if temp_exclude is None:
        temp_exclude = Path(os.environ.get("TEMP", ".")) / "wpa_excludes.txt"
        temp_exclude.write_text("\n".join(exclusions), encoding="utf-8")

    cmd = [str(binary)]
    for root in roots:
        cmd.append(str(root))
    cmd.extend(["--exclude-file", str(temp_exclude)])

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"wpa-scan failed: {result.stderr}")

    entries: list[RawScanEntry] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        modified = datetime.fromtimestamp(int(data["modified_secs"])).astimezone().isoformat()
        entries.append(
            RawScanEntry(
                path=Path(data["path"]),
                size_bytes=int(data["size_bytes"]),
                modified_at=modified,
            )
        )
    return entries


def _walk_python(roots: list[Path], exclusions: list[str]) -> list[RawScanEntry]:
    entries: list[RawScanEntry] = []
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            current = Path(dirpath)
            if is_excluded(current, exclusions):
                dirnames.clear()
                continue
            dirnames[:] = [name for name in dirnames if not is_excluded(current / name, exclusions)]
            for name in filenames:
                file_path = current / name
                if is_excluded(file_path, exclusions):
                    continue
                try:
                    stat = file_path.stat()
                except OSError:
                    continue
                modified = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat()
                entries.append(
                    RawScanEntry(
                        path=file_path,
                        size_bytes=stat.st_size,
                        modified_at=modified,
                    )
                )
    return entries
