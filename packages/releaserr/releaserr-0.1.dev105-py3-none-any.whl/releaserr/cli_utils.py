# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Any

import rich.console
from typer import Exit

if TYPE_CHECKING:
    from releaserr.config import ReleaserrConfig

CONSOLE = rich.console.Console(highlight=False)
ERR_CONSOLE = rich.console.Console(file=sys.stderr, highlight=False)
err = partial(ERR_CONSOLE.print, style="red")
msg = partial(err, style="blue")


@dataclass()
class CLIContext:
    project_name: str
    project_config: dict[str, Any]
    tool_config: dict[str, Any]
    global_config: ReleaserrConfig


class TyperChoices(str, Enum):
    @staticmethod
    def _generate_next_value_(name: str, *_) -> str:
        return name.lower()


__all__ = (
    "CLIContext",
    "CONSOLE",
    "ERR_CONSOLE",
    "Exit",
    "err",
    "msg",
)
