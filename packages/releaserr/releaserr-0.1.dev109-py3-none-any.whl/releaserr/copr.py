# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Interact with Fedora Copr
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from copr.v3 import Client

DEFAULT_CHROOTS = (
    "epel-9-x86_64",
    "fedora-37-x86_64",
    "fedora-38-x86_64",
    "fedora-39-x86_64",
    "fedora-rawhide-x86_64",
)


class CoprConfig(BaseModel):
    default_chroots: Sequence[str] = DEFAULT_CHROOTS


def get_copr_client() -> Client:
    from copr.v3 import Client

    return Client.create_from_config_file()
