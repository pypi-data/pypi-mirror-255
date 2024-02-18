# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from typing import TYPE_CHECKING

from releaserr.cli_utils import ERR_CONSOLE

if TYPE_CHECKING:
    from _typeshed import StrPath


def run(
    cmd: Sequence[StrPath], log: bool = True, **kwargs
) -> subprocess.CompletedProcess:
    kwargs.setdefault("check", True)
    if kwargs.get("capture_output"):
        kwargs.setdefault("text", True)
    if log:
        ERR_CONSOLE.print(f"Running: {tuple(map(str, cmd))}", style="green")
    return subprocess.run(cmd, **kwargs)  # noqa: PLW1510
