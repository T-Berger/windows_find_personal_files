"""Scan orchestration."""

import hashlib
import json
import platform
import socket
from dataclasses import dataclass
from pathlib import Path

from windows_personal_archive import __version__
from windows_personal_archive.archive.writer import ArchiveWriter
from windows_personal_archive.config.models import ArchiveConfig, EntryStatus
from windows_personal_archive.manifest.models import (
    Manifest,
    ManifestEntry,
    ManifestStats,
    utc_now_iso,
)
from windows_personal_archive.manifest.writer import write_manifest_json, write_manifest_jsonl
from windows_personal_archive.platform.windows import list_fixed_drives, users_root_path
from windows_personal_archive.scan.classify import classify_path
from windows_personal_archive.scan.path_map import source_to_archive_path
from windows_personal_archive.scan.rules import build_exclusion_list
from windows_personal_archive.scan.walker import walk_files


@dataclass(frozen=True)
class ScanResult:
    manifest: Manifest
    entries: list[ManifestEntry]
    meta_dir: Path


def plan_scan_roots(config: ArchiveConfig, output_path: Path) -> list[Path]:
    drives = list_fixed_drives(config.scan.include_removable)
    if not drives:
        raise RuntimeError("no drives found to scan")
    return drives


def run_scan(
    config: ArchiveConfig,
    output_path: Path,
    copy_files: bool,
    archive_writer: ArchiveWriter | None = None,
) -> ScanResult:
    roots = plan_scan_roots(config, output_path)
    exclusions = build_exclusion_list(
        config.exclude_prefixes,
        (output_path.resolve(),),
    )
    raw_entries = walk_files(roots, exclusions)
    users_root = users_root_path()

    manifest_entries: list[ManifestEntry] = []
    stats = ManifestStats()

    for raw in raw_entries:
        category = classify_path(raw.path, users_root)
        archive_rel = source_to_archive_path(raw.path)
        status = EntryStatus.PLANNED if not copy_files else EntryStatus.COPIED
        sha256: str | None = None

        if copy_files and archive_writer is not None:
            try:
                sha256 = archive_writer.add_file(raw.path, archive_rel, config.hash_files)
                status = EntryStatus.COPIED
                stats = ManifestStats(
                    files_copied=stats.files_copied + 1,
                    files_skipped=stats.files_skipped,
                    files_planned=stats.files_planned,
                    bytes_copied=stats.bytes_copied + raw.size_bytes,
                    errors=stats.errors,
                )
            except OSError as exc:
                status = EntryStatus.ERROR
                stats = ManifestStats(
                    files_copied=stats.files_copied,
                    files_skipped=stats.files_skipped,
                    files_planned=stats.files_planned,
                    bytes_copied=stats.bytes_copied,
                    errors=stats.errors + 1,
                )
                manifest_entries.append(
                    ManifestEntry(
                        source_path=str(raw.path),
                        archive_path=archive_rel,
                        category=category,
                        size_bytes=raw.size_bytes,
                        modified_at=raw.modified_at,
                        status=status,
                        status_reason=str(exc),
                        sha256=None,
                    )
                )
                continue
        elif not copy_files:
            stats = ManifestStats(
                files_copied=stats.files_copied,
                files_skipped=stats.files_skipped,
                files_planned=stats.files_planned + 1,
                bytes_copied=stats.bytes_copied,
                errors=stats.errors,
            )

        manifest_entries.append(
            ManifestEntry(
                source_path=str(raw.path),
                archive_path=archive_rel,
                category=category,
                size_bytes=raw.size_bytes,
                modified_at=raw.modified_at,
                status=status,
                sha256=sha256,
            )
        )

    meta_dir = _resolve_meta_dir(output_path, archive_writer)
    entries_rel = "META/manifest.jsonl"
    entries_path = meta_dir / "manifest.jsonl"
    write_manifest_jsonl(entries_path, manifest_entries)

    manifest = Manifest(
        schema_version="1.0",
        tool_version=__version__,
        created_at=utc_now_iso(),
        source_hostname=socket.gethostname(),
        source_os=f"{platform.system()} {platform.release()}",
        drives=tuple(str(d) for d in roots),
        entries_file=entries_rel,
        stats=stats,
    )
    write_manifest_json(meta_dir / "manifest.json", manifest)
    _write_meta_sidecars(meta_dir, config, manifest)

    return ScanResult(manifest=manifest, entries=manifest_entries, meta_dir=meta_dir)


def _resolve_meta_dir(output_path: Path, archive_writer: ArchiveWriter | None) -> Path:
    if archive_writer is not None:
        return archive_writer.meta_dir
    if output_path.suffix.lower() == ".zip":
        meta = output_path.parent / f"{output_path.stem}_meta"
        meta.mkdir(parents=True, exist_ok=True)
        return meta
    meta = output_path / "META"
    meta.mkdir(parents=True, exist_ok=True)
    return meta


def _write_meta_sidecars(meta_dir: Path, config: ArchiveConfig, manifest: Manifest) -> None:
    summary = meta_dir / "summary.txt"
    summary.write_text(
        "\n".join(
            [
                "Windows Personal Archive — Run Summary",
                f"Created: {manifest.created_at}",
                f"Files planned/copied: "
                f"{manifest.stats.files_planned + manifest.stats.files_copied}",
                f"Bytes copied: {manifest.stats.bytes_copied}",
                f"Errors: {manifest.stats.errors}",
            ]
        ),
        encoding="utf-8",
    )
    version_path = meta_dir / "version.json"
    version_path.write_text(
        json.dumps(
            {
                "tool_version": manifest.tool_version,
                "hostname": manifest.source_hostname,
                "os": manifest.source_os,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    config_path = meta_dir / "config.snapshot.json"
    config_path.write_text(
        json.dumps(
            {
                "output_format": config.output_format.value,
                "hash_files": config.hash_files,
                "full_drive_scan": config.scan.full_drive_scan,
                "users": list(config.scan.users),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
