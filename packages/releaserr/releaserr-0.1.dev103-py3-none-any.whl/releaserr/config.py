# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Global releaserr config
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel
from sourcehut.config import SrhtConfig

from releaserr.copr import CoprConfig
from releaserr.toml import load as toml_load

try:
    XDG_CONFIG_HOME = Path(os.environ["XDG_CONFIG_HOME"])
except KeyError:
    XDG_CONFIG_HOME = Path.home() / ".config"

CONFIG_PATH = XDG_CONFIG_HOME / "releaserr.toml"

DEFAULT_LICENSE = "MIT"


class ReleaserrConfig(BaseModel):
    copr: CoprConfig = CoprConfig()
    sourcehut: SrhtConfig = SrhtConfig().read_config()
    default_license: str = DEFAULT_LICENSE

    @classmethod
    def read_config(cls, path: Path | None = None) -> ReleaserrConfig:
        path = path or CONFIG_PATH
        try:
            with path.open("rb") as fp:
                return cls(**toml_load(fp))
        except FileNotFoundError:
            return cls()
