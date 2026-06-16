"""Known application data paths for classification."""

from dataclasses import dataclass

from windows_personal_archive.config.models import FileCategory


@dataclass(frozen=True)
class KnownAppPath:
    name: str
    relative_path: str
    category: FileCategory


# Relative to user profile (C:\Users\<user>\).
KNOWN_PROFILE_APPS: tuple[KnownAppPath, ...] = (
    KnownAppPath(
        "outlook_documents",
        "Documents\\Outlook Files",
        FileCategory.EMAIL,
    ),
)

# Relative to user profile with AppData prefix.
KNOWN_APPDATA_APPS: tuple[KnownAppPath, ...] = (
    KnownAppPath(
        "chrome",
        "AppData\\Local\\Google\\Chrome\\User Data",
        FileCategory.BROWSER,
    ),
    KnownAppPath(
        "firefox",
        "AppData\\Roaming\\Mozilla\\Firefox",
        FileCategory.BROWSER,
    ),
    KnownAppPath(
        "thunderbird",
        "AppData\\Roaming\\Thunderbird",
        FileCategory.EMAIL,
    ),
    KnownAppPath(
        "outlook_local",
        "AppData\\Local\\Microsoft\\Outlook",
        FileCategory.EMAIL,
    ),
    KnownAppPath(
        "outlook_roaming",
        "AppData\\Roaming\\Microsoft\\Outlook",
        FileCategory.EMAIL,
    ),
)

PROFILE_MEDIA_FOLDERS: frozenset[str] = frozenset(
    {"desktop", "pictures", "videos", "music", "downloads"}
)
PROFILE_DOCUMENT_FOLDERS: frozenset[str] = frozenset({"documents"})
