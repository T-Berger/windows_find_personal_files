"""Archive writers for folder layout and ZIP."""

import hashlib
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path


class ArchiveWriter(ABC):
    meta_dir: Path

    @abstractmethod
    def add_file(self, source: Path, archive_rel: str, hash_file: bool) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class FolderArchiveWriter(ArchiveWriter):
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)
        self.meta_dir = self._root / "META"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

    def add_file(self, source: Path, archive_rel: str, hash_file: bool) -> str | None:
        target = self._root / archive_rel.replace("/", "\\")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if hash_file:
            return _sha256(source)
        return None

    def close(self) -> None:
        return None


class ZipArchiveWriter(ArchiveWriter):
    def __init__(self, zip_path: Path) -> None:
        self._zip_path = zip_path
        self._zip_path.parent.mkdir(parents=True, exist_ok=True)
        self._zip = zipfile.ZipFile(self._zip_path, "w", compression=zipfile.ZIP_DEFLATED)
        self.meta_dir = self._zip_path.parent / f"{self._zip_path.stem}_meta"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

    def add_file(self, source: Path, archive_rel: str, hash_file: bool) -> str | None:
        self._zip.write(source, arcname=archive_rel.replace("\\", "/"))
        if hash_file:
            return _sha256(source)
        return None

    def close(self) -> None:
        self._zip.close()


def create_archive_writer(output_path: Path, output_format: str) -> ArchiveWriter:
    if output_format == "zip" or output_path.suffix.lower() == ".zip":
        return ZipArchiveWriter(output_path)
    return FolderArchiveWriter(output_path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
