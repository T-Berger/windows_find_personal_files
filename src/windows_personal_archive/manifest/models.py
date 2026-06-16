"""Manifest models."""

from dataclasses import dataclass
from datetime import datetime

from windows_personal_archive.config.models import EntryStatus, FileCategory


@dataclass(frozen=True)
class ManifestEntry:
    source_path: str
    archive_path: str
    category: FileCategory
    size_bytes: int
    modified_at: str
    status: EntryStatus
    status_reason: str | None = None
    sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "source_path": self.source_path,
            "archive_path": self.archive_path,
            "category": self.category.value,
            "size_bytes": self.size_bytes,
            "modified_at": self.modified_at,
            "status": self.status.value,
        }
        if self.status_reason is not None:
            data["status_reason"] = self.status_reason
        if self.sha256 is not None:
            data["sha256"] = self.sha256
        return data


@dataclass(frozen=True)
class ManifestStats:
    files_copied: int = 0
    files_skipped: int = 0
    files_planned: int = 0
    bytes_copied: int = 0
    errors: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "files_copied": self.files_copied,
            "files_skipped": self.files_skipped,
            "files_planned": self.files_planned,
            "bytes_copied": self.bytes_copied,
            "errors": self.errors,
        }


@dataclass(frozen=True)
class Manifest:
    schema_version: str
    tool_version: str
    created_at: str
    source_hostname: str
    source_os: str
    drives: tuple[str, ...]
    entries_file: str
    stats: ManifestStats

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "created_at": self.created_at,
            "source": {
                "hostname": self.source_hostname,
                "os": self.source_os,
                "drives": list(self.drives),
            },
            "entries_file": self.entries_file,
            "stats": self.stats.to_dict(),
        }


def utc_now_iso() -> str:
    return datetime.now().astimezone().isoformat()
