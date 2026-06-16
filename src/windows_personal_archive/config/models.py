"""Configuration models."""

from dataclasses import dataclass, field
from enum import StrEnum


class OutputFormat(StrEnum):
    ZIP = "zip"
    FOLDER = "folder"


class EntryStatus(StrEnum):
    COPIED = "copied"
    SKIPPED = "skipped"
    ERROR = "error"
    PLANNED = "planned"


class FileCategory(StrEnum):
    DOCUMENTS = "documents"
    MEDIA = "media"
    CONFIG = "config"
    CREDENTIALS = "credentials-adjacent"
    EMAIL = "email"
    BROWSER = "browser"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PathRule:
    path_prefix: str
    category: FileCategory = FileCategory.DOCUMENTS


@dataclass(frozen=True)
class ScanConfig:
    include_removable: bool = False
    users: tuple[str, ...] = ()
    full_drive_scan: bool = True


@dataclass(frozen=True)
class ArchiveConfig:
    output_format: OutputFormat = OutputFormat.ZIP
    hash_files: bool = False
    scan: ScanConfig = field(default_factory=ScanConfig)
    exclude_prefixes: tuple[str, ...] = ()
    include_rules: tuple[PathRule, ...] = ()
    verbose: bool = False
