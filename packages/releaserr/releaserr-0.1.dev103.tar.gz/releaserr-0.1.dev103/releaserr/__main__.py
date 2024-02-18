#!/usr/bin/env python3

# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Simple, purpose-built release manager for @gotmax23's projects
"""

import contextlib
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    TypeAlias,
    cast,
)

import httpx
import typer
from click.termui import edit
from typing_extensions import Annotated

from releaserr import scd
from releaserr.cli_utils import CONSOLE, CLIContext, TyperChoices, err, msg
from releaserr.config import ReleaserrConfig
from releaserr.new import APP as new_commands
from releaserr.subprocess_util import run
from releaserr.toml import load as load_toml
from releaserr.version import VERSION_SOURCES, VersionHandler

if TYPE_CHECKING:
    from _typeshed import StrPath

APP = typer.Typer(
    context_settings=dict(help_option_names=["-h", "--help"]), help=__doc__
)
APP.add_typer(new_commands, name="new")


def git(cmd: Sequence["StrPath"], **kwargs) -> subprocess.CompletedProcess:
    return run(("git", *cmd), **kwargs)


def add_frag(frag: Path, file: Path, version: str) -> Tuple[str, List[str]]:
    date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    frag_heading = f"## {version} - {date} <a id={version!r}></a>\n"
    frag_lines: list[str] = [frag_heading, "\n"]
    with frag.open() as fp:
        raw_frag_lines = list(fp)
        frag_lines.extend(raw_frag_lines)
    lines: list[str] = []
    with file.open("r+") as fp:
        needs_append = True
        for line in fp:
            if needs_append and line.startswith("##"):
                if frag_lines[0] != line:
                    lines.extend((*frag_lines, "\n"))
                needs_append = False
            lines.append(line)
        if needs_append:
            lines.extend(("\n", *frag_lines))
        fp.seek(0)
        fp.writelines(lines)
        fp.truncate()
    return frag_heading, raw_frag_lines


def format_git_msg(project: str, version: str, raw_frag_lines: List[str]) -> List[str]:
    lines: list[str] = [f"{project} {version}\n", "\n"]
    for line in raw_frag_lines:
        if line.startswith("### "):
            line = line[4:].rstrip() + ":" + "\n"
        lines.append(line)
    return lines


@APP.command()
def ensure_clean():
    if git(
        ["status", "--porcelain", "--untracked-files"], capture_output=True
    ).stdout.strip():
        msg = "There are untracked and/or modified files."
        err(msg)
        raise typer.Exit(1)


@APP.command()
def check_tag(version: str) -> None:
    tag = "v" + version
    tags = git(["tag", "--list"], capture_output=True).stdout.splitlines()
    if tag in tags:
        err(f"{tag} is already tagged")
        raise typer.Exit(1)


@APP.command()
def clog(
    *,
    version: str,
    git_msg_file: Path = Path("GIT_MSG"),
    frag: Path = Path("FRAG.md"),
    output: Path = Path("NEWS.md"),
    project: str = Path.cwd().name,
    commit: bool = False,
    tag: bool = False,
) -> None:
    if tag:
        commit = True
    _, lines = add_frag(frag, output, version)
    with git_msg_file.open("w") as fp:
        fp.writelines(format_git_msg(project, version, lines))
    if tag or commit:
        git(["add", "NEWS.md"])
        git(["commit", "-S", "-m", f"Release {version}"])
    if tag:
        ensure_clean()
        edit(filename=str(git_msg_file))
        if not git_msg_file.read_text().strip():
            err("Exiting...")
            raise typer.Exit(1)
        git(["tag", "-s", "-F", git_msg_file, f"v{version}"])


class BuildBackend(TyperChoices):
    FLIT_CORE = "flit_core"
    HATCHLING = "hatchling"
    GENERIC = "generic"


BUILD_COMMANDS: dict[BuildBackend, tuple["StrPath", ...]] = {
    BuildBackend.FLIT_CORE: ("flit", "build"),
    BuildBackend.HATCHLING: ("hatch", "build"),
    BuildBackend.GENERIC: ("python", "-m", "build"),
}


@contextlib.contextmanager
def chdir(directory: "StrPath") -> Iterator[Path]:
    """
    Non-reentrant contextmanager to change directories

    Yields:
        The old directory
    """
    cwd = Path.cwd()
    try:
        msg(f"cd {directory}")
        os.chdir(directory)
        yield cwd
    finally:
        msg("cd -")
        os.chdir(cwd)


@contextlib.contextmanager
def isolated_src() -> Iterator[Path]:
    """
    Create an isolated directory that only contains the latest git HEAD
    """
    branch: str = run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True
    ).stdout.strip()
    with tempfile.TemporaryDirectory() as _tmpdir:
        tmp = Path(_tmpdir)
        output = tmp / "build"
        run(["git", "clone", Path.cwd(), output, "--branch", branch])
        with chdir(tmp / "build") as old:
            yield old


def sign_artifacts(paths: Iterable["StrPath"], identity: str):
    for path in paths:
        run(["gpg", "--local-user", identity, "--armor", "--detach-sign", path])


@APP.command()
def build(
    *,
    backend: BuildBackend = BuildBackend.GENERIC,
    sign: bool = typer.Option(False, "-s", "--sign"),
    identity: Optional[str] = typer.Option(None, "-i", "--identity"),
    isolated: bool = typer.Option(
        False, "--isolated", help="Whether to build in an isolated directory"
    ),
    args: List[str] = typer.Option([], "-A", "--arg"),
) -> None:
    ensure_clean()

    if Path("dist").is_dir():
        msg("Removing dist/")
        shutil.rmtree("dist/", True)

    if sign and not identity:
        identity = git(["config", "user.email"], capture_output=True).stdout.strip()

    build_command = (*BUILD_COMMANDS[backend], *args)
    _ctx = isolated_src() if isolated else contextlib.nullcontext()
    with _ctx as old:
        run(build_command)
        artifacts = list(Path("dist").iterdir())
        if len(artifacts) != 2:
            raise RuntimeError(f"Expected two artifacts. Found {len(artifacts)}.")
        if sign or identity:
            assert identity  # appease mypy
            sign_artifacts(artifacts, identity)
        if old is not None:
            shutil.copytree("dist/", old / "dist")

    for path in Path("dist").iterdir():
        CONSOLE.print(f"[blue]Output:[/blue] {path}")

    run(["twine", "check", "--strict", *artifacts])


@APP.command()
def upload(
    *,
    args: List[str] = typer.Option([], "-A", "--arg"),
):
    """
    Upload Python distributions to PyPI
    """
    dist = Path("dist")
    artifacts: list[Path] = []
    for patt in "*.tar.gz", "*.whl":
        matches = list(dist.glob(patt))
        if len(matches) != 1:
            err("Did not find expected wheel and sdist")
            raise typer.Exit(1)
        artifacts.append(matches[0])
    for artifact in artifacts:
        CONSOLE.print(f"[blue]Found artifact:[/blue] {artifact}")

    run(["twine", "upload", *args, *artifacts])


_SOURCE_ENUM: TypeAlias = TyperChoices(  # type: ignore
    "_SOURCE_ENUM",
    list(VERSION_SOURCES),
)

_SOURCE_OPTION = typer.Option(..., "-s", "--source")


@APP.command()
def get_version(
    *, context: typer.Context, source: _SOURCE_ENUM = _SOURCE_OPTION
) -> None:
    """
    Get package's current version
    """
    cli_ctx = context.ensure_object(CLIContext)
    handler: VersionHandler = VERSION_SOURCES[source.value](
        cli_ctx.project_name, cli_ctx.tool_config
    )
    print(handler.get_version())


@APP.command()
def set_version(
    *,
    context: typer.Context,
    version: str = typer.Argument(...),
    source: _SOURCE_ENUM = _SOURCE_OPTION,
) -> None:
    """
    Set package version
    """
    cli_ctx = context.ensure_object(CLIContext)
    handler: VersionHandler = VERSION_SOURCES[source.value](
        cli_ctx.project_name, cli_ctx.tool_config
    )
    handler.set_version(version)
    print(handler.get_version())


@APP.command()
def post_version(*, context: typer.Context, source: _SOURCE_ENUM = _SOURCE_OPTION):
    """
    Shortcut to bump version to `{CURRENT_VERSION}.post0`
    """
    cli_ctx = context.ensure_object(CLIContext)
    handler: VersionHandler = VERSION_SOURCES[source.value](
        cli_ctx.project_name, cli_ctx.tool_config
    )
    print(handler.post_version())


# @APP.command()
# def copr_release(context: typer.Context):
#     cli_ctx = context.ensure_object(CLIContext)
#     config = cli_ctx.tool_config
#     specfile: str | None = config.get(
#         "specfile-path", next(iglob(f"*{cli_ctx.project_name}.spec"), None)
#     )
#     if not specfile:
#         err("Failed to determine specfile path!")
#         raise typer.Exit(1)


def rev_parse(key: str) -> str:
    return git(["rev-parse", key], capture_output=True).stdout.strip()


@APP.command()
def copr_webhook(
    *,
    url_file: Path,
    skip_if_missing: bool = False,
    branch: Annotated[Optional[List[str]], typer.Option("-b", "--branch")] = None,
):
    """
    Trigger a Copr package webhook.
    """
    url: str
    if url_file == Path("-"):
        url = sys.stdin.readline().strip()
    else:
        try:
            url = url_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            message = f"{url_file} does not exist!"
            if skip_if_missing:
                msg(message + " Skipping.")
                raise typer.Exit() from None
            else:
                err(message)
                raise typer.Exit(1) from None
    if branch:
        refs = [rev_parse(r) for r in branch]
        head = rev_parse("HEAD")
        if head not in refs:
            msg(f"This hook only runs on {branch}. Skipping.")
            raise typer.Exit()
    req = httpx.post(url, json={})
    try:
        req.raise_for_status()
    except httpx.HTTPStatusError:
        err(f"Failed to trigger webhook: {req.status_code} - {req.reason_phrase}")
        raise typer.Exit(1) from None


@APP.command(name="scd2md")
def scd2md(
    files: List[Path] = typer.Argument(
        ..., file_okay=True, dir_okay=False, exists=True
    ),
    output_dir: Optional[Path] = typer.Option(
        None, file_okay=False, dir_okay=True, exists=True
    ),
) -> None:
    """
    Long, terrible pipeline to convert scd to markdown
    """
    scd.scd2md(files, output_dir, True)


@APP.command()
def check_remote(
    remote: str = typer.Option("origin", "-r", "--remote"),
    branch: str = typer.Option("main", "-b", "--branch"),
    allow_untracked: bool = typer.Option(False),
    fetch: bool = typer.Option(True),
):
    if not allow_untracked:
        ensure_clean()
    br = "/".join((remote, branch))
    if fetch:
        run(["git", "fetch", remote, branch])
    head_hash: str = run(
        ["git", "show", "-q", "--format=%H", "HEAD"], capture_output=True
    ).stdout.strip()
    upstream_hash: str = run(
        ["git", "show", "-q", "--format=%H", br], capture_output=True
    ).stdout.strip()
    if head_hash != upstream_hash:
        err(f"{head_hash} does not match {br}")


def version_cb(value: bool):
    if value:
        from . import __version__

        print(__version__)
        raise typer.Exit(0)


@APP.callback()
def cb(
    context: typer.Context,
    name: Optional[str] = typer.Option(
        None, help="Override the autodetected project name"
    ),
    _: Optional[bool] = typer.Option(None, "--version", callback=version_cb),
):
    data: MutableMapping[str, Any] = {}
    with contextlib.suppress(OSError):  # noqa: SIM117
        with open("pyproject.toml", "rb") as fp:
            data = load_toml(fp)
    tool_config: MutableMapping[str, Any] = data.get("tool", {}).get("releaserr", {})
    project_config: MutableMapping[str, Any] = data.get("project", {})

    if not name:
        if "name" in project_config:
            name = project_config["name"]
        else:
            name = Path.cwd().name

    context.obj = CLIContext(
        cast(str, name),
        dict(project_config),
        dict(tool_config),
        ReleaserrConfig.read_config(),
    )


def main() -> int:
    try:
        APP()
    except subprocess.CalledProcessError as exc:
        err(exc)
        return exc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
