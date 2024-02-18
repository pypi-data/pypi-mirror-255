# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Generate project files for a Python project
"""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from pydantic.dataclasses import dataclass as pdataclass

from releaserr.cli_utils import TyperChoices, msg
from releaserr.subprocess_util import run

DT = datetime.datetime
UTC = datetime.timezone.utc
FILES: dict[Path, str] = {
    Path(".builds/main.yml"): "builds-main.yml.j2",
    Path(".builds/mockbuild.yml"): "builds-mockbuild.yml.j2",
    Path(".builds/mockbuild-f37.yml"): "builds-mockbuild.yml.j2",
    Path(".builds/mockbuild-epel9.yml"): "builds-mockbuild.yml.j2",
    Path(".copr/Makefile"): "copr-Makefile.j2",
    Path(".gitignore"): "gitignore.j2",
    Path("CONTRIBUTING.md"): "CONTRIBUTING.md.j2",
    Path("FRAG.md"): "FRAG.md.j2",
    Path("NEWS.md"): "NEWS.md.j2",
    Path("README.md"): "README.md.j2",
    Path("ruff.toml"): "ruff.toml.j2",
    Path("pyproject.toml"): "pyproject.toml.j2",
    Path("noxfile.py"): "noxfile.py.j2",
    Path("tests/__init__.py"): "blankmod.py.j2",
}
FILE_SETTINGS: dict[Path, dict[str, Any]] = {
    Path(".builds/mockbuild.yml"): {
        "chroot": "fedora-rawhide-x86_64",
        "shortname": "rawhide",
    },
    Path(".builds/mockbuild-f37.yml"): {
        "chroot": "fedora-37-x86_64",
        "shortname": "f37",
    },
    Path(".builds/mockbuild-epel9.yml"): {
        "chroot": "alma+epel-9-x86_64",
        "shortname": "epel9",
    },
}

DEFAULT_SPECFILE_LICENSE = "MIT"


class BUILD_BACKENDS(TyperChoices):
    FLIT_CORE = "flit_core"
    HATCHLING = "hatchling"


class SPECFILE_TEMPLATES(TyperChoices):
    LIBRARY = "library"
    APP = "app"

    def package_name(self, name: str) -> str:
        if self == SPECFILE_TEMPLATES.LIBRARY:
            name = f"python-{name}"
        return name


@pdataclass
class FilesConfig:
    name: str
    description: str
    path: Path
    build_backend: BUILD_BACKENDS
    license_id: str
    specfile_template: Optional[SPECFILE_TEMPLATES]


def get_license_headers(config: FilesConfig, dt: DT) -> list[str]:
    # REUSE-IgnoreStart
    return [
        f"Copyright (C) {dt.year} Maxwell G <maxwell@gtmx.me>",
        f"SPDX-License-Identifier: {config.license_id}",
    ]
    # REUSE-IgnoreEnd


def write_template(
    env: Environment,
    template: str,
    destpath: Path,
    output: Path,
    members: dict[str, Any],
    matches: Sequence[str] = ("*",),
) -> None:
    if any(fnmatch(str(output), pat) for pat in matches):
        msg(f"Writing {output}!")
    else:
        msg(f"Skipping {output}!", style="red")
        return
    rendered = env.get_template(template).render(
        members | FILE_SETTINGS.get(output, {})
    )
    dest = destpath / output
    if len(output.parts) > 1:
        dest.parent.mkdir(parents=len(output.parts) > 2, exist_ok=True)
    dest.write_text(rendered)


def download_license(license_id: str, destdir: Path) -> None:
    dest = destdir / "LICENSES" / f"{license_id}.txt"
    if dest.exists():
        return
    dest.parent.mkdir(exist_ok=True)
    run(["reuse", "download", "-o", dest, license_id])


def symlink_license(license_id: str, destdir: Path) -> None:
    src = Path("LICENSES", f"{license_id}.txt")
    dest = destdir / "LICENSE"
    dest.unlink(True)
    dest.symlink_to(src)


def write_files(config: FilesConfig, matches: Sequence[str] = ("*",)):
    files = FILES.copy()
    files[Path("src", config.name, "__init__.py")] = "init.py.j2"
    files[Path("src", config.name, "py.typed")] = "empty.j2"
    files[Path("tests", f"test_{config.name.replace('-', '_')}.py")] = (
        "test-placeholder.py.j2"
    )

    now = DT.now(UTC)
    jinja2_env = Environment(
        loader=PackageLoader("releaserr.new", "data"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        undefined=StrictUndefined,
    )
    kwargs = {
        "config": config,
        "license_headers": get_license_headers(config, now),
        "year": now.year,
    }

    for output, template in files.items():
        write_template(jinja2_env, template, config.path, output, kwargs, matches)

    specdate = now.strftime("%a %b %d %Y")
    speckwargs = kwargs | {
        "specdate": specdate,
        "speclicense": DEFAULT_SPECFILE_LICENSE,
    }
    if config.specfile_template == SPECFILE_TEMPLATES.APP:
        write_template(
            jinja2_env,
            "app.spec.j2",
            config.path,
            Path(f"{config.name}.spec"),
            speckwargs,
            matches,
        )
    elif config.specfile_template == SPECFILE_TEMPLATES.LIBRARY:
        write_template(
            jinja2_env,
            "library.spec.j2",
            config.path,
            Path(f"python-{config.name}.spec"),
            speckwargs,
            matches,
        )

    if config.specfile_template:
        # Specfiles are always licensed under MIT
        download_license("MIT", config.path)
    else:
        download_license(config.license_id, config.path)

    if config.build_backend == BUILD_BACKENDS.FLIT_CORE:
        symlink_license(config.license_id, config.path)
