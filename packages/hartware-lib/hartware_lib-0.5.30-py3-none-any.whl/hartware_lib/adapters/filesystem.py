from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from glob import glob
from pathlib import Path
from shutil import rmtree
from typing import IO, AsyncIterator, Iterator, List, Union

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper


class FileAlreadyExists(Exception):
    pass


class DirectoryAlreadyExists(Exception):
    pass


@dataclass
class FileAdapter:
    path: Path

    def touch(self, raise_if_exists: bool = False) -> bool:
        if self.exists:
            if raise_if_exists:
                raise FileAlreadyExists()

            return False

        self.directory.create()

        return self.write("")

    @property
    def directory(self) -> DirectoryAdapter:
        return DirectoryAdapter(self.path.parent)

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def delete(self) -> bool:
        if self.exists:
            self.path.unlink()

            return True

        return False

    @contextmanager
    def open(self, mode: str = "r") -> Iterator[IO[str]]:
        with open(self.path, mode=mode) as file:
            yield file

    def read(self) -> str:
        with self.open(mode="r") as file:
            return file.read()

    def write(self, data: str = "") -> bool:
        with self.open(mode="w") as file:
            file.write(data)

            return True

    @asynccontextmanager
    async def async_open(self, mode: str = "r") -> AsyncIterator[AsyncTextIOWrapper]:
        async with aiofiles.open(self.path, mode=mode) as file:  # type: ignore[call-overload]
            yield file

    async def async_read(self) -> str:
        async with self.async_open(mode="r") as file:
            return await file.read()

    async def async_write(self, data: str = "") -> bool:
        async with self.async_open(mode="w") as file:
            await file.write(data)
            await file.flush()

            return True


@dataclass
class DirectoryAdapter:
    path: Path

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def parent(self) -> DirectoryAdapter:
        return DirectoryAdapter(self.path.parent)

    def create(self, raise_if_exists: bool = False) -> bool:
        if self.exists:
            if raise_if_exists:
                raise DirectoryAlreadyExists()

            return False

        self.path.mkdir(parents=True)

        return True

    def file(self, path: Union[str, Path]) -> FileAdapter:
        return FileAdapter(self.path / path)

    def delete(self) -> bool:
        if self.exists:
            rmtree(self.path)

            return True

        return False

    def sub(self, sub_dir_path: Path) -> DirectoryAdapter:
        return DirectoryAdapter(self.path / sub_dir_path)

    def search(self, path_regex: Union[str, Path] = "*") -> List[FileAdapter]:
        return [
            FileAdapter(Path(path))
            for path in glob(str(self.path / "**" / path_regex), recursive=True)
        ]
