"""Classification tests."""

from pathlib import Path

from windows_personal_archive.config.models import FileCategory
from windows_personal_archive.scan.classify import classify_path


def test_classify_firefox_as_browser() -> None:
    path = Path("C:/Users/alice/AppData/Roaming/Mozilla/Firefox/profiles.ini")
    assert classify_path(path) == FileCategory.BROWSER


def test_classify_chrome_as_browser() -> None:
    path = Path("C:/Users/alice/AppData/Local/Google/Chrome/User Data/Default/Preferences")
    assert classify_path(path) == FileCategory.BROWSER


def test_classify_documents() -> None:
    path = Path("C:/Users/alice/Documents/notes.txt")
    assert classify_path(path) == FileCategory.DOCUMENTS
