# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Generate project files and create repositories
"""

import asyncio
import readline  # noqa: F401
from pathlib import Path
from typing import List, Optional

import typer
from rich.prompt import Confirm
from rich.rule import Rule
from rich.table import Table
from sourcehut.client import SrhtClient
from typing_extensions import Annotated

from releaserr.cli_utils import CONSOLE, CLIContext, Exit, TyperChoices, err
from releaserr.copr import DEFAULT_CHROOTS, get_copr_client
from releaserr.new.files import (
    BUILD_BACKENDS,
    SPECFILE_TEMPLATES,
    FilesConfig,
    write_files,
)
from releaserr.new.sourcehut import VISIBILITY as Visibility
from releaserr.new.sourcehut import SourcehutProjectMaker


def _guess_license(cli_ctx: CLIContext) -> str:
    project_license = cli_ctx.project_config.get("license")
    # fmt: off
    if (
        isinstance(project_license, dict)
        and isinstance((text := project_license.get("text")), str)
    ):
    # fmt: on
        return text
    elif isinstance(project_license, str):
        return project_license
    return cli_ctx.global_config.default_license


APP = typer.Typer(help=__doc__)


@APP.command()
def files(
    *,
    context: typer.Context,
    path: Annotated[Optional[Path], typer.Argument()] = None,
    name: Annotated[
        Optional[str],
        typer.Option(
            help="Provide name explicitly instead of guessing based on"
            " [PATH]'s basename"
        ),
    ] = None,
    backend: BUILD_BACKENDS = BUILD_BACKENDS.HATCHLING,
    license_id: Annotated[Optional[str], typer.Option("--license")] = None,
    description: Optional[str] = None,
    specfile: Optional[SPECFILE_TEMPLATES] = None,
    matches: Annotated[Optional[List[str]], typer.Option("-m", "--match")] = None,
):
    """
    Generate project files for a Python project
    """
    cli_ctx = context.ensure_object(CLIContext)
    if license_id is None:
        license_id = _guess_license(cli_ctx)
    if path and path != Path("."):
        path.mkdir()
    else:
        description = cli_ctx.project_config.get("description")
        path = Path.cwd()
    if description is None:
        description = input("description: ")
    name = name or path.name
    config = FilesConfig(name, description, path, backend, license_id, specfile)
    write_files(config, matches or ("*",))


class SourcehutResources(TyperChoices):
    GIT = "git"
    LIST = "list"
    TODO = "todo"


@APP.command(name="sourcehut")
def sourcehut_cmd(
    *,
    context: typer.Context,
    description: Optional[str] = None,
    visibility: Visibility = Visibility.PUBLIC,
    dry_run: Annotated[bool, typer.Option("-n", "--dry-run")] = False,
    assume_yes: Annotated[bool, typer.Option("-y", "--assume-yes")] = False,
    resources: Annotated[
        Optional[List[SourcehutResources]],
        typer.Argument(help="[default: all]", show_default=False),
    ] = None,
):
    """
    Create a Sourcehut git repository, mailing list, and tracker
    """

    resources = resources or list(SourcehutResources)
    if dry_run and assume_yes:
        err("Mutually exclusive: --dry-run and --assume-yes")
        raise Exit()

    cli_ctx = context.ensure_object(CLIContext)
    description = (
        description
        if description is not None
        else cli_ctx.project_config.get("description")
    )

    table = Table(show_header=False, title="Input", border_style="red")
    table.add_row("Name", cli_ctx.project_name)
    table.add_row("Description", description)
    table.add_row("Visibility", visibility)
    CONSOLE.print(table, justify="center")

    if (
        not dry_run
        and not assume_yes
        and not Confirm.ask("Create projects?", default=True)
    ):
        err("Aborted.")
        raise Exit(1)

    async def inner() -> None:
        async with SrhtClient.from_config(cli_ctx.global_config.sourcehut) as client:
            project_maker = SourcehutProjectMaker(
                client, cli_ctx.project_name, visibility, description
            )

            CONSOLE.print(Rule(style="blue"))
            protocol = client.protocol
            baseurl = client.baseurl
            table = Table(
                title="Created projects", show_header=False, border_style="green"
            )

            for resource in resources:
                if not dry_run:
                    await getattr(project_maker, f"create_{resource.value}")()
                table.add_row(
                    resource.name.title(),
                    f"{protocol}{resource.value}.{baseurl}/~gotmax23/{cli_ctx.project_name}",
                )
            CONSOLE.print(table, justify="center")
            CONSOLE.print(
                f"To create a new project: {baseurl}/projects/create",
                justify="center",
            )

    asyncio.run(inner())


@APP.command()
def coprs(
    *,
    context: typer.Context,
    chroots: Annotated[
        Optional[List[str]],
        typer.Option(
            "-c", "--chroot", show_default=False, help=f"[default: {DEFAULT_CHROOTS}]"
        ),
    ] = None,
    description: Optional[str] = None,
    specfile: SPECFILE_TEMPLATES = SPECFILE_TEMPLATES.APP,
):
    """
    Create a Copr release and Copr dev Copr for a project
    """

    cli_ctx = context.ensure_object(CLIContext)

    client = get_copr_client()

    baseurl = cli_ctx.global_config.sourcehut.baseurl
    protocol = cli_ctx.global_config.sourcehut.protocol
    for project in (cli_ctx.project_name, cli_ctx.project_name + "-dev"):
        client.project_proxy.add(
            "gotmax23",
            project,
            chroots=chroots or cli_ctx.global_config.copr.default_chroots,
            homepage=f"{protocol}{baseurl}/~gotmax23/{cli_ctx.project_name}",
            contact=f"~gotmax23/{cli_ctx.project_name}@lists.{baseurl}",
            description=description,
        )
    client.package_proxy.add(
        "gotmax23",
        cli_ctx.project_name + "-dev",
        packagename=specfile.package_name(cli_ctx.project_name),
        source_type="scm",
        source_dict={
            "clone_url": f"{protocol}git.{baseurl}/~gotmax23/{cli_ctx.project_name}",
            "scm_type": "git",
            "commitish": "main",
            "source_build_method": "make_srpm",
        },
    )
