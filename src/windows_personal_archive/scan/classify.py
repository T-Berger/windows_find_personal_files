"""File classification."""

from pathlib import Path

from windows_personal_archive.config.models import FileCategory
from windows_personal_archive.scan.known_apps import (
    KNOWN_APPDATA_APPS,
    KNOWN_PROFILE_APPS,
    PROFILE_DOCUMENT_FOLDERS,
    PROFILE_MEDIA_FOLDERS,
)
from windows_personal_archive.scan.rules import normalize_path_for_match


def classify_path(path: Path, users_root: Path | None = None) -> FileCategory:
    """Assign a category based on path heuristics and known applications."""
    normalized = normalize_path_for_match(str(path))
    users_marker = "\\users\\"

    if "\\.ssh\\" in normalized or "\\.gnupg\\" in normalized:
        return FileCategory.CREDENTIALS

    if users_marker in normalized:
        for app in KNOWN_APPDATA_APPS:
            app_norm = normalize_path_for_match(app.relative_path)
            if app_norm in normalized:
                return app.category
        for app in KNOWN_PROFILE_APPS:
            app_norm = normalize_path_for_match(app.relative_path)
            if app_norm in normalized:
                return app.category

        if "\\appdata\\" in normalized:
            return FileCategory.CONFIG

        parts = normalized.split(users_marker, 1)[1].split("\\")
        if len(parts) >= 3:
            folder = parts[1].lower()
            if folder in PROFILE_MEDIA_FOLDERS:
                return FileCategory.MEDIA
            if folder in PROFILE_DOCUMENT_FOLDERS:
                return FileCategory.DOCUMENTS

    if users_root is not None:
        try:
            rel = path.resolve().relative_to(users_root.resolve())
            if rel.parts and rel.parts[0].lower() in PROFILE_MEDIA_FOLDERS:
                return FileCategory.MEDIA
        except ValueError:
            pass

    return FileCategory.UNKNOWN
