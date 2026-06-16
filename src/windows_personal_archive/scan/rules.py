"""Default exclusion rules for full-drive scan."""

from pathlib import Path

# Path segments matched case-insensitively (contains check).
DEFAULT_EXCLUSION_SEGMENTS: tuple[str, ...] = (
    "\\windows\\",
    "\\program files\\",
    "\\program files (x86)\\",
    "\\programdata\\",
    "\\$recycle.bin\\",
    "\\system volume information\\",
    "\\windows\\winsxs\\",
    "\\appdata\\local\\temp\\",
    "\\appdata\\local\\microsoft\\windows\\inetcache\\",
)

DEFAULT_EXCLUSION_FILES: tuple[str, ...] = (
    "pagefile.sys",
    "hiberfil.sys",
    "swapfile.sys",
)

SYSTEM_USER_NAMES: frozenset[str] = frozenset(
    {
        "default",
        "default user",
        "defaultuser0",
        "public",
        "all users",
    }
)


def normalize_path_for_match(path: str) -> str:
    return path.replace("/", "\\").lower()


def build_exclusion_list(
    extra_prefixes: tuple[str, ...] = (),
    extra_paths: tuple[Path, ...] = (),
) -> list[str]:
    """Return exclusion prefixes for the Rust scanner and Python walker."""
    exclusions: list[str] = list(DEFAULT_EXCLUSION_SEGMENTS) + list(DEFAULT_EXCLUSION_FILES)
    for prefix in extra_prefixes:
        exclusions.append(normalize_path_for_match(prefix))
    for path in extra_paths:
        exclusions.append(normalize_path_for_match(str(path.resolve())))
    return exclusions


def is_excluded(path: Path, exclusions: list[str]) -> bool:
    normalized = normalize_path_for_match(str(path))
    return any(ex in normalized for ex in exclusions)
