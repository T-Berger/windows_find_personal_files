"""Drive and user discovery."""

import os
import sys
from pathlib import Path

from windows_personal_archive.scan.rules import SYSTEM_USER_NAMES

DRIVE_FIXED = 3


def list_fixed_drives(include_removable: bool = False) -> list[Path]:
    fixture = os.environ.get("WPA_TEST_FIXTURE_ROOT")
    if fixture:
        return [Path(fixture)]
    if sys.platform != "win32":
        return []
    return _windows_fixed_drives(include_removable)


def _windows_fixed_drives(include_removable: bool) -> list[Path]:
    import ctypes

    kernel32 = ctypes.windll.kernel32
    buf = ctypes.create_unicode_buffer(256)
    length = kernel32.GetLogicalDriveStringsW(256, buf)
    if length == 0:
        return []
    drives_str = buf.value
    drives: list[Path] = []
    for drive in drives_str.split("\x00"):
        if not drive:
            continue
        drive_type = kernel32.GetDriveTypeW(drive)
        if drive_type == DRIVE_FIXED or (include_removable and drive_type == 2):
            drives.append(Path(drive))
    return drives


def list_user_profiles(users_filter: tuple[str, ...] = ()) -> list[tuple[str, Path]]:
    """Return (username, profile_path) for local profiles."""
    if sys.platform != "win32":
        return _fixture_users(users_filter)

    users_dir = Path(os.environ.get("SYSTEMDRIVE", "C:") + "\\Users")
    if not users_dir.is_dir():
        return []

    profiles: list[tuple[str, Path]] = []
    for entry in users_dir.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name.lower() in SYSTEM_USER_NAMES:
            continue
        if users_filter and name not in users_filter:
            continue
        profiles.append((name, entry))
    return profiles


def _fixture_users(users_filter: tuple[str, ...]) -> list[tuple[str, Path]]:
    fixture = os.environ.get("WPA_TEST_FIXTURE_ROOT")
    if not fixture:
        return []
    users_dir = Path(fixture) / "Users"
    if not users_dir.is_dir():
        return []
    profiles: list[tuple[str, Path]] = []
    for entry in users_dir.iterdir():
        if entry.is_dir() and entry.name.lower() not in SYSTEM_USER_NAMES:
            if users_filter and entry.name not in users_filter:
                continue
            profiles.append((entry.name, entry))
    return profiles


def users_root_path() -> Path | None:
    if sys.platform == "win32":
        return Path(os.environ.get("SYSTEMDRIVE", "C:") + "\\Users")
    fixture = os.environ.get("WPA_TEST_FIXTURE_ROOT")
    if fixture:
        return Path(fixture) / "Users"
    return None
