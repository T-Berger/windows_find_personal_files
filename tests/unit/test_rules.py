"""Exclusion rule tests."""

from pathlib import Path

from windows_personal_archive.scan.rules import is_drive_root, is_excluded, normalize_path_for_match


def test_normalize_path() -> None:
    assert normalize_path_for_match("C:/Windows/System32") == "c:\\windows\\system32"


def test_excludes_windows_path() -> None:
    exclusions = ["\\windows\\"]
    assert is_excluded(Path("C:/Windows/System32/kernel.dll"), exclusions)


def test_allows_user_document() -> None:
    exclusions = ["\\windows\\"]
    assert not is_excluded(Path("C:/Users/alice/Documents/file.txt"), exclusions)


def test_drive_root_not_used_as_exclusion_prefix() -> None:
    from windows_personal_archive.scan.rules import build_exclusion_list

    exclusions = build_exclusion_list(extra_paths=(Path("C:/"),))
    assert not is_excluded(Path("C:/Users/alice/Documents/file.txt"), exclusions)


def test_is_drive_root() -> None:
    assert is_drive_root(Path("C:/"))
    assert not is_drive_root(Path("C:/Users"))
