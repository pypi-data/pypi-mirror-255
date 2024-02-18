# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Handle scdocs manpages
"""

from __future__ import annotations

import shlex
from collections.abc import Sequence
from pathlib import Path

from releaserr.cli_utils import msg
from releaserr.subprocess_util import run

DEFAULT_TO = "markdown_strict+pipe_tables"


def scd2md(
    files: Sequence[Path],
    output_dir: Path | None = None,
    log: bool = False,
    *,
    to: str = DEFAULT_TO,
) -> list[Path]:
    """
    Long, terrible pipeline to convert scd to markdown
    """
    created: list[Path] = []
    for path in files:
        directory = output_dir or path.parent
        base = path.with_suffix("")
        man_type = int(base.suffix.lstrip("."))
        new = directory / f"{base.with_suffix('').name}{man_type}.md"
        if log:
            msg(f"Converting {path} to {new}")
        # fmt: off
        cmd = [
            "sh", "-euo", "pipefail", "-c",
            # Convert scdoc to html
            f"scd2html < {shlex.quote(str(path))}"
            # Remove aria-hidden attributes so pandoc doesn't try to convert them
            "| sed 's|aria-hidden=\"true\"||'"
            "| pandoc --from html "
            # mkdocs doesn't support most of the pandoc markdown extensions.
            # Use markdown_strict and only enable pipe_tables.
            f"--to {shlex.quote(to)}"
            "| sed "
            # Remove anchors that scd2html inserts
            r"-e 's| \[¶\].*||' "
            f"> {shlex.quote(str(new))}",
        ]
        # fmt: on
        run(cmd, log=False)
        created.append(new)
    return created
