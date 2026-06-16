"""Load configuration from environment and optional TOML file."""

import os
import tomllib
from pathlib import Path

from windows_personal_archive.config.models import (
    ArchiveConfig,
    FileCategory,
    OutputFormat,
    PathRule,
    ScanConfig,
)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _parse_users(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    return tuple(u.strip() for u in raw.split(",") if u.strip())


def load_config(config_path: Path | None = None) -> ArchiveConfig:
    """Build effective config from defaults, file, and environment."""
    output_format = OutputFormat.ZIP
    hash_files = False
    include_removable = False
    users: tuple[str, ...] = ()
    full_drive_scan = True
    exclude_prefixes: tuple[str, ...] = ()
    include_rules: tuple[PathRule, ...] = ()
    verbose = False

    if config_path and config_path.is_file():
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        archive = data.get("archive", {})
        scan = data.get("scan", {})
        fmt = archive.get("output_format", "zip")
        output_format = OutputFormat(fmt)
        hash_files = bool(archive.get("hash_files", False))
        include_removable = bool(scan.get("include_removable", False))
        users = tuple(scan.get("users", []))
        full_drive_scan = bool(scan.get("full_drive_scan", True))
        verbose = bool(data.get("verbose", False))
        exclude_prefixes = tuple(
            item.get("path_prefix", "")
            for item in scan.get("exclude", [])
            if item.get("path_prefix")
        )
        include_rules = tuple(
            PathRule(
                path_prefix=item["path_prefix"],
                category=FileCategory(item.get("category", "documents")),
            )
            for item in scan.get("include", [])
            if item.get("path_prefix")
        )

    hash_files = _env_bool("WPA_HASH", hash_files)
    include_removable = _env_bool("WPA_INCLUDE_REMOVABLE", include_removable)
    users = _parse_users(os.environ.get("WPA_USERS")) or users
    verbose = _env_bool("WPA_VERBOSE", verbose)

    return ArchiveConfig(
        output_format=output_format,
        hash_files=hash_files,
        scan=ScanConfig(
            include_removable=include_removable,
            users=users,
            full_drive_scan=full_drive_scan,
        ),
        exclude_prefixes=exclude_prefixes,
        include_rules=include_rules,
        verbose=verbose,
    )


def infer_output_format(output_path: Path) -> OutputFormat:
    if output_path.suffix.lower() == ".zip":
        return OutputFormat.ZIP
    return OutputFormat.FOLDER
