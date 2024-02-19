# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from releaserr.cli_utils import Exit, err
from releaserr.subprocess_util import run
from releaserr.toml import Reader, Writer
from releaserr.toml import dump as dump_toml
from releaserr.toml import load as load_toml


class VersionHandler(metaclass=ABCMeta):
    changed_files: Sequence[Path] = ()

    def __init__(self, project_name: str, config: dict[str, Any]):
        self.project_name = project_name
        self.config = config
        if hasattr(self, "__post_init__"):
            self.__post_init__()

    @abstractmethod
    def set_version(self, version: str) -> None:
        pass

    def post_version(self) -> str:
        version = self.get_version()
        version += ".post0"
        self.set_version(version)
        return version

    @abstractmethod
    def get_version(self) -> str:
        pass


class HatchVersionHandler(VersionHandler):
    def set_version(self, version: str) -> None:
        run(["hatch", "version", version])

    def get_version(self) -> str:
        return run(["hatch", "version"], capture_output=True).stdout.strip()

    def post_version(self) -> str:
        run(["hatch", "version", "post"], capture_output=True)
        return self.get_version()


class InitPyVersion(VersionHandler):
    PATTERN = re.compile(
        r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2',
        flags=re.MULTILINE,
    )
    version_file: Path

    def __post_init__(self) -> None:
        version_file: Path | None = None
        if "version-file" in self.config:
            version_file = Path(self.config["version-file"])
        else:
            for path in (
                Path("src", self.project_name, "__init__.py"),
                Path(self.project_name, "__init__.py"),
            ):
                if path.exists():
                    version_file = path
        if not version_file:
            err("Failed to find version file!")
            raise Exit(1)

        self.version_file: Path = version_file
        self.changed_files = (self.version_file,)

    def get_match(self) -> tuple[re.Match, str]:
        contents = self.version_file.read_text(encoding="utf-8")
        match = self.PATTERN.search(contents)
        if not match:
            err(f"Failed to parse {self.version_file}!")
            raise Exit(1)
        return match, contents

    def get_version(self) -> str:
        match, _ = self.get_match()
        return match["version"]

    def set_version(self, version: str) -> None:
        match, contents = self.get_match()
        start, end = match.span("version")
        self.version_file.write_text(f"{contents[:start]}{version}{contents[end:]}")


class PyprojectTomlVersion(VersionHandler):
    version_file: Path

    def __post_init__(self) -> None:
        self.version_file: Path = Path("pyproject.toml")
        self.changed_files = (self.version_file,)

    def get_version(self) -> str:
        with self.version_file.open("rb") as fp:
            data = load_toml(fp)
        return data["project"]["version"]

    def set_version(self, version: str) -> None:
        with self.version_file.open("rb") as fp:
            data = load_toml(fp, prefered_reader=Reader.TOMLKIT, allow_fallback=False)
        with self.version_file.open("wb") as fp:
            data["project"]["version"] = version
            dump_toml(data, fp, prefered_writer=Writer.TOMLKIT, allow_fallback=False)


VERSION_SOURCES: dict[str, type[VersionHandler]] = {
    "file": InitPyVersion,
    "hatch": HatchVersionHandler,
    "pyproject.toml": PyprojectTomlVersion,
}
