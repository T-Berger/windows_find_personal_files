"""Manifest serialization."""

import json
from pathlib import Path

from windows_personal_archive.manifest.models import Manifest, ManifestEntry


def write_manifest_json(path: Path, manifest: Manifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def write_manifest_jsonl(path: Path, entries: list[ManifestEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry.to_dict()) + "\n")


def read_manifest_jsonl(path: Path) -> list[ManifestEntry]:
    from windows_personal_archive.config.models import EntryStatus, FileCategory

    entries: list[ManifestEntry] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            entries.append(
                ManifestEntry(
                    source_path=data["source_path"],
                    archive_path=data["archive_path"],
                    category=FileCategory(data["category"]),
                    size_bytes=int(data["size_bytes"]),
                    modified_at=data["modified_at"],
                    status=EntryStatus(data["status"]),
                    status_reason=data.get("status_reason"),
                    sha256=data.get("sha256"),
                )
            )
    return entries


def read_manifest_header(path: Path) -> Manifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    from windows_personal_archive.manifest.models import ManifestStats

    stats_raw = data.get("stats", {})
    stats = ManifestStats(
        files_copied=int(stats_raw.get("files_copied", 0)),
        files_skipped=int(stats_raw.get("files_skipped", 0)),
        files_planned=int(stats_raw.get("files_planned", 0)),
        bytes_copied=int(stats_raw.get("bytes_copied", 0)),
        errors=int(stats_raw.get("errors", 0)),
    )
    source = data.get("source", {})
    return Manifest(
        schema_version=data.get("schema_version", "1.0"),
        tool_version=data.get("tool_version", "0.0.0"),
        created_at=data.get("created_at", ""),
        source_hostname=source.get("hostname", ""),
        source_os=source.get("os", ""),
        drives=tuple(source.get("drives", [])),
        entries_file=data.get("entries_file", "META/manifest.jsonl"),
        stats=stats,
    )
