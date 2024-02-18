# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
from pathlib import Path

import nox

LINT_FILES = ("releaserr/", "noxfile.py")
LINT_SESSIONS = ("formatters", "codeqa", "typing")
nox.options.sessions = (*LINT_SESSIONS, "integration")


@nox.session
def codeqa(session: nox.Session) -> None:
    session.install(".[codeqa]")
    session.run("ruff", *session.posargs, *LINT_FILES)
    session.run("reuse", "lint")


@nox.session
def formatters(session: nox.Session) -> None:
    session.install(".[formatters]")
    session.run("black", *session.posargs, *LINT_FILES)
    session.run("isort", *session.posargs, *LINT_FILES)


@nox.session
def typing(session: nox.Session) -> None:
    session.install("-e", ".[typing]")
    session.run("mypy", *session.posargs, *LINT_FILES)


@nox.session
def lint(session: nox.Session) -> None:
    for target in LINT_SESSIONS:
        session.notify(target)


@nox.session
def integration(session: nox.Session) -> None:
    session.install(".", "nox", "reuse")

    tmp = session.create_tmp()
    project = Path(tmp, "testproj").resolve()
    session.run("rm", "-rf", str(project), external=True)
    with session.chdir(tmp):
        session.run(
            "releaserr", "new", "files", str(project), "--description=test project"
        )
    with session.chdir(project):
        session.run("nox", *session.posargs, env={"CI": "1"})


@nox.session
def publish(session: nox.Session) -> None:
    """
    Publish the current git snapshot to PyPI
    """
    session.install(".", "build", "twine")
    session.run("releaserr", "check-remote")
    isolated = [] if "BUILD_SUBMITTER" in os.environ else ["--isolated"]
    session.run("releaserr", "build", *isolated)
    session.run("releaserr", "upload")
