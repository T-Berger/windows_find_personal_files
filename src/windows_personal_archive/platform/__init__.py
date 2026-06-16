"""Platform helpers."""

from windows_personal_archive.platform.windows import (
    list_fixed_drives,
    list_user_profiles,
    users_root_path,
)

__all__ = ["list_fixed_drives", "list_user_profiles", "users_root_path"]
