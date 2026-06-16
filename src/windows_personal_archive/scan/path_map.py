"""Map source paths to archive-relative paths and back."""

import re
from pathlib import Path

_USERS_PATTERN = re.compile(r"^([A-Za-z]):\\Users\\([^\\]+)\\(.*)$", re.IGNORECASE)


def drive_label(drive: str) -> str:
    letter = drive.rstrip("\\:").upper()
    if len(letter) > 1 and letter.endswith(":"):
        letter = letter[0]
    return f"{letter}_"


def source_to_archive_path(source: Path) -> str:
    """Map an absolute source path to an archive-relative POSIX path."""
    resolved = str(source.resolve())
    normalized = resolved.replace("/", "\\")
    users_match = _USERS_PATTERN.match(normalized)
    if users_match:
        username = users_match.group(2)
        remainder = users_match.group(3)
        remainder_norm = remainder.replace("\\", "/")
        lower_remainder = remainder.lower()
        if lower_remainder.startswith("appdata\\") or lower_remainder.startswith("appdata/"):
            sub = remainder_norm[len("AppData/") :]
            return f"USERS/{username}/APPDATA/{sub}"
        return f"USERS/{username}/PROFILE/{remainder_norm}"

    drive = normalized[:3]
    if len(normalized) >= 3 and normalized[1] == ":":
        rel = normalized[3:].replace("\\", "/")
        label = drive_label(drive)
        return f"DRIVE_ROOTS/{label}/{rel}"

    safe = normalized.replace("\\", "/").replace(":", "_")
    return f"DRIVE_ROOTS/UNKNOWN/{safe}"


def archive_to_target_path(
    archive_rel: str,
    user_map: dict[str, str],
    default_drive: str = "C:",
) -> Path:
    """Map an archive-relative path to a target filesystem path."""
    parts = archive_rel.replace("\\", "/").split("/")
    if not parts:
        raise ValueError("empty archive path")

    if parts[0] == "USERS" and len(parts) >= 3:
        source_user = parts[1]
        target_user = user_map.get(source_user, source_user)
        section = parts[2]
        rest = parts[3:]
        base = Path(f"{default_drive}\\Users\\{target_user}")
        if section == "PROFILE":
            return base.joinpath(*rest)
        if section == "APPDATA":
            return base.joinpath("AppData", *rest)
        return base.joinpath(*parts[2:])

    if parts[0] == "DRIVE_ROOTS" and len(parts) >= 2:
        drive_label_part = parts[1]
        drive_letter = drive_label_part.replace("_", "").upper()
        drive = f"{drive_letter}:"
        rest = parts[2:]
        return Path(drive + "\\").joinpath(*rest)

    return Path(default_drive + "\\").joinpath(*parts)
