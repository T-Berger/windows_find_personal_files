"""Path mapping tests."""

from pathlib import Path

from windows_personal_archive.scan.path_map import archive_to_target_path, source_to_archive_path


def test_profile_document_maps_to_users() -> None:
    source = Path("C:/Users/alice/Documents/report.pdf")
    archive = source_to_archive_path(source)
    assert archive == "USERS/alice/PROFILE/Documents/report.pdf"


def test_appdata_maps_to_users_appdata() -> None:
    source = Path("C:/Users/alice/AppData/Roaming/Mozilla/Firefox/profiles.ini")
    archive = source_to_archive_path(source)
    assert archive == "USERS/alice/APPDATA/Roaming/Mozilla/Firefox/profiles.ini"


def test_drive_root_maps_to_drive_roots() -> None:
    source = Path("D:/Projects/code/main.py")
    archive = source_to_archive_path(source)
    assert archive == "DRIVE_ROOTS/D_/Projects/code/main.py"


def test_archive_to_target_profile() -> None:
    target = archive_to_target_path(
        "USERS/alice/PROFILE/Documents/report.pdf",
        {"alice": "alice"},
        "C:",
    )
    assert target == Path("C:/Users/alice/Documents/report.pdf")


def test_archive_to_target_user_remap() -> None:
    target = archive_to_target_path(
        "USERS/alice/PROFILE/Documents/report.pdf",
        {"alice": "bob"},
        "C:",
    )
    assert target == Path("C:/Users/bob/Documents/report.pdf")
